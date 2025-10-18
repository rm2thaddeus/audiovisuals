use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader};
use std::process::{Child, Command, Stdio};
use std::thread;
use tauri::{Emitter, Window};

/// Progress update emitted from Python stdout.
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct ProgressEvent {
    pub progress: f32,
    pub message: String,
}

/// Minimal wrapper around a spawned Python child process.
pub struct PythonProcess {
    child: Option<Child>,
    window: Window,
}

impl PythonProcess {
    pub fn new(window: Window) -> Self {
        Self {
            child: None,
            window,
        }
    }

    /// Spawn `python` with the supplied script/command and arguments.
    pub fn spawn(&mut self, script_or_flag: &str, args: Vec<&str>) -> Result<(), String> {
        let mut command = Command::new("python");
        command
            .arg(script_or_flag)
            .args(args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());

        let mut child = command
            .spawn()
            .map_err(|err| format!("Failed to spawn Python process: {err}"))?;

        if let Some(stdout) = child.stdout.take() {
            let window = self.window.clone();
            thread::spawn(move || {
                let reader = BufReader::new(stdout);
                for line in reader.lines().flatten() {
                    if let Some(progress) = parse_progress_line(&line) {
                        let _ = window.emit(
                            "python-progress",
                            ProgressEvent {
                                progress,
                                message: line.clone(),
                            },
                        );
                    } else {
                        let _ = window.emit("python-output", line.clone());
                    }
                }
            });
        }

        if let Some(stderr) = child.stderr.take() {
            let window = self.window.clone();
            thread::spawn(move || {
                let reader = BufReader::new(stderr);
                for line in reader.lines().flatten() {
                    let _ = window.emit("python-error", line);
                }
            });
        }

        self.child = Some(child);
        Ok(())
    }

    /// Wait for the child to exit and return the OS status code.
    pub fn wait(&mut self) -> Result<i32, String> {
        if let Some(mut child) = self.child.take() {
            let status = child
                .wait()
                .map_err(|err| format!("Failed to wait for process: {err}"))?;
            Ok(status.code().unwrap_or(-1))
        } else {
            Err(String::from("No process running"))
        }
    }

    /// Forcefully terminate the process if it is still running.
    pub fn kill(&mut self) -> Result<(), String> {
        if let Some(mut child) = self.child.take() {
            child
                .kill()
                .map_err(|err| format!("Failed to kill process: {err}"))?;
        }
        Ok(())
    }
}

/// Attempt to parse a percentage from free-form output text.
fn parse_progress_line(line: &str) -> Option<f32> {
    line.find('%').and_then(|percent_index| {
        let number_str = line[..percent_index]
            .split_whitespace()
            .last()
            .unwrap_or("")
            .trim_start_matches(['[', '(']);
        number_str.parse::<f32>().ok()
    })
}

#[cfg(test)]
mod tests {
    use super::parse_progress_line;

    #[test]
    fn parses_percentages() {
        assert_eq!(parse_progress_line("Progress: 65%"), Some(65.0));
        assert_eq!(parse_progress_line("65% complete"), Some(65.0));
        assert_eq!(parse_progress_line("[45%]"), Some(45.0));
        assert_eq!(parse_progress_line("No progress here"), None);
    }
}
