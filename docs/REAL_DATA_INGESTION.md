# Real-data local ingestion

The local consolidator is intentionally separate from the Stock and Crypto runtimes. It performs no network access and writes only the requested output file.

```sh
cd /Users/ssg/agent-monitor
python3 -B scripts/consolidate_snapshot_v1.py \
  --stock /private/path/stock_status.json \
  --crypto /private/path/crypto_status.json \
  --output /private/path/snapshot.json
```

The default freshness window is 30 minutes. Use `--max-age-seconds` only for a measured test. If either source is missing a valid timestamp, the consolidated result is `UNAVAILABLE`; if one is older than the window, it is `STALE`. The consolidator never calculates a misleading cross-environment PnL or budget total: those values remain unavailable unless a future contract defines currency and environment aggregation.

For a private local preview, place the generated `snapshot.json` beside the PWA assets. The browser tries `snapshot.json` first and falls back to the explicitly marked `DEMO` fixture. Do not commit or publish a real `snapshot.json`; the current GitHub Pages site is public and remains DEMO-only.

The next integration step is an Intel-side, read-only publisher to a private Cloudflare endpoint after WebAuthn, redaction, quotas and retention are validated. No scheduler or cloud resource is created by this local tool.

## Intel fusion sequence

The Stock exporter writes its local output on Intel. The Crypto exporter writes its local output on Mini; Intel retrieves a copy into a private temporary directory. Nothing is sent from Stock to Mini.

```sh
python3 -B scripts/consolidate_snapshot_v1.py \
  --stock /private/intel/path/stock_status.json \
  --crypto /private/intel/tmp/crypto_status.json \
  --output /private/intel/tmp/snapshot.json \
  --max-age-seconds 1800
```

The output is the only input that a future private publisher may send to Cloudflare. Until the private endpoint and authentication are validated, inspect it locally and keep it outside the public repository.
