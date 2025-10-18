pub mod commands;
pub mod python;
pub mod file_manager;
pub mod styles;
pub mod storage;

use commands::{generate_video, test_python};
use file_manager::{validate_audio_file, get_file_metadata, get_audio_duration};
use styles::{list_styles, get_style_details, get_style_thumbnail};
use storage::{load_recent_generations, save_generation, delete_generation, clear_all_generations};

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

