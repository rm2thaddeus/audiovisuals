use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};
use symphonia::core::errors::Error as SymphoniaError;
use symphonia::core::formats::FormatOptions;
use symphonia::core::io::MediaSourceStream;
use symphonia::core::meta::MetadataOptions;
use symphonia::core::probe::Hint;
use tauri::async_runtime;

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct FileValidationResult {
    pub valid: bool,
    pub error: Option<String>,
    pub canonical_path: Option<String>,
    pub size: Option<u64>,
    pub format: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct AudioFileMetadata {
    pub path: String,
    pub duration: f32,
    pub bitrate: u32,
    pub sample_rate: u32,
    pub channels: u16,
    pub format: String,
    pub file_size: u64,
}

const SUPPORTED_FORMATS: &[&str] = &["mp3", "wav", "flac", "aiff", "m4a"];
const MAX_FILE_SIZE: u64 = 500 * 1024 * 1024; // 500MB

/// Validate that an audio file exists and has a supported format.
#[tauri::command]
pub async fn validate_audio_file(path: String) -> Result<FileValidationResult, String> {
    let input_path = PathBuf::from(&path);

    if !input_path.exists() {
        return Ok(FileValidationResult {
            valid: false,
            error: Some("File does not exist".to_string()),
            canonical_path: None,
            size: None,
            format: None,
        });
    }

    let metadata = fs::metadata(&input_path).map_err(|e| e.to_string())?;

    let extension = input_path
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    if !SUPPORTED_FORMATS.contains(&extension.as_str()) {
        return Ok(FileValidationResult {
            valid: false,
            error: Some(format!(
                "Unsupported format. Supported: {:?}",
                SUPPORTED_FORMATS
            )),
            canonical_path: None,
            size: Some(metadata.len()),
            format: Some(extension),
        });
    }

    if metadata.len() > MAX_FILE_SIZE {
        return Ok(FileValidationResult {
            valid: false,
            error: Some(format!(
                "File too large. Maximum: {} MB",
                MAX_FILE_SIZE / 1024 / 1024
            )),
            canonical_path: None,
            size: Some(metadata.len()),
            format: Some(extension),
        });
    }

    let canonical_path = input_path
        .canonicalize()
        .ok()
        .and_then(|p| normalize_path(&p));

    Ok(FileValidationResult {
        valid: true,
        error: None,
        canonical_path,
        size: Some(metadata.len()),
        format: Some(extension),
    })
}

/// Get detailed metadata about an audio file.
#[tauri::command]
pub async fn get_file_metadata(path: String) -> Result<AudioFileMetadata, String> {
    let path_clone = path.clone();
    async_runtime::spawn_blocking(move || extract_metadata(&path_clone))
        .await
        .map_err(|e| e.to_string())?
}

/// Convenience command to get only the duration.
#[tauri::command]
pub async fn get_audio_duration(path: String) -> Result<f32, String> {
    let path_clone = path.clone();
    async_runtime::spawn_blocking(move || extract_metadata(&path_clone).map(|meta| meta.duration))
        .await
        .map_err(|e| e.to_string())?
}

fn extract_metadata(path: &str) -> Result<AudioFileMetadata, String> {
    let input_path = PathBuf::from(path);
    if !input_path.exists() {
        return Err("File not found".to_string());
    }

    let file_size = fs::metadata(&input_path)
        .map(|m| m.len())
        .map_err(|e| format!("Failed to read metadata: {e}"))?;

    let extension = input_path
        .extension()
        .and_then(|e| e.to_str())
        .map(|ext| ext.to_lowercase())
        .unwrap_or_default();

    let file = std::fs::File::open(&input_path)
        .map_err(|e| format!("Failed to open file: {e}"))?;
    let media_source = MediaSourceStream::new(Box::new(file), Default::default());

    let mut hint = Hint::new();
    if !extension.is_empty() {
        hint.with_extension(&extension);
    }

    let format_opts = FormatOptions::default();
    let metadata_opts = MetadataOptions::default();

    let probed = symphonia::default::get_probe()
        .format(&hint, media_source, &format_opts, &metadata_opts)
        .map_err(|e| format!("Failed to probe audio format: {e}"))?;

    let mut format = probed.format;
    let track = format
        .default_track()
        .ok_or_else(|| "No supported audio tracks found".to_string())?;

    let codec_params = &track.codec_params;
    let sample_rate = codec_params.sample_rate.unwrap_or(0);
    // Use time_base and n_frames for bitrate estimation if available
    let bitrate_kbps: u32 = if let Some(n_frames) = codec_params.n_frames {
        if let Some(_time_base) = codec_params.time_base {
            // Estimate from file size and duration
            let duration_seconds = n_frames as f64 / sample_rate as f64;
            if duration_seconds > 0.0 {
                ((file_size as f64 * 8.0) / (duration_seconds * 1000.0)) as u32
            } else {
                0
            }
        } else {
            0
        }
    } else {
        0
    };
    
    let channels = codec_params
        .channels
        .map(|c| c.count() as u16)
        .unwrap_or(0);

    let mut total_samples = codec_params.n_frames.unwrap_or(0);

    // If we don't have frame count from codec params, try to estimate by reading packets
    if total_samples == 0 {
        loop {
            match format.next_packet() {
                Ok(_packet) => {
                    // Packet doesn't provide duration directly in Symphonia v0.5
                    // Frame counting happens during decoding, not probe phase
                    // For now, just count packets as a rough estimate
                    total_samples = total_samples.saturating_add(1);
                }
                Err(SymphoniaError::IoError(_)) | Err(SymphoniaError::ResetRequired) => break,
                Err(_err) => break, // Stop on other errors
            }
        }
    }

    let duration_seconds = if sample_rate > 0 {
        total_samples as f64 / sample_rate as f64
    } else {
        0.0
    };

    Ok(AudioFileMetadata {
        path: path.to_string(),
        duration: duration_seconds as f32,
        bitrate: bitrate_kbps,
        sample_rate: sample_rate as u32,
        channels,
        format: extension,
        file_size,
    })
}

fn normalize_path(path: &Path) -> Option<String> {
    let raw = path.to_string_lossy().to_string();
    if raw.starts_with(r"\\?\") {
        Some(raw[4..].to_string())
    } else {
        Some(raw)
    }
}
