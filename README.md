# 🧩 Foliofy

**Fill in a form, watch your portfolio render live, and download a complete,
deploy-ready website as a ZIP** — résumé, QR code, README and deploy kit
included. A React + Flask app with a local SQLite database.

> You enter your details → the backend generates an entire project folder
> (website + résumé + deploy kit + README) → you download it as a ZIP and ship
> it anywhere.

---

## ✨ Features

| | Feature | What it does |
|--|---------|--------------|
| 🎯 | **Portfolio generator** | Turns your details into a self-contained static site and zips the whole project. |
| 🪄 | **4 distinct themes** | Aurora · Neon · Minimal · Terminal — plus a custom accent colour. |
| 👁 | **Live preview** | The portfolio re-renders in an iframe as you type (desktop / tablet / mobile). |
| 📊 | **Completeness score** | A 0–100 score with an A+–D grade and specific suggestions on what to add. |
| 📄 | **PDF résumé** | A matching one-page `resume.pdf` is bundled in the ZIP. |
| 🔳 | **QR code** | An SVG QR to your site/profile, bundled as `assets/qr.svg`. |
| 🚀 | **One-click deploy kit** | GitHub Pages workflow + Netlify, Vercel and Docker/nginx configs. |
| 🗂 | **History (SQLite)** | Every generation is saved — reload it into the editor or re-download anytime. |

---

## 🛠 Tech stack

| Layer | What we used |
|-------|--------------|
| **Frontend** | React 18, Vite, Framer Motion, hand-written CSS (no UI kit) |
| **Backend** | Python 3, Flask, Flask-CORS |
| **Database** | SQLite (Python stdlib) — `backend/portfolio.db` |
| **Generation** | `qrcode` (SVG QR), `fpdf2` (PDF résumé), Python `zipfile` (deploy ZIP) |
| **Config** | python-dotenv |

The QR and PDF libraries are optional — the app degrades gracefully (placeholder
QR / printable `resume.html`) if they aren't installed.

---

## 📁 Project structure

```
Foliofy/  (folder: PortfolioGenerator)
├── backend/
│   ├── app.py             # Flask API: preview, score, generate, download, history, stats
│   ├── themes.py          # renders the portfolio site (4 themes) + the live preview HTML
│   ├── scoring.py         # heuristic completeness score + improvement suggestions
│   ├── generator.py       # assembles the deploy-ready ZIP (site + README + deploy kit)
│   ├── resume_pdf.py      # builds the one-page PDF résumé (fpdf2)
│   ├── qr_util.py         # builds the SVG QR code
│   ├── requirements.txt
│   └── generated/         # stored ZIPs on disk (gitignored)
└── frontend/
    ├── index.html
    ├── vite.config.js     # dev proxy /api → :5001
    ├── package.json
    └── src/
        ├── App.jsx        # multi-step form, live-preview wiring, history
        ├── api.js         # thin REST client
        ├── index.css
        └── components/    # Field, RepeatList, ThemePicker, ScorePanel, LivePreview, History
```

---

## 🚀 Getting started

**1. Backend (Flask + SQLite)**
```bash
cd PortfolioGenerator/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # API on http://localhost:5001
```

**2. Frontend (React + Vite)**
```bash
cd PortfolioGenerator/frontend
npm install
npm run dev              # http://localhost:5174  (proxies /api → :5001)
```

**Production** — `cd frontend && npm run build`, then `python app.py` serves the
built app from Flask at `:5001`.

---

## 🔌 API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/health` | Status + which optional features (PDF/QR) are available |
| `POST` | `/api/preview` | `{data}` → `{html, score, qr_svg}` for the live preview |
| `POST` | `/api/score` | `{data}` → completeness report |
| `POST` | `/api/generate` | `{data}` → builds + stores a ZIP, returns metadata |
| `GET` | `/api/download/<id>` | Stream a generated ZIP |
| `GET` | `/api/history` · `/api/history/<id>` · `DELETE /api/history/<id>` | Recent generations |
| `GET` | `/api/stats` | Totals (count, avg score, best) |

---

