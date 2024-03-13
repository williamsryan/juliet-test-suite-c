use clap::Parser;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Instant;
use tokio::process::Command;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Opts {
    /// The directory to scan
    directory: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts: Opts = Opts::parse();

    let paths = fs::read_dir(&opts.directory)?;

    let mut handles = vec![];
    let mut log_file = File::create("run-stats.log")?;

    let mut total = 0;
    let mut failed = 0;

    for path in paths {
        total += 1;
        let path = path?.path();
        if path.extension().and_then(|s| s.to_str()) == Some("js") {
            let path_str = path.to_str().unwrap().to_owned();
            let wasm_path = path.with_extension("wasm");
            let handle = tokio::spawn(async move {
                let start = Instant::now();
                let output = Command::new("node")
                    .arg(&path_str)
                    .output()
                    .await
                    .expect("Failed to execute command");
                let duration = start.elapsed();

                if output.status.success() {
                    let filtered_dir = Path::new("filtered");
                    fs::create_dir_all(&filtered_dir).expect("Failed to create directory");
                    // ...
                    (path_str, duration, true)
                } else {
                    eprintln!("Error running {}: {:?}", path_str, output);
                    (path_str, duration, false)
                }
            });

            handles.push(handle);
        }
    }

    for handle in handles {
        let (path_str, duration, success) = handle.await?;
        if !success {
            failed += 1;
        }
        writeln!(log_file, "{} took {:?}. Success: {}", path_str, duration, success)?;
    }

    writeln!(log_file, "Total: {}. Failed: {}", total, failed)?;

    Ok(())
}