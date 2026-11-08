import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    snapshot = json.loads((ROOT / "schema/demo-snapshot.json").read_text())
    schema = json.loads((ROOT / "schema/snapshot.schema.json").read_text())
    assert snapshot["schema_version"] == schema["properties"]["schema_version"]["const"]
    assert snapshot["data_status"] == "DEMO"
    assert set(snapshot["agents"]) == {"stock", "crypto"}
    assert all(a["environment"] in {"RESEARCH", "SIMULATION", "PAPER", "LIVE", "UNKNOWN"} for a in snapshot["agents"].values())
    datetime.fromisoformat(snapshot["generated_at"].replace("Z", "+00:00"))
    for metric in snapshot["metrics"].values():
        assert metric["status"] == "UNAVAILABLE"
        assert metric["value"] is None
    html = (ROOT / "dist/index.html").read_text()
    assert "MODE DÉMONSTRATION" in html
    assert "READ ONLY" in html
    print("PASS: snapshot contract, unavailable-value policy and demo UI markers")

if __name__ == "__main__":
    main()
