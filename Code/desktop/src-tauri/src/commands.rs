use crate::python::PythonProcess;
use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use tauri::{async_runtime, Window};

#[derive(Deserialize)]
pub struct GenerateVideoParams {
    pub audio_path: String,
    pub output_path: String,
    pub resolution: String,
    pub fps: u32,
    pub style_name: Option<String>,
    pub quality: Option<u32>,
    pub layers: Option<u32>,
    pub hidden_dim: Option<u32>,
}

#[derive(Serialize)]
pub struct CommandResult<T = ()> {
    pub success: bool,
    pub message: String,
    pub data: Option<T>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GenerateVideoResult {
    pub video_path: String,
    pub duration: f32,
    pub size: u64,
}

/// Convert Windows paths to proper CLI format
fn normalize_path_for_cli(path: &str) -> String {
    // On Windows, normalize backslashes to forward slashes for CLI compatibility
    #[cfg(target_os = "windows")]
    {
        path.replace('\\', "/")
    }

    #[cfg(not(target_os = "windows"))]
    {
        path.to_string()
    }
}

/// Validate that input file exists and is readable
fn validate_input_file(path: &str) -> Result<(), String> {
    if !Path::new(path).exists() {
        return Err(format!("Input file not found: {}", path));
    }

    // Check if it's a readable file
    match std::fs::metadata(path) {
        Ok(metadata) => {
            if !metadata.is_file() {
                return Err(format!("Input path is not a file: {}", path));
            }
            Ok(())
        }
        Err(e) => Err(format!("Cannot access input file: {}", e)),
    }
}

/// Validate that output directory exists or can be created
fn validate_output_path(path: &str) -> Result<(), String> {
    if let Some(parent) = Path::new(path).parent() {
        if !parent.as_os_str().is_empty() && !parent.exists() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("Cannot create output directory: {}", e))?;
        }
    }
    Ok(())
}

fn resolve_cli_script() -> Result<PathBuf, String> {
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut candidates = vec![manifest_dir
        .join("..")
        .join("..")
        .join("backend")
        .join("cli.py")];

    if let Ok(current_dir) = std::env::current_dir() {
        candidates.push(current_dir.join("..").join("backend").join("cli.py"));
        candidates.push(current_dir.join("backend").join("cli.py"));
    }

    candidates
        .into_iter()
        .find(|path| path.exists())
        .ok_or_else(|| "Unable to locate backend CLI script (cli.py)".to_string())
}

fn find_style_weights(style_name: &str, cli_dir: &Path) -> Option<PathBuf> {
    let base_dir = cli_dir.join("styles");
    if !base_dir.exists() {
        return None;
    }

    let filename = format!("{style_name}.pth");

    let direct_candidate = base_dir.join(&filename);
    if direct_candidate.exists() {
        return Some(direct_candidate);
    }

    if let Ok(entries) = std::fs::read_dir(&base_dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                let candidate = path.join(&filename);
                if candidate.exists() {
                    return Some(candidate);
                }
            }
        }
    }

    None
}

#[tauri::command]
pub async fn generate_video(
    params: GenerateVideoParams,
    window: Window,
) -> Result<CommandResult<GenerateVideoResult>, String> {
    async_runtime::spawn_blocking(move || {
        let GenerateVideoParams {
            audio_path,
            output_path,
            resolution,
            fps,
            style_name,
            quality,
            layers,
            hidden_dim,
        } = params;

        validate_input_file(&audio_path)?;
        validate_output_path(&output_path)?;

        let script_path = resolve_cli_script()?;
        let cli_dir = script_path
            .parent()
            .ok_or_else(|| "Invalid CLI script path".to_string())?;
        let audio_path_cli = normalize_path_for_cli(&audio_path);
        let output_path_cli = normalize_path_for_cli(&output_path);

        let mut args: Vec<String> = vec![
            audio_path_cli,
            output_path_cli.clone(),
            "--resolution".into(),
            resolution.clone(),
            "--fps".into(),
            fps.to_string(),
        ];

        if let Some(layers) = layers {
            args.push("--layers".into());
            args.push(layers.to_string());
        }

        if let Some(hidden_dim) = hidden_dim {
            args.push("--hidden-dim".into());
            args.push(hidden_dim.to_string());
        }

        if let Some(quality) = quality {
            let audio_scale = (quality as f32) / 100.0;
            args.push("--audio-scale".into());
            args.push(format!("{:.2}", audio_scale));
        }

        if let Some(style_name) = style_name {
            if !style_name.is_empty() && style_name != "default" {
                if let Some(weights_path) = find_style_weights(&style_name, cli_dir) {
                    if let Some(path_str) = weights_path.to_str() {
                        args.push("--load-weights".into());
                        args.push(path_str.replace('\\', "/"));
                    }
                }
            }
        }

        let arg_refs: Vec<&str> = args.iter().map(|s| s.as_str()).collect();

        let script_str = script_path
            .to_str()
            .ok_or_else(|| "Failed to convert CLI script path".to_string())?;

        let mut process = PythonProcess::new(window.clone());
        process
            .spawn(script_str, arg_refs)
            .map_err(|e| format!("Failed to start video generation: {}", e))?;

        let exit_code = process
            .wait()
            .map_err(|e| format!("Process failed: {}", e))?;

        if exit_code != 0 {
            return Err(format!(
                "Video generation failed with exit code {}",
                exit_code
            ));
        }

        let output_metadata = std::fs::metadata(&output_path)
            .map_err(|e| format!("Failed to get output file info: {}", e))?;

        let size = output_metadata.len();

        let duration = 0.0;

        Ok(CommandResult {
            success: true,
            message: String::from("Video generated successfully"),
            data: Some(GenerateVideoResult {
                video_path: output_path_cli,
                duration,
                size,
            }),
        })
    })
    .await
    .map_err(|err| err.to_string())?
}

#[tauri::command]
pub async fn test_python(window: Window) -> Result<CommandResult, String> {
    async_runtime::spawn_blocking(move || {
        let mut process = PythonProcess::new(window);
        process.spawn("--version", Vec::new())?;
        let exit_code = process.wait()?;

        let success = exit_code == 0;
        Ok(CommandResult {
            success,
            message: format!("Python exited with code {exit_code}"),
            data: None,
        })
    })
    .await
    .map_err(|err| err.to_string())?
}
