from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TitanDefender Cloud", version="0.1.0")

class HashCheck(BaseModel):
    sha256: str

@app.get("/")
def root():
    return {"service": "TitanDefender Cloud", "status": "ok"}

@app.post("/reputation")
def reputation(req: HashCheck):
    # TODO: lookup in DB
    return {"sha256": req.sha256, "verdict": "unknown", "prevalence": 0}
