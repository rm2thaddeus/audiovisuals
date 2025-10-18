use crate::python::PythonProcess;
use serde::{Deserialize, Serialize};
use tauri::{async_runtime, Window};
use std::path::Path;

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

#[tauri::command]
pub async fn generate_video(
    params: GenerateVideoParams,
    window: Window,
) -> Result<CommandResult<GenerateVideoResult>, String> {
    async_runtime::spawn_blocking(move || {
        // Validate inputs
        validate_input_file(&params.audio_path)?;
        validate_output_path(&params.output_path)?;
        
        // Normalize paths for Windows compatibility
        let audio_path = normalize_path_for_cli(&params.audio_path);
        let output_path = normalize_path_for_cli(&params.output_path);
        
        // Build CLI arguments
        let mut args: Vec<&str> = vec![];
        
        // Positional arguments
        args.push(&audio_path);
        args.push(&output_path);
        
        // Optional arguments based on parameters
        args.push("--resolution");
        args.push(&params.resolution);
        
        args.push("--fps");
        // fps as string since we need to pass it to CLI
        let fps_str = params.fps.to_string();
        args.push(&fps_str);
        
        // Optional: layers
        let layers_str;
        if let Some(layers) = params.layers {
            layers_str = layers.to_string();
            args.push("--layers");
            args.push(&layers_str);
        }
        
        // Optional: hidden dimension
        let hidden_dim_str;
        if let Some(hidden_dim) = params.hidden_dim {
            hidden_dim_str = hidden_dim.to_string();
            args.push("--hidden-dim");
            args.push(&hidden_dim_str);
        }
        
        // Optional: quality/audio scale (map 0-100 quality to 0.0-1.0 scale)
        let audio_scale_str;
        if let Some(quality) = params.quality {
            let audio_scale = (quality as f32) / 100.0;
            audio_scale_str = format!("{:.2}", audio_scale);
            args.push("--audio-scale");
            args.push(&audio_scale_str);
        }
        
        // Convert String args to &str for the process
        let args_str: Vec<&str> = args.iter().map(|s| *s).collect();
        
        // Spawn the Python process
        let mut process = PythonProcess::new(window.clone());
        process.spawn("Code/backend/cli.py", args_str)
            .map_err(|e| format!("Failed to start video generation: {}", e))?;
        
        // Wait for process to complete
        let exit_code = process.wait()
            .map_err(|e| format!("Process failed: {}", e))?;
        
        if exit_code != 0 {
            return Err(format!("Video generation failed with exit code {}", exit_code));
        }
        
        // Get output file info
        let output_metadata = std::fs::metadata(&output_path)
            .map_err(|e| format!("Failed to get output file info: {}", e))?;
        
        let size = output_metadata.len();
        
        // Try to estimate duration (would need proper video parsing in production)
        // For now, use a placeholder calculation
        let duration = 0.0; // This would be parsed from video metadata in production
        
        Ok(CommandResult {
            success: true,
            message: String::from("Video generated successfully"),
            data: Some(GenerateVideoResult {
                video_path: output_path,
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
