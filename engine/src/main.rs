use clap::Parser;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::Read;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(name = "titan", version, about = "TitanDefender Engine")]
struct Cli {
    #[command(subcommand)]
    cmd: Commands,
}

#[derive(clap::Subcommand, Debug)]
enum Commands {
    Scan { path: String, #[arg(short, long)] quick: bool },
    Quarantine { path: String },
    ListSigs,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Signature {
    hash: String,
    name: String,
    severity: u8,
}

#[derive(Serialize, Deserialize, Debug)]
struct SigDb {
    signatures: Vec<Signature>,
}

#[derive(Serialize, Deserialize, Debug)]
struct ScanHit {
    path: String,
    hash: String,
    threat: String,
    severity: u8,
}

fn sha256_file(path: &Path) -> Option<String> {
    let mut f = fs::File::open(path).ok()?;
    let mut buf = Vec::new();
    f.read_to_end(&mut buf).ok()?;
    let mut h = Sha256::new();
    h.update(&buf);
    Some(format!("{:x}", h.finalize()))
}

fn load_sigs() -> SigDb {
    // embedded minimal db
    SigDb {
        signatures: vec![
            Signature { hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855".into(), name: "EmptyFile (test)".into(), severity: 1 },
        ],
    }
}

fn scan_path(root: &Path, quick: bool) -> Vec<ScanHit> {
    let sigs = load_sigs();
    let mut hits = Vec::new();
    let walker = WalkDir::new(root).max_depth(if quick { 2 } else { 100 });
    for entry in walker.into_iter().filter_map(|e| e.ok()) {
        if !entry.file_type().is_file() { continue; }
        let path = entry.path();
        if let Some(hash) = sha256_file(path) {
            for sig in &sigs.signatures {
                if sig.hash == hash {
                    hits.push(ScanHit {
                        path: path.display().to_string(),
                        hash,
                        threat: sig.name.clone(),
                        severity: sig.severity,
                    });
                }
            }
        }
    }
    hits
}

fn quarantine(path: &Path) -> std::io::Result<PathBuf> {
    let qdir = dirs::home_dir().unwrap_or_default().join(".titan").join("quarantine");
    fs::create_dir_all(&qdir)?;
    let dest = qdir.join(path.file_name().unwrap_or_default());
    fs::rename(path, &dest)?;
    Ok(dest)
}

fn main() {
    let cli = Cli::parse();
    match cli.cmd {
        Commands::Scan { path, quick } => {
            println!("Scanning: {}", path);
            let hits = scan_path(Path::new(&path), quick);
            if hits.is_empty() {
                println!("No threats found.");
            } else {
                for h in &hits {
                    println!("[{}] {} -> {}", h.severity, h.threat, h.path);
                }
                println!("Total threats: {}", hits.len());
            }
        }
        Commands::Quarantine { path } => {
            match quarantine(Path::new(&path)) {
                Ok(d) => println!("Quarantined to {}", d.display()),
                Err(e) => eprintln!("Error: {}", e),
            }
        }
        Commands::ListSigs => {
            let db = load_sigs();
            for s in &db.signatures {
                println!("{} {} (sev {})", s.hash, s.name, s.severity);
            }
        }
    }
}
