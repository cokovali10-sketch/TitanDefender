from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import app
client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_reputation_unknown():
    r = client.post("/reputation", json={"sha256": "deadbeef"})
    assert r.status_code == 200
    assert r.json()["verdict"] == "unknown"

def test_report_and_stats():
    r = client.post("/report", json={"path": "/tmp", "threats": 2, "files_scanned": 100})
    assert r.status_code == 200
    r2 = client.get("/stats")
    assert r2.json()["total_reports"] >= 1

