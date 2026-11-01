use std::path::Path;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct ScanResult {
    pub path: String,
    pub threat: Option<String>,
    pub severity: u8,
}

pub fn scan_file(path: &Path) -> ScanResult {
    // TODO: hash check, YARA, heuristic
    ScanResult {
        path: path.display().to_string(),
        threat: None,
        severity: 0,
    }
}

fn main() {
    println!("TitanDefender Engine v0.1.0");
    for arg in std::env::args().skip(1) {
        let r = scan_file(Path::new(&arg));
        println!("{:?}", r);
    }
}
