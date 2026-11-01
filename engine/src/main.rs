use clap::Parser;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{self, Read};
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
    Scan { path: String, #[arg(short, long)] quick: bool, #[arg(long)] json: bool },
    Quarantine { path: String },
    Quarantines,
    ListSigs,
    Watch { path: String },
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
    // try loading from signatures/hashes.json
    let candidates = ["signatures/hashes.json", "hashes.json", "../signatures/hashes.json"];
    for c in candidates {
        if let Ok(data) = fs::read_to_string(c) {
            if let Ok(db) = serde_json::from_str::<SigDb>(&data) {
                if !db.signatures.is_empty() {
                    return db;
                }
            }
        }
    }
    // fallback embedded
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
                        hash: hash.clone(),
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
    if std::env::args().count() <= 1 {
        loop {
            println!();
            println!("================ TitanDefender ================");
            println!(" 1) Quick scan (common locations)");
            println!(" 2) Custom scan");
            println!(" 3) List signatures");
            println!(" 4) Real-time watch (info)");
            println!(" 5) Quarantine list (info)");
            println!(" 0) Exit");
            println!("==============================================");
            print!("Choice: ");
            use std::io::Write;
            std::io::stdout().flush().unwrap();
            let mut input = String::new();
            if std::io::stdin().read_line(&mut input).is_err() { break; }
            match input.trim() {
                "1" => { let h = scan_path(std::path::Path::new("C:\\"), true); println!("Threats: {}", h.len()); for x in &h { println!("[{}] {} -> {}", x.severity, x.threat, x.path); } }
                "2" => {
                    print!("Path: "); std::io::stdout().flush().unwrap();
                    let mut pth = String::new(); std::io::stdin().read_line(&mut pth).unwrap();
                    let h = scan_path(std::path::Path::new(pth.trim()), false);
                    println!("Threats: {}", h.len()); for x in &h { println!("[{}] {} -> {}", x.severity, x.threat, x.path); }
                }
                "3" => { let db = load_sigs(); println!("Loaded {} sigs", db.signatures.len()); }
                "4" => { println!("Run: titan watch <path>"); }
                "5" => { println!("Run: titan quarantines"); }
                "0" => break,
                _ => println!("Invalid choice"),
            }
        }
        return;
    }
    let cli = Cli::parse();
    match cli.cmd {
        Commands::Scan { path, quick, json: args_json } => {
            println!("Scanning: {}", path);
            let hits = scan_path(Path::new(&path), quick);
            if args_json {
                println!("{}", serde_json::to_string_pretty(&hits).unwrap());
            } else if hits.is_empty() {
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
            println!("Loaded {} signatures", db.signatures.len());
            for s in &db.signatures {
                println!("{} {} (sev {})", s.hash, s.name, s.severity);
            }
        }
        Commands::Quarantines => {
            let qdir = dirs::home_dir().unwrap_or_default().join(".titan").join("quarantine");
            if !qdir.exists() {
                println!("Quarantine empty.");
            } else {
                for e in fs::read_dir(&qdir).unwrap() {
                    if let Ok(e) = e {
                        println!("{}", e.file_name().to_string_lossy());
                    }
                }
            }
        }
        Commands::Watch { path } => {
            use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
            use std::sync::mpsc::channel;
            let (tx, rx) = channel();
            let mut watcher = RecommendedWatcher::new(tx, Config::default()).unwrap();
            watcher.watch(Path::new(&path), RecursiveMode::Recursive).unwrap();
            println!("Watching {} for changes...", path);
            for res in rx {
                match res {
                    Ok(event) => {
                        for p in event.paths {
                            if p.is_file() {
                                if let Some(h) = sha256_file(&p) {
                                    let db = load_sigs();
                                    for sig in &db.signatures {
                                        if sig.hash == h {
                                            println!("[THREAT] {} -> {}", sig.name, p.display());
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Err(e) => eprintln!("watch error: {}", e),
                }
            }
        }
    }
}
