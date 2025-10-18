use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct StyleInfo {
    pub name: String,
    pub display_name: String,
    pub thumbnail: String,
    pub created: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct StyleDetails {
    pub name: String,
    pub display_name: String,
    pub thumbnail: String,
    pub created: String,
    pub parameters: std::collections::HashMap<String, f32>,
    pub description: Option<String>,
}

/// List all available styles from the styles directory
#[tauri::command]
pub async fn list_styles() -> Result<Vec<StyleInfo>, String> {
    // Check if styles directory exists
    let styles_dir = "styles";
    
    if !Path::new(styles_dir).exists() {
        // Return empty list if styles directory doesn't exist yet
        return Ok(vec![]);
    }

    let mut styles = Vec::new();

    // Read styles directory
    match fs::read_dir(styles_dir) {
        Ok(entries) => {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    if let Some(name) = path.file_name() {
                        if let Some(name_str) = name.to_str() {
                            // TODO: Load actual metadata from style directory
                            styles.push(StyleInfo {
                                name: name_str.to_string(),
                                display_name: name_str
                                    .replace("_", " ")
                                    .split_whitespace()
                                    .map(|w| {
                                        let mut c = w.chars();
                                        match c.next() {
                                            None => String::new(),
                                            Some(f) => {
                                                f.to_uppercase().collect::<String>() + c.as_str()
                                            }
                                        }
                                    })
                                    .collect::<Vec<_>>()
                                    .join(" "),
                                thumbnail: String::new(), // TODO: Generate thumbnails
                                created: chrono::Local::now()
                                    .format("%Y-%m-%d")
                                    .to_string(),
                            });
                        }
                    }
                }
            }
        }
        Err(e) => {
            return Err(format!("Failed to read styles directory: {}", e));
        }
    }

    // Sort by name
    styles.sort_by(|a, b| a.name.cmp(&b.name));

    // Add a default style at the beginning
    let mut result = vec![StyleInfo {
        name: "default".to_string(),
        display_name: "Default".to_string(),
        thumbnail: String::new(),
        created: chrono::Local::now()
            .format("%Y-%m-%d")
            .to_string(),
    }];
    result.extend(styles);

    Ok(result)
}

/// Get detailed information about a specific style
#[tauri::command]
pub async fn get_style_details(name: String) -> Result<StyleDetails, String> {
    if name == "default" {
        return Ok(StyleDetails {
            name: "default".to_string(),
            display_name: "Default".to_string(),
            thumbnail: String::new(),
            created: chrono::Local::now()
                .format("%Y-%m-%d")
                .to_string(),
            parameters: std::collections::HashMap::new(),
            description: Some("Default CPPN configuration".to_string()),
        });
    }

    let style_path = format!("styles/{}", name);
    if !Path::new(&style_path).exists() {
        return Err(format!("Style not found: {}", name));
    }

    // TODO: Load actual metadata from style.json or similar
    Ok(StyleDetails {
        name: name.clone(),
        display_name: name
            .replace("_", " ")
            .split_whitespace()
            .map(|w| {
                let mut c = w.chars();
                match c.next() {
                    None => String::new(),
                    Some(f) => f.to_uppercase().collect::<String>() + c.as_str(),
                }
            })
            .collect::<Vec<_>>()
            .join(" "),
        thumbnail: String::new(),
        created: chrono::Local::now()
            .format("%Y-%m-%d")
            .to_string(),
        parameters: std::collections::HashMap::new(),
        description: None,
    })
}

/// Get thumbnail image for a style
#[tauri::command]
pub async fn get_style_thumbnail(name: String) -> Result<String, String> {
    // TODO: Generate or retrieve thumbnail image
    // For now, return empty string
    Ok(String::new())
}

