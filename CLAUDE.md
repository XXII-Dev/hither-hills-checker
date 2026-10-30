# hither-hills-checker

Hither Hills campsite availability checker (Selenium).

This repo was split out of the old `XXII-Dev/XXII` workspace on 2026-10-30 with its git history preserved.

## Working rules

- **Python tooling:** `uv` for env + packages. Never `conda` / `anaconda` / `miniconda`.
- **Network exposure:** dev / preview servers bind to **localhost only**. Never `0.0.0.0`, never the LAN.
- **Performance:** precompute, vectorize NumPy, use the GPU when relevant. No `pandas` in hot loops.
- **Secrets:** never hard-code keys, tokens or passwords. Read them from environment variables / `.env` (gitignored).
- **Architecture:** when a feature involves time-series joins, filters, or "always up to date" expectations, default to a DB-backed pipeline rather than static precomputed JSON.
