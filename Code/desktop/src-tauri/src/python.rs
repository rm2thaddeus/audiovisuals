// NOTE: This file handles Windows Python process spawning. All paths use backslash (\) or forward slash (/)
// Both work in Rust on Windows. Paths are provided by Tauri's sandboxed file system.

use std::process::{Command, Stdio, Child, ChildStdout, ChildStderr};
use std::io::{BufRead, BufReader};
use std::sync::{Arc, Mutex};
use std::thread;
use tauri::Window;
use serde::{Serialize, Deserialize};

/// Progress event emitted during Python process execution
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct ProgressEvent {
    pub progress: f32,
    pub message: String,
}

/// Represents a running Python process
pub struct PythonProcess {
    child: Option<Child>,
    window: Window,
}

impl PythonProcess {
    /// Create a new Python process manager
    pub fn new(window: Window) -> Self {
        Self { child: None, window }
    }

    /// Spawn a Python process with the given script and arguments
    /// 
    /// NOTE: On Windows, use "python" directly (not /usr/bin/python - that doesn't exist)
    /// Paths can use either backslash or forward slash
    pub fn spawn(
        &mut self,
        script: &str,
        args: Vec<&str>,
    ) -> Result<(), String> {
        // ✅ CORRECT: On Windows, "python" resolves from PATH
        // Command { python } → C:\Users\...\Python312\python.exe (automatically resolved)
        let mut cmd = Command::new("python");
        cmd.arg(script)
            .args(args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        match cmd.spawn() {
            Ok(mut child) => {
                // Spawn thread to read stdout
                if let Some(stdout) = child.stdout.take() {
                    let window = self.window.clone();
                    thread::spawn(move || {
                        let reader = BufReader::new(stdout);
                        for line in reader.lines() {
                            if let Ok(line) = line {
                                // Emit progress event for each line
                                if let Some(progress) = parse_progress_line(&line) {
                                    let _ = window.emit("python-progress", ProgressEvent {
                                        progress,
                                        message: line.clone(),
                                    });
                                } else {
                                    // Non-progress output
                                    let _ = window.emit("python-output", line);
                                }
                            }
                        }
                    });
                }

                self.child = Some(child);
                Ok(())
            }
            Err(e) => Err(format!("Failed to spawn Python process: {}", e)),
        }
    }

    /// Wait for the process to complete and return the exit code
    pub fn wait(&mut self) -> Result<i32, String> {
        if let Some(mut child) = self.child.take() {
            match child.wait() {
                Ok(status) => Ok(status.code().unwrap_or(-1)),
                Err(e) => Err(format!("Failed to wait for process: {}", e)),
            }
        } else {
            Err("No process running".to_string())
        }
    }

    /// Kill the process immediately
    pub fn kill(&mut self) -> Result<(), String> {
        if let Some(mut child) = self.child.take() {
            child.kill().map_err(|e| format!("Failed to kill process: {}", e))?;
        }
        Ok(())
    }
}

/// Parse progress percentage from output line
/// 
/// Looks for patterns like:
/// - "Progress: 65%"
/// - "[Progress] 45%"
/// - "65% complete"
fn parse_progress_line(line: &str) -> Option<f32> {
    // Look for percentage pattern
    if let Some(pos) = line.find('%') {
        // Find the last number before %
        let before = &line[..pos];
        let num_str = before
            .split_whitespace()
            .last()
            .unwrap_or("")
            .trim_start_matches('[')
            .trim_start_matches('(');
        
        num_str.parse::<f32>().ok()
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_progress() {
        assert_eq!(parse_progress_line("Progress: 65%"), Some(65.0));
        assert_eq!(parse_progress_line("65% complete"), Some(65.0));
        assert_eq!(parse_progress_line("[45%]"), Some(45.0));
        assert_eq!(parse_progress_line("No progress here"), None);
    }
}
