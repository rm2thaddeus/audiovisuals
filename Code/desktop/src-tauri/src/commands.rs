use crate::python::PythonProcess;
use serde::{Deserialize, Serialize};
use tauri::{async_runtime, Window};

#[derive(Deserialize)]
pub struct GenerateVideoParams {
    pub audio_path: String,
    pub output_path: String,
    pub resolution: String,
    pub fps: u32,
}

#[derive(Serialize)]
pub struct CommandResult<T = ()> {
    pub success: bool,
    pub message: String,
    pub data: Option<T>,
}

#[tauri::command]
pub async fn generate_video(
    _params: GenerateVideoParams,
    _window: Window,
) -> Result<CommandResult, String> {
    Ok(CommandResult {
        success: false,
        message: String::from("Feature coming in Week 3-4"),
        data: None,
    })
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
