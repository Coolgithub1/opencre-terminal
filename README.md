# OpenCRE Terminal

OpenCRE Terminal is an open-source, static-first commercial real estate intelligence terminal. It is designed to run entirely through GitHub Pages and GitHub Actions, without a server, database, paid AI service, or proprietary data dependency.

## Current status

Phases 1 through 3 are complete. The project includes a Vite + React + TypeScript terminal shell, GitHub Pages deployment, reproducible static datasets, and deterministic market analytics/rankings. All provided datasets and displayed numbers are explicitly labeled **DEMO DATA — synthetic, not real market data**.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Generate and validate the static demo datasets:

```bash
python -m pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/validate_data.py
```

## Verification

```bash
cd frontend
npm run typecheck
npm run build
```

See [docs/architecture.md](docs/architecture.md), [docs/analytics.md](docs/analytics.md), [docs/implementation-roadmap.md](docs/implementation-roadmap.md), and [TODO.md](TODO.md).

## License and data

Code is licensed under Apache-2.0. Synthetic demo data is included only to make the application runnable after cloning; it must not be treated as market research. Future source data must retain provenance, attribution, and its applicable license.
