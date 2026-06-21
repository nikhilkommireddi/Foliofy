"""
Foliofy — Flask backend.

Endpoints
  GET  /api/health                 service + feature availability
  POST /api/preview                {data} -> {html, score, qr_svg}
  POST /api/score                  {data} -> score report
  POST /api/generate               {data} -> persists a ZIP, returns metadata
  GET  /api/download/<id>          stream the generated ZIP
  GET  /api/history                recent generations
  GET  /api/history/<id>           full stored data for one generation
  DELETE /api/history/<id>         delete a generation (+ its ZIP)
  GET  /api/stats                  totals
"""

from __future__ import annotations

import datetime
import json
import os
import sqlite3

from flask import Flask, g, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

import generator
import themes
from qr_util import make_qr_svg, primary_link
from scoring import score_portfolio

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portfolio.db")
GEN_DIR = os.path.join(BASE_DIR, "generated")
FRONTEND_DIST = os.path.join(BASE_DIR, "..", "frontend", "dist")
os.makedirs(GEN_DIR, exist_ok=True)

MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB of JSON is plenty

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
CORS(app)


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT,
            title       TEXT,
            theme       TEXT,
            score       INTEGER,
            grade       TEXT,
            data_json   TEXT,
            zip_path    TEXT,
            created_at  TEXT
        )
        """
    )
    db.commit()
    db.close()


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _data_from_request() -> dict:
    payload = request.get_json(silent=True) or {}
    data = payload.get("data", payload)
    return data if isinstance(data, dict) else {}


def _validate(data: dict):
    if not (data.get("fullName") or "").strip():
        return "Please add your name before generating."
    return None


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #
@app.route("/api/health")
def api_health():
    features = {"pdf": False, "qr": False}
    try:
        import fpdf  # noqa: F401
        features["pdf"] = True
    except Exception:
        pass
    try:
        import qrcode  # noqa: F401
        features["qr"] = True
    except Exception:
        pass
    return jsonify({"ok": True, "themes": themes.THEMES, "features": features})


@app.route("/api/preview", methods=["POST"])
def api_preview():
    data = _data_from_request()
    return jsonify(
        {
            "html": themes.render_preview_html(data),
            "score": score_portfolio(data),
            "qr_svg": make_qr_svg(primary_link(data)),
            "qr_target": primary_link(data),
        }
    )


@app.route("/api/score", methods=["POST"])
def api_score():
    return jsonify(score_portfolio(_data_from_request()))


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = _data_from_request()
    err = _validate(data)
    if err:
        return jsonify({"error": err}), 400

    zip_bytes, score = generator.build_zip(data)
    created = datetime.datetime.now().isoformat(timespec="seconds")

    db = get_db()
    cur = db.execute(
        """INSERT INTO portfolios
           (full_name, title, theme, score, grade, data_json, zip_path, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data.get("fullName", ""),
            data.get("title", ""),
            themes.theme_of(data),
            score["score"],
            score["grade"],
            json.dumps(data, ensure_ascii=False),
            "",
            created,
        ),
    )
    new_id = cur.lastrowid

    zip_path = os.path.join(GEN_DIR, f"{new_id}.zip")
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)
    db.execute("UPDATE portfolios SET zip_path = ? WHERE id = ?", (zip_path, new_id))
    db.commit()

    return jsonify(
        {
            "id": new_id,
            "filename": f"{generator.project_name(data)}.zip",
            "download_url": f"/api/download/{new_id}",
            "size_bytes": len(zip_bytes),
            "score": score,
            "created_at": created,
        }
    )


@app.route("/api/download/<int:item_id>")
def api_download(item_id):
    db = get_db()
    row = db.execute(
        "SELECT data_json, zip_path FROM portfolios WHERE id = ?", (item_id,)
    ).fetchone()
    if row is None or not row["zip_path"] or not os.path.exists(row["zip_path"]):
        return jsonify({"error": "Not found"}), 404
    data = json.loads(row["data_json"])
    return send_file(
        row["zip_path"],
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{generator.project_name(data)}.zip",
    )


@app.route("/api/history")
def api_history():
    db = get_db()
    rows = db.execute(
        "SELECT id, full_name, title, theme, score, grade, created_at "
        "FROM portfolios ORDER BY id DESC LIMIT 30"
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/history/<int:item_id>")
def api_history_item(item_id):
    db = get_db()
    row = db.execute(
        "SELECT id, data_json, score, grade, created_at FROM portfolios WHERE id = ?",
        (item_id,),
    ).fetchone()
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(
        {
            "id": row["id"],
            "data": json.loads(row["data_json"]),
            "score": row["score"],
            "grade": row["grade"],
            "created_at": row["created_at"],
        }
    )


@app.route("/api/history/<int:item_id>", methods=["DELETE"])
def api_history_delete(item_id):
    db = get_db()
    row = db.execute("SELECT zip_path FROM portfolios WHERE id = ?", (item_id,)).fetchone()
    if row and row["zip_path"] and os.path.exists(row["zip_path"]):
        try:
            os.remove(row["zip_path"])
        except OSError:
            pass
    db.execute("DELETE FROM portfolios WHERE id = ?", (item_id,))
    db.commit()
    return jsonify({"ok": True})


@app.route("/api/stats")
def api_stats():
    db = get_db()
    row = db.execute(
        "SELECT COUNT(*) AS total, AVG(score) AS avg_score, MAX(score) AS best "
        "FROM portfolios"
    ).fetchone()
    return jsonify(
        {
            "total": row["total"] or 0,
            "avg_score": round(row["avg_score"] or 0, 1),
            "best": row["best"] or 0,
        }
    )


# --------------------------------------------------------------------------- #
# Serve the built frontend (after `npm run build`)
# --------------------------------------------------------------------------- #
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    full_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.exists(full_path):
        return send_from_directory(FRONTEND_DIST, path)
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return (
        "<h1>Foliofy API</h1>"
        "<p>Frontend isn't built. In <code>frontend/</code> run "
        "<code>npm install &amp;&amp; npm run dev</code> (dev) or "
        "<code>npm run build</code> to serve from Flask.</p>",
        200,
    )


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5001"))
    app.run(debug=True, host="0.0.0.0", port=port)
