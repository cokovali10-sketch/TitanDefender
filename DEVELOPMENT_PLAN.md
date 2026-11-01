# TitanDefender Development Plan

## Project Overview
TitanDefender is a modern antivirus with glassmorphism UI. Located at D:\PortfolioProjects\TitanDefender. Tech stack: Rust (engine), Go (agent), Python FastAPI (cloud backend), React + Tauri (UI), C (kernel driver). GitHub: https://github.com/cokovali10-sketch/TitanDefender

## Current State
- 15 source files, ~238 lines of actual code
- Rust engine: CLI with scan, quarantine, list sigs, watch (hash-based detection)
- Go agent: basic IPC and updates (skeleton)
- Python backend: FastAPI with reputation endpoint (stub)
- React UI: glassmorphism single page with animated scan (enhanced)
- YARA signatures: 1 file (suspicious.yara)
- Kernel driver: minifilter.c skeleton
- CI/CD: GitHub Actions
- Status: Phase 1 (Core Engine) - very early

## Architecture
```
TitanDefender/
├── engine/          # Rust (scan, YARA, hash DB, quarantine, watch)
├── driver/          # C (Windows minifilter), eBPF (Linux)
├── agent/           # Go (IPC, updates, telemetry)
├── ui/              # Tauri + React (glassmorphism)
├── backend/         # Python FastAPI (cloud reputation, ML)
├── signatures/      # YARA rules, hash DBs
├── tests/
├── docs/
└── packaging/       # .exe installer
```

## Development Priorities

### Phase 1: Core Engine (High Priority)
1. **Signature Database**
   - Expand hash database (MD5, SHA1, SHA256)
   - Add YARA rule parsing and matching
   - Implement heuristic detection
   - Add signature update mechanism

2. **Scanning Engine**
   - Full system scan with progress reporting
   - Quick scan (common locations)
   - Custom path scan
   - Parallel scanning with thread pool
   - File type detection (PE, ELF, Mach-O, scripts)
   - Archive scanning (ZIP, RAR, 7z)

3. **Quarantine System**
   - Secure quarantine (encrypted storage)
   - Restore functionality
   - Delete permanently
   - Quarantine management (list, search, filter)

4. **Real-time Protection**
   - File system monitoring (notify crate)
   - On-access scanning
   - Behavioral monitoring
   - Process monitoring

### Phase 2: Detection (High Priority)
5. **YARA Integration**
   - YARA rule parser
   - Rule matching engine
   - Rule compilation and caching
   - Rule update mechanism

6. **Heuristic Detection**
   - PE file analysis (imports, sections, entropy)
   - Script analysis (PowerShell, VBScript, JavaScript)
   - Macro analysis (Office documents)
   - Packed executable detection

7. **ML Classification**
   - PE feature extraction
   - ONNX runtime integration
   - Model training pipeline
   - Model update mechanism

### Phase 3: Kernel Driver (Medium Priority)
8. **Windows Minifilter**
   - File system filter driver
   - On-access scanning hooks
   - Process monitoring
   - Registry monitoring

9. **Linux eBPF**
   - File system monitoring
   - Process monitoring
   - Network monitoring

### Phase 4: Agent & IPC (Medium Priority)
10. **Go Agent**
    - IPC with Rust engine
    - Auto-update mechanism
    - Telemetry collection
    - Cloud communication
    - Service management

11. **Communication**
    - Named pipes (Windows)
    - Unix sockets (Linux)
    - gRPC between components
    - Event streaming

### Phase 5: Cloud Backend (Medium Priority)
12. **FastAPI Backend**
    - Reputation lookup (hash, URL, IP)
    - Telemetry ingestion
    - ML model serving
    - Signature distribution
    - User management
    - Statistics and reporting

13. **Database**
    - PostgreSQL for cloud data
    - Redis for caching
    - Signature database
    - Threat intelligence feeds

### Phase 6: UI (Medium Priority)
14. **Tauri + React UI**
    - Dashboard with threat level
    - Scan progress and results
    - Quarantine management
    - Settings and configuration
    - History and reports
    - System tray integration
    - Notifications

15. **Glassmorphism Design**
    - Frosted glass panels
    - Dark/light themes
    - Smooth animations (framer-motion)
    - Responsive layout
    - Accessibility

### Phase 7: Advanced Features (Low Priority)
16. **Anti-Ransomware**
    - Behavioral monitoring
    - Canary files
    - File encryption detection
    - Automatic backup

17. **Web Protection**
    - URL filtering
    - Anti-phishing
    - Browser extension
    - DNS filtering

18. **EDR Telemetry**
    - Process monitoring
    - Network monitoring
    - MITRE ATT&CK mapping
    - Incident response

19. **Extra Features**
    - Parental control
    - Firewall integration
    - Password manager
    - VPN (optional)
    - System optimizer
    - Game mode

### Phase 8: Packaging & Distribution
20. **Packaging**
    - .exe installer (NSIS/WiX)
    - Code signing
    - Auto-update mechanism
    - Multi-language support (RU/EN/KZ)

21. **Testing & Certification**
    - Unit tests
    - Integration tests
    - Performance benchmarks
    - False positive testing
    - Certification (AV-TEST, VirusTotal)

## How to Work
1. Write code in batches (200-400 lines per file)
2. Commit after each batch: git add -A && git commit -m "..." && git push
3. Write functional, useful code - not stubs
4. Add tests for each new feature
5. Run tests before committing
6. Keep code compiling
7. Be honest about progress

## Code Style
- Rust: standard Rust conventions, cargo fmt, clippy
- Go: standard Go conventions, gofmt, go vet
- Python: PEP 8, type hints, black formatter
- React: functional components, hooks, TypeScript
- C: kernel coding style

## Verification Commands
- Rust: cargo build --release && cargo test
- Go: go build ./... && go vet ./... && go test ./...
- Python: python -m pytest tests/ -q
- React: npm run build
- C: make (in driver/)

## Git Workflow
- Commit after each meaningful change
- Use descriptive commit messages: "feat: add X", "fix: fix Y", "test: add Z"
- Push to remote after committing
- Never commit secrets or credentials

## Current Modules and Their Responsibilities

### engine/src/main.rs
- CLI with scan, quarantine, list sigs, watch
- SHA256 hash-based detection
- File walking with walkdir
- Quarantine functionality
- Real-time file watching with notify

### agent/main.go
- Basic IPC with engine
- Auto-update skeleton
- Service management (skeleton)

### backend/main.py
- FastAPI app
- Reputation endpoint (stub)
- Health check

### ui/App.jsx
- Glassmorphism UI
- Animated scan progress
- Status cards
- Quick scan button

### driver/minifilter.c
- Windows minifilter driver skeleton
- File system filter registration

### signatures/suspicious.yara
- YARA rules (basic)

## Immediate Next Steps
1. Expand signature database (hash DB with 100+ entries)
2. Add YARA rule parsing and matching
3. Implement heuristic detection (PE analysis)
4. Add quarantine management (list, restore, delete)
5. Implement full scan with progress reporting
6. Add real-time protection with notify
7. Build Go agent IPC with Rust engine
8. Expand FastAPI backend (reputation, telemetry)
9. Build Tauri + React UI (dashboard, settings)
10. Add unit tests for all components

## Risks
- Kernel code = BSOD risk → extensive testing on VMs
- Legal: antivirus may be flagged as PUP by other AVs → code signing, reputation
- Signature DBs require constant maintenance
- Performance: real-time scanning must be <1% CPU overhead
- ML models need training data

## Success Criteria
- Scan 10k files in <30s
- Real-time overhead <2% CPU
- Detection rate ≥95% on test sets
- Zero false positives on clean system files
- .exe installer <50MB

## Git Status
- Repository: https://github.com/cokovali10-sketch/TitanDefender
- Branch: main
- Latest commit: 458fdf4
- Working tree: clean

## Important Notes
- Do NOT create duplicate files
- Do NOT inflate statistics
- Keep code compiling and tests passing
- Be honest about progress
- Write functional, useful code
- Follow existing patterns from the codebase