"""
app.py
FastAPI web application providing an interactive demonstration and visual telemetry dashboard
for the @AppleSupport AI Agent, with real-time side-by-side baseline comparisons,
historical resolution inspection, and benchmark scorecards.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.agent import AppleSupportAgent
from baselines.trivial_baseline import TrivialBaselineAgent
from baselines.simple_baseline import SimpleBaselineAgent
from src.data_loader import load_golden_set

app = FastAPI(
    title="@AppleSupport AI Agent - Decision Telemetry & Benchmark Dashboard",
    version="1.0.0"
)

# Static files directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize models
print("[Init] Initializing AI models...")
agent = AppleSupportAgent()
trivial_agent = TrivialBaselineAgent()
simple_agent = SimpleBaselineAgent()
simple_agent.fit()
print("[Init] Models loaded and ready.")

class ProcessRequest(BaseModel):
    text: str
    thread_context: Optional[List[str]] = None

@app.get("/")
def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_path)

@app.post("/api/process")
def process_query(req: ProcessRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text query cannot be empty.")

    text = req.text.strip()
    thread = req.thread_context or []

    # 1. Process with AppleSupportAgent
    resp_agent = agent.process(text, thread)

    # 2. Process with Trivial Baseline
    resp_triv = trivial_agent.process(text, thread)

    # 3. Process with Simple Baseline
    resp_simp = simple_agent.process(text, thread)

    return {
        "query": text,
        "agent": resp_agent.to_dict(),
        "trivial": resp_triv,
        "simple": resp_simp
    }

@app.get("/api/benchmark")
def get_benchmark_results():
    results_path = os.path.join("eval", "benchmark_results.json")
    if not os.path.exists(results_path):
        # If not run yet, execute or return error
        raise HTTPException(status_code=404, detail="Benchmark results not found. Run eval/benchmark.py first.")
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/samples")
def get_curated_samples():
    golden = load_golden_set()
    # Pick 2 representative samples per stratum for quick demoing
    sample_ids = [
        "gold_001", "gold_013",  # Standard inbound (iOS 11 autocorrect, battery drain)
        "gold_073", "gold_074",  # Ambiguous multi-intent (bootloop during update, battery regression)
        "gold_109", "gold_110",  # Escalation edge (hyperbole vs literal battery swelling)
        "gold_137", "gold_138",  # Frustrated churn risk (demanding human manager, switching to Samsung)
        "gold_163", "gold_171"   # Multilingual & noise (Spanish support, gibberish)
    ]
    curated = [g for g in golden if g["id"] in sample_ids]
    return curated

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
