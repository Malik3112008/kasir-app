# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kasir App V2 — a point-of-sale (POS) application for an Indonesian school cooperative ("Koperasi Siswa", branded "INOMART"). It has two interfaces: **Admin** (inventory, orders, reports, settings) and **Pembeli** (buyer — browse, cart, checkout via cash or QRIS). All UI text is in Bahasa Indonesia.

## Running the App

```bash
# First-time setup (creates venv, installs deps)
bash setup.sh

# Run the dev server (localhost:5000, auto-increments to 5010 if busy)
bash run.sh
# or directly:
python app.py
```

Default admin login: `admin` / `admin123`. Buyer login: `pembeli` / `beli123`.

There are no tests and no linter configured.

## Architecture

**Single-file Flask app** — the entire application lives in `app.py` (~1,700 lines). There are no blueprints, modules, or packages. All routes, data, and business logic are co-located in clearly marked sections within that file.

**No database** — all state (users, products, orders, cart, notifications) is stored in Python dicts/lists in memory. Data is lost on server restart. The only persisted file is `data_koperasi.json` (cooperative settings).

**Templates** are split across two directories loaded via Jinja2 `ChoiceLoader`:
- `kasir-admin/templates/` — 33 admin HTML templates
- `kasir-pembeli/templates/` — 16 buyer HTML templates

Templates use numeric prefixes (e.g., `03.`, `05.1.`, `14-`) from the original project spec. There is no shared base template or template inheritance — each page is standalone.

**Static assets** — each page has its own CSS file in `static/`. A shared `global-fix.css` provides CSS reset and common variables. No CSS preprocessors or JS bundlers. Frontend is plain HTML/CSS/JS with Font Awesome (CDN) and Google Fonts (Poppins).

**Vercel deployment** — `vercel.json` routes all requests to `api/index.py`, which imports the Flask `app` from `app.py`.

## Key Files

| File | Role |
|------|------|
| `app.py` | All routes and application logic (the only Python code that matters) |
| `api/index.py` | Vercel serverless entry point (imports `app` from `app.py`) |
| `data_koperasi.json` | Persisted cooperative settings (name, address, phone, hours, logo) |
| `static/global-fix.css` | Shared CSS reset/base styles |

## Route Prefixes

- `/admin/*` — all admin pages (login, dashboard, inventory, reports, orders, settings)
- `/pembeli/*` — all buyer pages (home, cart, payment, orders, ratings)

The root `/` serves as a landing page to choose Admin or Pembeli.

## Conventions

- Auth is checked per-route via `session.get('user')` — no centralized auth middleware or decorator.
- Reports export as printable HTML or Excel (via openpyxl). There is no real PDF generation — "PDF" exports are printable HTML pages.
- The `/dynamic_cards.css` route generates CSS dynamically for the denah (floor plan) feature.
- File uploads go to `static/gambar/` (admin logo) or `static/uploads/rating/` (buyer photos).
