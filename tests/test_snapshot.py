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
    assert all("kpis" in agent for agent in snapshot["agents"].values())
    assert all("pnl_net" in agent["kpis"] and "drawdown" in agent["kpis"] for agent in snapshot["agents"].values())
    assert all(a["environment"] in {"RESEARCH", "SIMULATION", "PAPER", "LIVE", "UNKNOWN"} for a in snapshot["agents"].values())
    datetime.fromisoformat(snapshot["generated_at"].replace("Z", "+00:00"))
    assert snapshot["notice"].startswith("DEMONSTRATION DATA")
    assert len(snapshot["decisions"]) >= 3
    assert len(snapshot["orders"]) >= 3
    assert len(snapshot["positions"]) >= 4
    assert {p["environment"] for p in snapshot["portfolios"]} == {"SIMULATION", "PAPER"}
    assert any(o["executed_quantity"] == 0 for o in snapshot["orders"])
    assert any(o["status"] == "PARTIAL" for o in snapshot["orders"])
    assert any(a["severity"] == "GUARDRAIL" for a in snapshot["alerts"])
    html = (ROOT / "dist/index.html").read_text()
    assert "MODE DÉMONSTRATION" in html
    assert "READ ONLY" in html
    assert "Portefeuilles" in html
    assert "Santé &amp; budgets" in html
    assert "snapshot.json" in (ROOT / "dist/app.js").read_text()
    print("PASS: snapshot contract, representative demo data and UI markers")

if __name__ == "__main__":
    main()
