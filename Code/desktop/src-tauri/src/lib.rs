pub mod commands;
pub mod file_manager;
pub mod python;
pub mod storage;
pub mod styles;

use commands::{generate_video, test_python};
use file_manager::{get_audio_duration, get_file_metadata, validate_audio_file};
use storage::{clear_all_generations, delete_generation, load_recent_generations, save_generation};
use styles::{get_style_details, get_style_thumbnail, list_styles};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            generate_video,
            test_python,
            validate_audio_file,
            get_file_metadata,
            get_audio_duration,
            list_styles,
            get_style_details,
            get_style_thumbnail,
            load_recent_generations,
            save_generation,
            delete_generation,
            clear_all_generations
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
