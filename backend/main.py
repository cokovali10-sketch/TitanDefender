from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import time

app = FastAPI(title="TitanDefender Cloud", version="0.2.0")

class HashCheck(BaseModel):
    sha256: str

class ScanReport(BaseModel):
    path: str
    threats: int
    files_scanned: int
    timestamp: Optional[float] = None

REPUTATION_DB = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {"verdict": "clean", "prevalence": 1000},
}

reports: List[ScanReport] = []

@app.get("/")
def root():
    return {"service": "TitanDefender Cloud", "status": "ok", "version": "0.2.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "uptime": time.time(), "reports": len(reports)}

@app.post("/reputation")
def reputation(req: HashCheck):
    info = REPUTATION_DB.get(req.sha256.lower())
    if info:
        return {"sha256": req.sha256, "verdict": info["verdict"], "prevalence": info["prevalence"]}
    return {"sha256": req.sha256, "verdict": "unknown", "prevalence": 0}

@app.post("/report")
def submit_report(rep: ScanReport):
    rep.timestamp = rep.timestamp or time.time()
    reports.append(rep)
    return {"status": "accepted", "id": len(reports)}

@app.get("/stats")
def stats():
    total_threats = sum(r.threats for r in reports)
    return {"total_reports": len(reports), "total_threats": total_threats, "files_scanned": sum(r.files_scanned for r in reports)}

@app.get("/history")
def history(limit: int = 50):
    return {"items": reports[-limit:], "total": len(reports)}

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """<html><head><title>TitanDefender Cloud</title><style>
    body{background:#0a0e1a;color:#e2e8f0;font-family:Segoe UI,sans-serif;padding:40px;}
    h1{color:#c4b5fd;} .card{background:#111827;border:1px solid #1e293b;border-radius:12px;padding:20px;margin:10px 0;}
    </style></head><body><h1>TitanDefender Cloud Dashboard</h1>
    <div class='card'><h3>API Endpoints</h3><ul>
    <li>GET /health</li><li>POST /reputation</li><li>POST /report</li><li>GET /stats</li></ul></div>
    <div class='card'><p>Service running. Connect your TitanDefender client.</p></div></body></html>"""
