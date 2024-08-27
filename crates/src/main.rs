use clap::Parser;
use std::fs::{self, File};
use std::io::Write;
use std::path::Path;
use std::time::Instant;
use tokio::process::Command;

use tokio::sync::Semaphore;
use std::sync::Arc;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Opts {
    /// The directory to scan
    #[arg(value_name = "input.dir")]
    directory: String,
    /// The number of files to sample
    #[arg(short = 's', long = "sample")]
    sample: Option<usize>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let opts: Opts = Opts::parse();

    // let paths = fs::read_dir(&opts.directory)?;
    let paths: Vec<_> = fs::read_dir(&opts.directory)?
        .filter_map(Result::ok)
        .filter(|entry| entry.path().extension().and_then(|s| s.to_str()) == Some("js"))
        .collect();

    let mut handles = vec![];
    let mut log_file = File::create("run-stats.log")?;

    let mut total = 0;
    let mut failed = 0;

    // Set the limit for the number of concurrent tasks
    let semaphore = Arc::new(Semaphore::new(100));

    let output_dir = Path::new("run-stats");
    if let Err(e) = fs::create_dir_all(&output_dir) {
        eprintln!("Failed to create directory: {}", e);
    }

    for path in paths.into_iter().take(opts.sample.unwrap_or(usize::MAX)) {
        total += 1;
        let path = path.path();
        let path_str = path.to_str().unwrap().to_owned();
        // let wasm_path = path.with_extension("wasm");
        let semaphore = Arc::clone(&semaphore);

        let handle = tokio::spawn(async move {
            let permit = semaphore.acquire().await.unwrap();
            let start = Instant::now();
            let output = Command::new("node")
                .arg(&path_str)
                .output()
                .await
                .expect("Failed to execute command");

            // Release the permit when the task is done
            drop(permit);

            let duration = start.elapsed();

            if output.status.success() {
                println!(
                    "{} took {:?}. Success: {}",
                    path_str,
                    duration,
                    output.status.success()
                );
                // let filtered_dir = Path::new("filtered");
                // fs::create_dir_all(&filtered_dir).expect("Failed to create directory");
                // let new_js_path = filtered_dir.join(Path::new(&path_str).file_name().unwrap());
                // let new_wasm_path = filtered_dir.join(wasm_path.file_name().unwrap());
                // fs::copy(&path_str, &new_js_path).expect("Failed to copy JS file");
                // fs::copy(&wasm_path, &new_wasm_path).expect("Failed to copy Wasm file");
                (path_str, duration, true)
            } else {
                eprintln!("Error running {}: {:?}", path_str, output);
                (path_str, duration, false)
            }
        });

        handles.push(handle);
    }

    for handle in handles {
        let (path_str, duration, success) = handle.await?;
        if !success {
            failed += 1;
        }
        let filename = Path::new(&path_str).file_name().unwrap().to_str().unwrap();
        writeln!(
            log_file,
            "{} took {:?}. Success: {}",
            filename, duration, success
        )?;
    }

    writeln!(
        log_file,
        "\n==================== Statistics ===================="
    )?;
    writeln!(log_file, "Total: {}. Failed: {}", total, failed)?;

    println!("\n==================== Statistics ====================");
    println!("Total: {}. Failed: {}", total, failed);

    Ok(())
}
