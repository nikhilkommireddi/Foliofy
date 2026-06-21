"""
generator.py — assemble a complete, deployable portfolio project as a ZIP.

The archive contains a self-contained static website plus a proper README, a
PDF résumé, a QR code, and a one-click deploy kit (GitHub Pages, Netlify,
Vercel, Docker/nginx).
"""

from __future__ import annotations

import io
import json
import zipfile

import themes
from qr_util import make_qr_svg, primary_link
from resume_pdf import build_resume_pdf
from scoring import score_portfolio


def _slug(name: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in (name or "portfolio"))
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-") or "portfolio"


def project_name(data: dict) -> str:
    return f"{_slug(data.get('fullName') or 'my')}-portfolio"


# --------------------------------------------------------------------------- #
# Static project files
# --------------------------------------------------------------------------- #
def _readme(data: dict, score: dict) -> str:
    name = data.get("fullName") or "Your Name"
    title = data.get("title") or "Developer"
    skills = ", ".join(data.get("skills") or []) or "—"
    socials = "\n".join(
        f"- [{s.get('label','Link')}]({s.get('url','#')})"
        for s in (data.get("socials") or [])
    ) or "- _none yet_"
    theme = themes.theme_of(data)
    return f"""# {name} — Portfolio Website

> {data.get('tagline') or f'Personal portfolio for {name}, {title}.'}

A self-contained, responsive personal portfolio generated with
**Foliofy**. No build step, no dependencies — just open `index.html`.

![Theme](https://img.shields.io/badge/theme-{theme}-6d5efc) \
![Completeness](https://img.shields.io/badge/completeness-{score['score']}%25%20({score['grade']})-brightgreen) \
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ What's inside

| File | Purpose |
|------|---------|
| `index.html` | The portfolio website |
| `styles.css` | All styling (theme: **{theme}**) |
| `script.js` | Dark/light toggle, typed effect, scroll reveals |
| `resume.pdf` | A matching one-page résumé |
| `assets/qr.svg` | QR code linking to your profile |
| `data.json` | The structured data this site was built from |
| `.github/workflows/deploy.yml` | Auto-deploy to GitHub Pages |
| `netlify.toml`, `vercel.json` | One-click deploys |
| `Dockerfile`, `nginx.conf` | Container deploy |

## 🚀 Run locally

Because it's a static site, any of these work:

```bash
# Option A — just open it
open index.html

# Option B — a tiny local server (recommended)
python3 -m http.server 8000
# then visit http://localhost:8000
```

## 🌐 Deploy

**GitHub Pages** — push this folder to a repo; the included workflow publishes
it automatically. Then enable Pages → "GitHub Actions" in repo settings.

```bash
git init && git add . && git commit -m "My portfolio"
git branch -M main
git remote add origin https://github.com/<you>/{project_name(data)}.git
git push -u origin main
```

**Netlify / Vercel** — drag-and-drop the folder, or connect the repo. Config is
already included.

**Docker**

```bash
docker build -t my-portfolio .
docker run -p 8080:80 my-portfolio   # http://localhost:8080
```

## 🛠 Customise

Everything is plain HTML/CSS/JS — edit freely. To regenerate from changed data,
edit `data.json` and re-run Foliofy, or tweak the files directly.

## 👤 About

- **Name:** {name}
- **Title:** {title}
- **Skills:** {skills}

### Links
{socials}

---

_Generated with [Foliofy](#) · theme `{theme}` · completeness {score['score']}% ({score['grade']})._
"""


def _resume_html(data: dict) -> str:
    """Printable HTML résumé used when fpdf2 isn't available."""
    d = data
    rows = ""

    def block(title, items, fmt):
        nonlocal rows
        if not items:
            return
        rows += f"<h2>{themes.e(title)}</h2>"
        for it in items:
            rows += fmt(it)

    rows += f"<h1>{themes.e(d.get('fullName') or '')}</h1>"
    rows += f"<p class='t'>{themes.e(d.get('title') or '')}</p>"
    contact = " · ".join(
        themes.e(x) for x in [d.get("email"), d.get("phone"), d.get("location"), d.get("website")] if x
    )
    rows += f"<p class='c'>{contact}</p>"
    if d.get("about"):
        rows += f"<h2>Summary</h2><p>{themes.e(d['about'])}</p>"
    if d.get("skills"):
        rows += "<h2>Skills</h2><p>" + ", ".join(themes.e(s) for s in d["skills"]) + "</p>"
    block("Experience", d.get("experience") or [],
          lambda it: f"<h3>{themes.e(it.get('role',''))} — {themes.e(it.get('company',''))}</h3>"
                     f"<p class='c'>{themes.e(it.get('period',''))}</p><p>{themes.e(it.get('description',''))}</p>")
    block("Projects", d.get("projects") or [],
          lambda it: f"<h3>{themes.e(it.get('name',''))}</h3><p>{themes.e(it.get('description',''))}</p>")
    block("Education", d.get("education") or [],
          lambda it: f"<h3>{themes.e(it.get('degree',''))} — {themes.e(it.get('school',''))}</h3>"
                     f"<p class='c'>{themes.e(it.get('period',''))}</p>")
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Résumé</title>
<style>body{{font-family:Georgia,serif;max-width:720px;margin:40px auto;padding:0 24px;color:#1a1a1a;line-height:1.5}}
h1{{margin:0;font-size:30px}}h2{{border-bottom:2px solid #6d5efc;color:#6d5efc;margin-top:24px;font-size:16px;text-transform:uppercase;letter-spacing:.05em}}
h3{{margin:12px 0 2px;font-size:15px}}.t{{font-size:16px;margin:4px 0}}.c{{color:#777;font-size:13px;margin:2px 0}}
@media print{{body{{margin:0}}}}</style></head><body>{rows}</body></html>"""


def _deploy_workflow() -> str:
    return """name: Deploy portfolio to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: "."
      - id: deployment
        uses: actions/deploy-pages@v4
"""


def _dockerfile() -> str:
    return """FROM nginx:alpine
COPY . /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
"""


def _nginx() -> str:
    return """server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;
  location / { try_files $uri $uri/ /index.html; }
}
"""


def _gitignore() -> str:
    return ".DS_Store\nnode_modules/\n*.log\n"


# --------------------------------------------------------------------------- #
# Build the archive
# --------------------------------------------------------------------------- #
def build_zip(data: dict) -> tuple[bytes, dict]:
    """Return (zip_bytes, score_dict)."""
    score = score_portfolio(data)
    root = project_name(data)
    link = primary_link(data)

    files: dict[str, bytes] = {}

    def add(path: str, content):
        if isinstance(content, str):
            content = content.encode("utf-8")
        files[f"{root}/{path}"] = content

    add("index.html", themes.render_index_html(data))
    add("styles.css", themes.render_styles_css(data))
    add("script.js", themes.render_script_js(data))
    add("data.json", json.dumps(data, indent=2, ensure_ascii=False))
    add("assets/qr.svg", make_qr_svg(link))
    add("README.md", _readme(data, score))
    add("LICENSE", _mit_license(data))
    add(".gitignore", _gitignore())
    add(".github/workflows/deploy.yml", _deploy_workflow())
    add("netlify.toml", '[build]\n  publish = "."\n')
    add("vercel.json", json.dumps({"cleanUrls": True, "trailingSlash": False}, indent=2))
    add("Dockerfile", _dockerfile())
    add("nginx.conf", _nginx())

    pdf = build_resume_pdf(data)
    if pdf:
        add("resume.pdf", pdf)
    else:
        add("resume.html", _resume_html(data))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, content in files.items():
            zf.writestr(path, content)
    return buf.getvalue(), score


def _mit_license(data: dict) -> str:
    holder = data.get("fullName") or "The Author"
    return f"""MIT License

Copyright (c) {holder}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
