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
    Scan { path: String, #[arg(short, long)] quick: bool, #[arg(long)] json: bool },
    Quarantine { path: String },
    Quarantines,
    ListSigs,
    Watch { path: String },
    DeepScan { path: String },
    Optimize,
    Menu,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Signature { hash: String, name: String, severity: u8 }

#[derive(Serialize, Deserialize, Debug)]
struct SigDb { signatures: Vec<Signature> }

#[derive(Serialize, Deserialize, Debug)]
struct ScanHit { path: String, hash: String, threat: String, severity: u8 }

fn sha256_file(path: &Path) -> Option<String> {
    let mut f = fs::File::open(path).ok()?;
    let mut buf = Vec::new();
    f.read_to_end(&mut buf).ok()?;
    let mut h = Sha256::new();
    h.update(&buf);
    Some(format!("{:x}", h.finalize()))
}

fn load_sigs() -> SigDb {
    let candidates = ["signatures/hashes.json", "hashes.json", "../signatures/hashes.json"];
    for c in candidates {
        if let Ok(data) = fs::read_to_string(c) {
            if let Ok(db) = serde_json::from_str::<SigDb>(&data) {
                if !db.signatures.is_empty() { return db; }
            }
        }
    }
    SigDb { signatures: vec![Signature { hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855".into(), name: "EmptyFile (test)".into(), severity: 1 }] }
}

fn scan_path(root: &Path, quick: bool) -> Vec<ScanHit> {
    let sigs = load_sigs();
    let mut hits = Vec::new();
    let walker = WalkDir::new(root).max_depth(if quick { 2 } else { 100 });
    for entry in walker.into_iter().filter_map(|e| e.ok()) {
        if !entry.file_type().is_file() { continue; }
        let path = entry.path();
        if let Some(hash) = sha256_file(path) {
            let h = hash.clone();
            for sig in &sigs.signatures {
                if sig.hash == h {
                    hits.push(ScanHit { path: path.display().to_string(), hash: h.clone(), threat: sig.name.clone(), severity: sig.severity });
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

fn interactive_menu() {
    loop {
        println!();
        println!("================ TitanDefender ================");
        println!(" 1) Quick scan");
        println!(" 2) Custom scan");
        println!(" 3) Deep scan");
        println!(" 4) List signatures");
        println!(" 5) Quarantine list");
        println!(" 6) Optimize PC");
        println!(" 7) Real-time watch (info)");
        println!(" 0) Exit");
        println!("==============================================");
        print!("Choice: ");
        use std::io::Write;
        std::io::stdout().flush().unwrap();
        let mut input = String::new();
        if std::io::stdin().read_line(&mut input).is_err() { break; }
        match input.trim() {
            "1" => { let h = scan_path(Path::new("C:\\\\"), true); println!("Threats: {}", h.len()); for x in &h { println!("[{}] {} -> {}", x.severity, x.threat, x.path); } }
            "2" => {
                print!("Path: "); std::io::stdout().flush().unwrap();
                let mut pth = String::new(); std::io::stdin().read_line(&mut pth).unwrap();
                let h = scan_path(Path::new(pth.trim()), false);
                println!("Threats: {}", h.len()); for x in &h { println!("[{}] {} -> {}", x.severity, x.threat, x.path); }
            }
            "3" => {
                print!("Path: "); std::io::stdout().flush().unwrap();
                let mut pth = String::new(); std::io::stdin().read_line(&mut pth).unwrap();
                let path = pth.trim();
                let mut total = 0usize; let mut threats = 0usize;
                for entry in WalkDir::new(path).into_iter().filter_map(|e| e.ok()) {
                    if !entry.file_type().is_file() { continue; }
                    total += 1;
                    if let Some(h) = sha256_file(entry.path()) {
                        let db = load_sigs();
                        for sig in &db.signatures { if sig.hash == h { threats += 1; println!("[THREAT] {} -> {}", sig.name, entry.path().display()); } }
                    }
                    if total % 5000 == 0 { println!("Scanned {} files...", total); }
                }
                println!("Deep scan complete: {} files, {} threats", total, threats);
            }
            "4" => { let db = load_sigs(); println!("Loaded {} sigs", db.signatures.len()); }
            "5" => {
                let qdir = dirs::home_dir().unwrap_or_default().join(".titan").join("quarantine");
                if !qdir.exists() { println!("Quarantine empty."); }
                else { for e in fs::read_dir(&qdir).unwrap() { if let Ok(e)=e { println!("{}", e.file_name().to_string_lossy()); } } }
            }
            "6" => {
                println!("=== Optimizer ===");
                let temp = std::env::temp_dir();
                let mut ts = 0u64; let mut tc = 0usize;
                for e in WalkDir::new(&temp).max_depth(3).into_iter().filter_map(|e| e.ok()) {
                    if e.file_type().is_file() { if let Ok(m)=e.metadata() { ts += m.len(); tc += 1; } }
                }
                println!("Temp files: {} ({} MB)", tc, ts/1024/1024);
                println!("Suggestions: clear temp, disable startup apps, update drivers, enable Game Mode.");
            }
            "7" => { println!("Run from CLI: titan watch <path>"); }
            "0" => break,
            _ => println!("Invalid choice"),
        }
    }
}

fn main() {
    if std::env::args().count() <= 1 {
        interactive_menu();
        return;
    }
    let cli = Cli::parse();
    match cli.cmd {
        Commands::Scan { path, quick, json: j } => {
            let hits = scan_path(Path::new(&path), quick);
            if j { println!("{}", serde_json::to_string_pretty(&hits).unwrap()); }
            else if hits.is_empty() { println!("No threats found."); }
            else { for h in &hits { println!("[{}] {} -> {}", h.severity, h.threat, h.path); } println!("Total threats: {}", hits.len()); }
        }
        Commands::Quarantine { path } => {
            match quarantine(Path::new(&path)) { Ok(d) => println!("Quarantined to {}", d.display()), Err(e) => eprintln!("Error: {}", e) }
        }
        Commands::Quarantines => {
            let qdir = dirs::home_dir().unwrap_or_default().join(".titan").join("quarantine");
            if !qdir.exists() { println!("Quarantine empty."); }
            else { for e in fs::read_dir(&qdir).unwrap() { if let Ok(e)=e { println!("{}", e.file_name().to_string_lossy()); } } }
        }
        Commands::ListSigs => { let db = load_sigs(); println!("Loaded {} sigs", db.signatures.len()); }
        Commands::Watch { path } => {
            use notify::{Config, RecommendedWatcher, RecursiveMode, Watcher};
            use std::sync::mpsc::channel;
            let (tx, rx) = channel();
            let mut watcher = RecommendedWatcher::new(tx, Config::default()).unwrap();
            watcher.watch(Path::new(&path), RecursiveMode::Recursive).unwrap();
            println!("Watching {}...", path);
            for res in rx {
                if let Ok(event) = res {
                    for p in event.paths {
                        if p.is_file() { if let Some(h) = sha256_file(&p) {
                            let db = load_sigs();
                            for sig in &db.signatures { if sig.hash == h { println!("[THREAT] {} -> {}", sig.name, p.display()); } }
                        } }
                    }
                }
            }
        }
        Commands::DeepScan { path } => {
            let mut total = 0usize; let mut threats = 0usize;
            for entry in WalkDir::new(&path).into_iter().filter_map(|e| e.ok()) {
                if !entry.file_type().is_file() { continue; }
                total += 1;
                if let Some(h) = sha256_file(entry.path()) {
                    let db = load_sigs();
                    for sig in &db.signatures { if sig.hash == h { threats += 1; println!("[THREAT] {} -> {}", sig.name, entry.path().display()); } }
                }
                if total % 5000 == 0 { println!("Scanned {} files...", total); }
            }
            println!("Deep scan complete: {} files, {} threats", total, threats);
        }
        Commands::Optimize => {
            println!("=== TitanDefender Optimizer ===");
            let temp = std::env::temp_dir();
            let mut ts = 0u64; let mut tc = 0usize;
            for e in WalkDir::new(&temp).max_depth(3).into_iter().filter_map(|e| e.ok()) {
                if e.file_type().is_file() { if let Ok(m) = e.metadata() { ts += m.len(); tc += 1; } }
            }
            println!("Temp files: {} ({} MB) - cleanable", tc, ts/1024/1024);
            println!("Suggestions: clear temp, disable startup apps, update drivers, enable Game Mode.");
        }
        Commands::Menu => { interactive_menu(); }
    }
}
