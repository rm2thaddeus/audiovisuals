use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "camelCase")]
pub struct Generation {
    pub id: String,
    pub filename: String,
    pub audio_path: String,
    pub video_path: String,
    pub output_path: String,
    pub settings: GenerationSettings,
    pub created_at: String,
    pub duration: f32,
    pub file_size: u64,
    pub thumbnail: Option<String>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "camelCase")]
pub struct GenerationSettings {
    pub resolution: String,
    pub fps: u32,
    pub quality: u32,
    pub audio_path: String,
    pub style_name: String,
}

const GENERATIONS_FILE: &str = "generations_history.json";
const MAX_STORED: usize = 100;

/// Load recent generations from storage
#[tauri::command]
pub async fn load_recent_generations() -> Result<Vec<Generation>, String> {
    if !Path::new(GENERATIONS_FILE).exists() {
        return Ok(vec![]);
    }

    match fs::read_to_string(GENERATIONS_FILE) {
        Ok(content) => match serde_json::from_str::<Vec<Generation>>(&content) {
            Ok(generations) => Ok(generations),
            Err(e) => Err(format!("Failed to parse generations: {}", e)),
        },
        Err(e) => Err(format!("Failed to read generations file: {}", e)),
    }
}

/// Save a new generation to storage
#[tauri::command]
pub async fn save_generation(mut generation: Generation) -> Result<(), String> {
    // Generate unique ID if not provided
    if generation.id.is_empty() {
        generation.id = uuid::Uuid::new_v4().to_string();
    }

    // Load existing generations
    let mut generations = load_recent_generations().await.unwrap_or_default();

    // Add new generation at the beginning
    generations.insert(0, generation);

    // Keep only the most recent MAX_STORED
    generations.truncate(MAX_STORED);

    // Save to file
    match serde_json::to_string_pretty(&generations) {
        Ok(json) => match fs::write(GENERATIONS_FILE, json) {
            Ok(_) => Ok(()),
            Err(e) => Err(format!("Failed to write generations file: {}", e)),
        },
        Err(e) => Err(format!("Failed to serialize generations: {}", e)),
    }
}

/// Delete a generation from storage
#[tauri::command]
pub async fn delete_generation(id: String) -> Result<(), String> {
    let mut generations = load_recent_generations().await?;

    // Find and remove the generation
    generations.retain(|g| g.id != id);

    // Save back to file
    match serde_json::to_string_pretty(&generations) {
        Ok(json) => match fs::write(GENERATIONS_FILE, json) {
            Ok(_) => Ok(()),
            Err(e) => Err(format!("Failed to write generations file: {}", e)),
        },
        Err(e) => Err(format!("Failed to serialize generations: {}", e)),
    }
}

/// Clear all generations
#[tauri::command]
pub async fn clear_all_generations() -> Result<(), String> {
    match fs::write(GENERATIONS_FILE, "[]") {
        Ok(_) => Ok(()),
        Err(e) => Err(format!("Failed to clear generations: {}", e)),
    }
}
