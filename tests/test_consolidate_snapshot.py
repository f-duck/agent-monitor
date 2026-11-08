import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from monitor.consolidate_snapshot import atomic_write, consolidate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
NOW = datetime(2026, 11, 9, 10, 5, tzinfo=timezone.utc)


def main():
    stock = FIXTURES / "stock_status_v1.json"
    crypto = FIXTURES / "crypto_status_v1.json"
    result = consolidate(stock, crypto, now=NOW, max_age_seconds=1800)
    assert result["data_status"] == "LIVE_READ_ONLY"
    assert result["agents"]["stock"]["environment"] == "RESEARCH"
    assert result["agents"]["crypto"]["environment"] == "PAPER"
    assert result["agents"]["stock"]["kpis"]["pnl_net"] is None
    assert result["agents"]["crypto"]["kpis"]["pnl_net"] == 45.5
    assert result["decisions"][0]["agent"] == "Agent Stock"
    assert result["decisions"][1]["agent"] == "Agent Crypto"
    assert result["metrics"]["net_pnl"]["status"] == "UNAVAILABLE"

    stale = json.loads(crypto.read_text())
    stale["generated_at"] = "2026-11-09T08:00:00Z"
    with tempfile.TemporaryDirectory() as directory:
        stale_path = Path(directory) / "crypto.json"
        stale_path.write_text(json.dumps(stale), encoding="utf-8")
        result = consolidate(stock, stale_path, now=NOW, max_age_seconds=1800)
        assert result["data_status"] == "STALE"
        assert result["agents"]["crypto"]["status"] == "STALE"
        assert any("Crypto" in alert["title"] for alert in result["alerts"])

    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "snapshot.json"
        atomic_write(output, result)
        assert json.loads(output.read_text())["snapshot_id"] == result["snapshot_id"]
        assert list(output.parent.glob("*.tmp")) == []
    print("PASS: local Stock/Crypto consolidation, freshness and atomic write")


if __name__ == "__main__":
    main()
