# NSEI option-chain collector

This module collects NSE option-chain snapshots for NIFTY at 1-minute frequency and stores:

- raw JSON snapshots for auditability
- normalized parquet snapshots for research use

## Structure

- `src/nsei/client.py` - NSE session/bootstrap and fetch logic
- `src/nsei/normalize.py` - JSON to flat tabular rows
- `src/nsei/storage.py` - raw/parquet storage paths
- `src/nsei/collector.py` - one snapshot collection entrypoint
- `scripts/run_option_chain_day.py` - market-hours polling loop

## Run once

Set up the Python environment first:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Then collect a snapshot:

```bash
.venv/bin/python scripts/run_option_chain_day.py --symbol NIFTY --once
```

## Run for the day

```bash
.venv/bin/python scripts/run_option_chain_day.py --symbol NIFTY
```

## Output layout

Raw snapshots:

- `data/raw/option_chain/YYYY-MM-DD/NIFTY/HHMMSS.json`

Processed snapshots:

- `data/processed/option_chain/date=YYYY-MM-DD/symbol=NIFTY/HHMMSS.parquet`

## Notes

- NSE may require cookie/bootstrap refreshes, so the client first hits the option-chain page before calling the JSON endpoint.
- This is a v1 for NIFTY only, but the structure is ready to extend later.
- For true daily automation on macOS, the next step is to wire this script into `launchd`.
