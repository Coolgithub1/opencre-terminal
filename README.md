# OpenCRE Terminal

OpenCRE Terminal is an open-source, static-first commercial real estate intelligence terminal. It is designed to run entirely through GitHub Pages and GitHub Actions, without a server, database, paid AI service, or proprietary data dependency.

## Phase 1 status

This repository currently implements **Phase 1**: a Vite + React + TypeScript terminal shell, synthetic demo datasets, and GitHub Pages deployment. All numbers shown in the application are explicitly labeled **DEMO DATA — synthetic, not real market data**.

## Local development

```bash
cd frontend
npm install
npm run dev
```

## Verification

```bash
cd frontend
npm run typecheck
npm run build
```

See [docs/architecture.md](docs/architecture.md), [docs/implementation-roadmap.md](docs/implementation-roadmap.md), and [TODO.md](TODO.md).

## License and data

Code is licensed under Apache-2.0. Synthetic demo data is included only to make the application runnable after cloning; it must not be treated as market research. Future source data must retain provenance, attribution, and its applicable license.
