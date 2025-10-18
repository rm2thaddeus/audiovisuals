use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize, Debug)]
pub struct FileValidationResult {
    pub valid: bool,
    pub error: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct AudioFileMetadata {
    pub path: String,
    pub duration: f32,
    pub bitrate: u32,
    pub sample_rate: u32,
}

const SUPPORTED_FORMATS: &[&str] = &["mp3", "wav", "flac", "aiff", "m4a"];
const MAX_FILE_SIZE: u64 = 500 * 1024 * 1024; // 500MB

/// Validate that an audio file exists and has a supported format
#[tauri::command]
pub async fn validate_audio_file(path: String) -> Result<FileValidationResult, String> {
    // Check if file exists
    if !Path::new(&path).exists() {
        return Ok(FileValidationResult {
            valid: false,
            error: Some("File does not exist".to_string()),
        });
    }

    // Get file extension
    let extension = Path::new(&path)
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    // Check if format is supported
    if !SUPPORTED_FORMATS.contains(&extension.as_str()) {
        return Ok(FileValidationResult {
            valid: false,
            error: Some(format!(
                "Unsupported format. Supported: {:?}",
                SUPPORTED_FORMATS
            )),
        });
    }

    // Check file size
    match fs::metadata(&path) {
        Ok(metadata) => {
            if metadata.len() > MAX_FILE_SIZE {
                return Ok(FileValidationResult {
                    valid: false,
                    error: Some(format!(
                        "File too large. Maximum: {} MB",
                        MAX_FILE_SIZE / 1024 / 1024
                    )),
                });
            }
        }
        Err(e) => {
            return Ok(FileValidationResult {
                valid: false,
                error: Some(format!("Cannot read file: {}", e)),
            });
        }
    }

    Ok(FileValidationResult {
        valid: true,
        error: None,
    })
}

/// Get detailed metadata about an audio file using Python backend
#[tauri::command]
pub async fn get_file_metadata(path: String) -> Result<AudioFileMetadata, String> {
    // This would call the Python CLI to extract metadata
    // For now, return placeholder values
    // TODO: Implement actual metadata extraction via Python CLI
    
    if !Path::new(&path).exists() {
        return Err("File not found".to_string());
    }

    // Placeholder implementation
    Ok(AudioFileMetadata {
        path: path.clone(),
        duration: 0.0,
        bitrate: 0,
        sample_rate: 44100,
    })
}

/// Get audio duration from file
#[tauri::command]
pub async fn get_audio_duration(path: String) -> Result<f32, String> {
    if !Path::new(&path).exists() {
        return Err("File not found".to_string());
    }

    // TODO: Implement actual duration extraction via Python CLI or ffprobe
    Ok(0.0)
}

