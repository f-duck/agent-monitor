"""Consolidate local Stock and Crypto status exports without network access."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ENVIRONMENTS = {"RESEARCH", "SIMULATION", "PAPER", "LIVE", "UNKNOWN"}
STATUSES = {"RUNNING", "STALE", "OFFLINE", "UNKNOWN"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc)


def _number(value: Any) -> float | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, dict):
        return _number(value.get("value"))
    return None


def _text(value: Any, default: str = "Indisponible") -> str:
    if isinstance(value, dict):
        value = value.get("value") or value.get("status")
    return str(value) if value not in (None, "") else default


def _items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        nested = value.get("items") or value.get("records") or value.get("rows")
        if isinstance(nested, list):
            return [item for item in nested if isinstance(item, dict)]
    return []


def _field(source: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in source:
            return source[name]
    return None


def _kpis(source: dict[str, Any]) -> dict[str, float | int | None]:
    kpis = source.get("kpis") if isinstance(source.get("kpis"), dict) else {}
    budget = source.get("budget") if isinstance(source.get("budget"), dict) else {}
    pnl = source.get("pnl") if isinstance(source.get("pnl"), dict) else {}
    return {
        "pnl_net": _number(kpis.get("pnl_net", pnl.get("net"))),
        "drawdown": _number(kpis.get("drawdown", source.get("drawdown"))),
        "portfolio_value": _number(kpis.get("portfolio_value", budget.get("portfolio_value"))),
        "available_budget": _number(kpis.get("available_budget", budget.get("available"))),
        "committed_budget": _number(kpis.get("committed_budget", budget.get("committed"))),
        "ai_cost": _number(kpis.get("ai_cost", source.get("ai_cost"))),
    }


def _unavailable(reason: str) -> dict[str, Any]:
    return {"value": None, "status": "UNAVAILABLE", "reason": reason}


def _agent_summary(source: dict[str, Any], key: str, now: datetime, max_age: timedelta) -> tuple[dict[str, Any], bool, bool]:
    name = "Agent Crypto" if key == "crypto" else "Agent Stock"
    generated = _parse_time(source.get("generated_at"))
    source_status = str(source.get("status", "UNKNOWN")).upper()
    status = source_status if source_status in STATUSES else "UNKNOWN"
    stale = generated is None or now - generated > max_age
    if stale and status == "RUNNING":
        status = "STALE"
    environment = str(source.get("environment", "UNKNOWN")).upper()
    if environment not in ENVIRONMENTS:
        environment = "UNKNOWN"
    health = _text(source.get("health"), "UNAVAILABLE")
    if stale:
        health = f"{health} · snapshot périmé" if health != "UNAVAILABLE" else "Snapshot périmé"
    alerts = source.get("alerts") if isinstance(source.get("alerts"), list) else []
    summary = {
        "name": name,
        "status": status,
        "environment": environment,
        "phase": _text(source.get("phase")),
        "last_seen_at": generated.isoformat().replace("+00:00", "Z") if generated else None,
        "health": health,
        "machine": _text(source.get("machine")),
        "release": _text(source.get("release") or source.get("source_release")),
        "cpu": _text(source.get("cpu")),
        "memory": _text(source.get("memory")),
        "disk_free": _text(source.get("disk_free")),
        "freshness": _text(source.get("freshness"), "STALE" if stale else "Indisponible"),
        "alerts": [a if isinstance(a, str) else a.get("title", "Alert") for a in alerts],
        "kpis": _kpis(source),
    }
    return summary, stale, generated is not None


def _tag_items(items: Any, key: str) -> list[dict[str, Any]]:
    tagged = []
    for item in _items(items):
        copy = dict(item)
        copy.setdefault("agent", "Agent Crypto" if key == "crypto" else "Agent Stock")
        tagged.append(copy)
    return tagged


def _read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data, raw


def consolidate(stock_path: Path, crypto_path: Path, *, now: datetime | None = None, max_age_seconds: int = 1800) -> dict[str, Any]:
    now = (now or _utc_now()).astimezone(timezone.utc).replace(microsecond=0)
    stock, stock_raw = _read_json(stock_path)
    crypto, crypto_raw = _read_json(crypto_path)
    max_age = timedelta(seconds=max_age_seconds)
    stock_agent, stock_stale, stock_timestamped = _agent_summary(stock, "stock", now, max_age)
    crypto_agent, crypto_stale, crypto_timestamped = _agent_summary(crypto, "crypto", now, max_age)
    if not stock_timestamped or not crypto_timestamped:
        data_status = "UNAVAILABLE"
    elif stock_stale or crypto_stale:
        data_status = "STALE"
    else:
        data_status = "LIVE_READ_ONLY"
    digest = hashlib.sha256(stock_raw + b"\n" + crypto_raw).hexdigest()[:16]
    generated_at = now.isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "1.0",
        "snapshot_id": f"consolidated-{now.strftime('%Y%m%dT%H%M%SZ')}-{digest}",
        "generated_at": generated_at,
        "data_status": data_status,
        "notice": "LIVE READ-ONLY DATA" if data_status == "LIVE_READ_ONLY" else "Some source data is stale or unavailable",
        "agents": {"stock": stock_agent, "crypto": crypto_agent},
        "metrics": {
            "net_pnl": _unavailable("Consolidation multi-environment non calculée"),
            "drawdown": _unavailable("Consolidation multi-environment non calculée"),
            "available_budget": _unavailable("Devises et environnements distincts"),
            "committed_budget": _unavailable("Devises et environnements distincts"),
            "ai_cost": _unavailable("Unités de coût conservées par agent"),
        },
        "portfolios": [],
        "decisions": _tag_items(stock.get("decisions"), "stock") + _tag_items(crypto.get("decisions"), "crypto"),
        "orders": _tag_items(stock.get("orders"), "stock") + _tag_items(crypto.get("orders"), "crypto"),
        "positions": _tag_items(stock.get("positions"), "stock") + _tag_items(crypto.get("positions"), "crypto"),
        "quotas": _tag_items(stock.get("quotas"), "stock") + _tag_items(crypto.get("quotas"), "crypto"),
        "diagnostics": _tag_items(stock.get("diagnostics"), "stock") + _tag_items(crypto.get("diagnostics"), "crypto"),
        "alerts": ([{"severity": "WARN", "title": "Stock snapshot périmé", "detail": "Aucun nouveau snapshot Stock dans la fenêtre attendue."}] if stock_stale else []) + ([{"severity": "WARN", "title": "Crypto snapshot périmé", "detail": "Aucun nouveau snapshot Crypto dans la fenêtre attendue."}] if crypto_stale else []),
        "work": {"project": "Agent Monitor", "phase": "LIVE_READ_ONLY local", "roadmap": [], "commits": []},
    }


def atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consolidate local Agent Monitor status exports")
    parser.add_argument("--stock", type=Path, required=True)
    parser.add_argument("--crypto", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-age-seconds", type=int, default=1800)
    parser.add_argument("--now", help="UTC ISO timestamp for deterministic tests")
    args = parser.parse_args(argv)
    now = _parse_time(args.now) if args.now else None
    payload = consolidate(args.stock, args.crypto, now=now, max_age_seconds=args.max_age_seconds)
    atomic_write(args.output, payload)
    print(json.dumps({"output": str(args.output), "snapshot_id": payload["snapshot_id"], "data_status": payload["data_status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
