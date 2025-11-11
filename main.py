import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Idea, IssueReport, SimulationScenario, Dataset

app = FastAPI(title="CitySense API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "CitySense Backend Ready"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response

# ---------------------- Mock/Open Data Endpoints ----------------------

# Static mock datasets for the Open Data Hub
MOCK_DATASETS: List[Dataset] = [
    Dataset(
        name="Public Transit Occupancy",
        description="Historical occupancy rates of buses and metro lines.",
        category="transport",
        last_updated="2025-01-15",
        download_csv="/data/transit_occupancy.csv",
        download_json="/data/transit_occupancy.json",
        api_endpoint="/api/datasets/transit-occupancy",
    ),
    Dataset(
        name="Air Quality Index",
        description="Hourly AQI, PM2.5, and CO2 measurements across districts.",
        category="air",
        last_updated="2025-01-20",
        download_csv="/data/aqi.csv",
        download_json="/data/aqi.json",
        api_endpoint="/api/datasets/air-quality",
    ),
    Dataset(
        name="Smart Bin Fill Levels",
        description="Smart waste bin telemetry including fill-level and pickup times.",
        category="waste",
        last_updated="2025-01-10",
        download_csv="/data/waste_bins.csv",
        download_json="/data/waste_bins.json",
        api_endpoint="/api/datasets/smart-bins",
    ),
]

@app.get("/api/datasets", response_model=List[Dataset])
def list_datasets():
    return MOCK_DATASETS

# ---------------------- Citizen Ideas & Issues ----------------------

@app.get("/api/ideas")
def get_ideas():
    try:
        ideas = get_documents("idea", {}, limit=100)
        # Ensure votes field exists
        for i in ideas:
            i["_id"] = str(i.get("_id"))
            i["votes"] = int(i.get("votes", 0))
        return {"items": ideas}
    except Exception:
        # Fallback mock when DB not configured
        mock = [
            {
                "_id": "demo1",
                "title": "Add bike lanes on Jalan Merdeka",
                "description": "Protected bike lanes to connect downtown and university district.",
                "category": "mobility",
                "location": "Jalan Merdeka",
                "tags": ["#GreenMobility"],
                "votes": 42,
            },
            {
                "_id": "demo2",
                "title": "Community solar on rooftops",
                "description": "Install solar panels on public buildings to offset grid load.",
                "category": "energy",
                "location": "Central District",
                "tags": ["#CleanEnergy"],
                "votes": 31,
            },
        ]
        return {"items": mock}

@app.post("/api/ideas")
def create_idea(idea: Idea):
    try:
        idea_id = create_document("idea", idea)
        return {"id": idea_id, "status": "created"}
    except Exception:
        # Accept but mock in non-DB mode
        return {"id": "mock", "status": "accepted"}

@app.post("/api/issues")
def report_issue(issue: IssueReport):
    try:
        issue_id = create_document("issuereport", issue)
        return {"id": issue_id, "status": "reported"}
    except Exception:
        return {"id": "mock", "status": "accepted"}

@app.post("/api/scenarios")
def save_scenario(scn: SimulationScenario):
    try:
        sid = create_document("simulationscenario", scn)
        return {"id": sid, "status": "saved"}
    except Exception:
        return {"id": "mock", "status": "accepted"}

# ---------------------- Dashboard Mock Streams ----------------------

class MapLayerPayload(BaseModel):
    layer: str

@app.get("/api/dashboard/layers")
def get_layers():
    return {
        "layers": [
            {"key": "transport", "label": "Transport"},
            {"key": "energy", "label": "Energy"},
            {"key": "waste", "label": "Waste"},
            {"key": "air", "label": "Air Quality"},
        ]
    }

@app.get("/api/dashboard/data")
def get_dashboard_data(time: Optional[str] = None):
    # Provide mock KPIs for each layer, time can be "now" or an ISO date
    return {
        "time": time or "now",
        "transport": {
            "ev_usage_pct": 38,
            "traffic_congestion": 0.57,
            "transit_occupancy": 0.66,
        },
        "energy": {
            "renewable_mix_pct": 52,
            "grid_load_mw": 820,
            "building_efficiency": 0.74,
        },
        "waste": {
            "smart_bin_fill": 0.41,
            "recycling_rate": 0.36,
        },
        "air": {
            "pm25": 18,
            "co2": 410,
            "aqi": 62,
        },
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
