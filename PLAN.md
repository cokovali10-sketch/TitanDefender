# TitanDefender — Plan

## Vision
Полноценный антивирус уровня Kaspersky с современным glassmorphism UI, поставляемый как `.exe` (Windows) и кроссплатформенно. Много полезных функций: защита в реальном времени, песочница, EDR, облачная репутация, родительский контроль, оптимизация системы.

## Tech Stack
- **Core engine**: Rust (производительность, безопасность)
- **Agent/service**: Go (сетевой слой, обновления)
- **UI**: Tauri + React + Tailwind (glassmorphism) → `.exe`
- **Backend**: Python FastAPI (облачная репутация, ML, телеметрия)
- **Kernel**: Windows minifilter driver (C), eBPF (Linux)
- **DB**: SQLite (локально), PostgreSQL (облако)
- **ML**: ONNX Runtime (классификация PE/скриптов)

## Features
1. Real-time on-access scanner (minifilter/eBPF)
2. Full system scan + quick scan + custom paths
3. YARA + hash signatures + heuristic + ML
4. Cloud reputation (file prevalence, signer trust)
5. Sandbox (dynamic analysis in isolated VM)
6. Quarantine + restore + delete
7. EDR telemetry → MITRE ATT&CK mapping
8. Anti-ransomware (behavioral, canary files)
9. Web protection (URL filtering, anti-phishing)
10. Email protection
11. Parental control
12. Firewall integration
13. Password manager (vault)
14. VPN (optional)
15. System optimizer (cleanup, startup manager)
16. Game mode (silent, low overhead)
17. Scheduled scans
18. Reports & statistics dashboard
19. Multi-language (RU/EN/KZ)
20. Auto-updates (engine + signatures + UI)

## UI Design (Glassmorphism)
- Frosted glass panels, blur, transparency
- Dark/light themes with accent gradients (cyan → violet)
- Smooth animations (framer-motion)
- Dashboard: threat level, scan progress, stats cards
- Sidebar navigation with icons
- Tray icon + notifications
- Onboarding wizard

## Architecture
```
┌─────────────────────────────────────────┐
│  Tauri UI (React, glassmorphism)        │
├─────────────────────────────────────────┤
│  Go Agent (IPC, updates, telemetry)     │
├─────────────────────────────────────────┤
│  Rust Engine (scan, heuristics, ML)     │
├─────────────────────────────────────────┤
│  Kernel Driver (minifilter/eBPF)        │
├─────────────────────────────────────────┤
│  Cloud Backend (FastAPI, PG, ML)        │
└─────────────────────────────────────────┘
```

## Phases
1. Core engine (Rust): scanner, YARA, hash DB, quarantine
2. Kernel driver (Windows minifilter) + eBPF (Linux)
3. Go agent + IPC + auto-updates
4. Tauri UI (glassmorphism) + tray + notifications
5. Cloud backend (reputation, ML, telemetry)
6. Sandbox + anti-ransomware + web protection
7. Extra features (parental, VPN, optimizer)
8. Testing, certification, packaging (.exe installer)

## Repo Structure
```
TitanDefender/
├── engine/          # Rust
├── driver/          # C (Windows), eBPF (Linux)
├── agent/           # Go
├── ui/              # Tauri + React
├── backend/         # Python FastAPI
├── signatures/      # YARA rules, hash DBs
├── tests/
├── docs/
└── packaging/       # .exe installer (NSIS/WiX)
```

## Risks
- Kernel code = BSOD risk → extensive testing on VMs
- Legal: antivirus may be flagged as PUP by other AVs → code signing, reputation
- Signature DBs require constant maintenance
- Performance: real-time scanning must be <1% CPU overhead

## Success Criteria
- Scan 10k files in <30s
- Real-time overhead <2% CPU
- Detection rate ≥95% on test sets
- Zero false positives on clean system files
- .exe installer <50MB
