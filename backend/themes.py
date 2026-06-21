"""
themes.py — turns portfolio data into a real, self-contained website.

The same semantic HTML is rendered for every theme; the look is driven by a
`theme-*` body class and an injected accent colour. Four genuinely distinct
themes are shipped: aurora, neon, minimal and terminal.

Public helpers:
    render_index_html(data)  -> str   (links styles.css + script.js)
    render_styles_css(data)  -> str
    render_script_js(data)   -> str
    render_preview_html(data)-> str   (one file, inline css/js, for an <iframe>)
"""

from __future__ import annotations

import html
import json

THEMES = ["aurora", "neon", "minimal", "terminal"]
DEFAULT_ACCENT = {
    "aurora": "#6d5efc",
    "neon": "#13f1c4",
    "minimal": "#111827",
    "terminal": "#33ff8a",
}


def e(value) -> str:
    """HTML-escape any value to a safe string."""
    return html.escape("" if value is None else str(value))


def _list(data, key):
    val = data.get(key)
    return val if isinstance(val, list) else []


def theme_of(data) -> str:
    theme = (data.get("theme") or "aurora").lower()
    return theme if theme in THEMES else "aurora"


def accent_of(data) -> str:
    accent = (data.get("accent") or "").strip()
    if accent:
        return accent
    return DEFAULT_ACCENT[theme_of(data)]


# --------------------------------------------------------------------------- #
# Section builders (return HTML strings)
# --------------------------------------------------------------------------- #
def _nav(data):
    name = e(data.get("fullName") or "Your Name")
    links = [
        ("about", "About"),
        ("skills", "Skills"),
        ("projects", "Projects"),
        ("experience", "Experience"),
        ("contact", "Contact"),
    ]
    items = "".join(
        f'<a href="#{slug}">{label}</a>' for slug, label in links
    )
    initials = "".join(p[0] for p in (data.get("fullName") or "Y N").split()[:2]).upper()
    return f"""
  <header class="nav">
    <a class="brand" href="#top"><span class="brand-badge">{e(initials)}</span>{name}</a>
    <nav class="nav-links">{items}</nav>
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle colour mode">◑</button>
  </header>"""


def _hero(data):
    name = e(data.get("fullName") or "Your Name")
    title = e(data.get("title") or "Your Role")
    tagline = e(data.get("tagline") or "")
    location = e(data.get("location") or "")
    email = e(data.get("email") or "")
    avatar = (data.get("avatarUrl") or "").strip()

    socials = ""
    for s in _list(data, "socials"):
        label = e(s.get("label") or "Link")
        url = e(s.get("url") or "#")
        socials += f'<a class="chip" href="{url}" target="_blank" rel="noopener">{label}</a>'

    avatar_html = (
        f'<img class="avatar" src="{e(avatar)}" alt="{name}" />'
        if avatar
        else f'<div class="avatar avatar-fallback">{e("".join(p[0] for p in (data.get("fullName") or "Y N").split()[:2]).upper())}</div>'
    )

    loc_html = f'<span class="loc">📍 {location}</span>' if location else ""
    cta = (
        f'<a class="btn btn-primary" href="mailto:{email}">Get in touch</a>'
        if email
        else ""
    )

    return f"""
  <section class="hero" id="top">
    <div class="hero-text">
      <p class="kicker">Hi, I'm</p>
      <h1 class="display">{name}</h1>
      <p class="role"><span id="typed" data-text="{title}">{title}</span></p>
      <p class="tagline">{tagline}</p>
      <div class="hero-meta">{loc_html}</div>
      <div class="hero-actions">
        {cta}
        <a class="btn btn-ghost" href="resume.pdf" download>Download résumé</a>
      </div>
      <div class="socials">{socials}</div>
    </div>
    <div class="hero-art">{avatar_html}</div>
  </section>"""


def _about(data):
    about = (data.get("about") or "").strip()
    if not about:
        return ""
    paras = "".join(f"<p>{e(p)}</p>" for p in about.split("\n") if p.strip())
    return f"""
  <section class="section" id="about">
    <h2 class="section-title"><span>01</span> About</h2>
    <div class="prose">{paras}</div>
  </section>"""


def _skills(data):
    skills = _list(data, "skills")
    if not skills:
        return ""
    chips = "".join(f'<li class="skill">{e(s)}</li>' for s in skills)
    return f"""
  <section class="section" id="skills">
    <h2 class="section-title"><span>02</span> Skills</h2>
    <ul class="skills-grid">{chips}</ul>
  </section>"""


def _projects(data):
    projects = _list(data, "projects")
    if not projects:
        return ""
    cards = ""
    for p in projects:
        tech = "".join(f"<span>{e(t)}</span>" for t in (p.get("tech") or []))
        links = ""
        if p.get("link"):
            links += f'<a href="{e(p["link"])}" target="_blank" rel="noopener">Live ↗</a>'
        if p.get("repo"):
            links += f'<a href="{e(p["repo"])}" target="_blank" rel="noopener">Code ↗</a>'
        cards += f"""
      <article class="card reveal">
        <h3>{e(p.get("name") or "Untitled project")}</h3>
        <p>{e(p.get("description") or "")}</p>
        <div class="tech">{tech}</div>
        <div class="card-links">{links}</div>
      </article>"""
    return f"""
  <section class="section" id="projects">
    <h2 class="section-title"><span>03</span> Projects</h2>
    <div class="cards">{cards}</div>
  </section>"""


def _timeline(data, key, title, num):
    items = _list(data, key)
    if not items:
        return ""
    rows = ""
    for it in items:
        primary = it.get("role") or it.get("degree") or ""
        secondary = it.get("company") or it.get("school") or ""
        rows += f"""
      <li class="reveal">
        <div class="t-dot"></div>
        <div class="t-body">
          <div class="t-head">
            <strong>{e(primary)}</strong>
            <span class="t-period">{e(it.get("period") or "")}</span>
          </div>
          <div class="t-sub">{e(secondary)}</div>
          <p>{e(it.get("description") or "")}</p>
        </div>
      </li>"""
    return f"""
  <section class="section" id="{key}">
    <h2 class="section-title"><span>{num}</span> {e(title)}</h2>
    <ul class="timeline">{rows}</ul>
  </section>"""


def _contact(data):
    email = e(data.get("email") or "")
    phone = e(data.get("phone") or "")
    website = (data.get("website") or "").strip()
    rows = ""
    if email:
        rows += f'<a class="contact-row" href="mailto:{email}"><span>Email</span>{email}</a>'
    if phone:
        rows += f'<a class="contact-row" href="tel:{phone}"><span>Phone</span>{phone}</a>'
    if website:
        rows += f'<a class="contact-row" href="{e(website)}" target="_blank" rel="noopener"><span>Website</span>{e(website)}</a>'
    if not rows:
        return ""
    return f"""
  <section class="section" id="contact">
    <h2 class="section-title"><span>05</span> Contact</h2>
    <div class="contact-card">
      {rows}
    </div>
  </section>"""


def _footer(data):
    name = e(data.get("fullName") or "Your Name")
    return f"""
  <footer class="footer">
    <p>© <span id="year"></span> {name}. Built with Foliofy.</p>
  </footer>"""


def _body(data):
    return "".join(
        [
            _nav(data),
            '<main class="wrap">',
            _hero(data),
            _about(data),
            _skills(data),
            _projects(data),
            _timeline(data, "experience", "Experience", "04"),
            _timeline(data, "education", "Education", "06"),
            _contact(data),
            "</main>",
            _footer(data),
        ]
    )


# --------------------------------------------------------------------------- #
# CSS
# --------------------------------------------------------------------------- #
def render_styles_css(data) -> str:
    accent = accent_of(data)
    return _BASE_CSS.replace("__ACCENT__", accent)


_BASE_CSS = r"""
:root{
  --accent: __ACCENT__;
  --bg:#0e0f1a; --ink:#eef0ff; --soft:#a6abce; --card:#171a2b;
  --line:rgba(255,255,255,.09); --radius:18px;
  --font:'Plus Jakarta Sans',system-ui,sans-serif;
  --mono:'JetBrains Mono','SF Mono',ui-monospace,monospace;
}
body.light{ --bg:#f6f7fb; --ink:#14152b; --soft:#5a5f7a; --card:#ffffff; --line:rgba(20,21,43,.08); }
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--font);background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;line-height:1.55;transition:background .4s,color .4s}
a{color:inherit;text-decoration:none}
h1,h2,h3,.display{font-family:'Space Grotesk',var(--font);letter-spacing:-.02em}
.wrap{max-width:1040px;margin:0 auto;padding:0 24px}
img{max-width:100%}

/* nav */
.nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;
  gap:16px;padding:14px 24px;backdrop-filter:blur(14px);background:color-mix(in srgb,var(--bg) 72%,transparent);
  border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-weight:800}
.brand-badge{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;
  background:var(--accent);color:#fff;font-size:13px}
.nav-links{display:flex;gap:20px;font-weight:600;color:var(--soft)}
.nav-links a:hover{color:var(--ink)}
.theme-toggle{border:1px solid var(--line);background:transparent;color:var(--ink);
  width:38px;height:38px;border-radius:10px;cursor:pointer;font-size:16px}
@media(max-width:720px){.nav-links{display:none}}

/* hero */
.hero{display:grid;grid-template-columns:1.4fr .9fr;gap:40px;align-items:center;padding:72px 0 40px}
.kicker{color:var(--accent);font-weight:700;letter-spacing:.12em;text-transform:uppercase;font-size:13px}
.display{font-size:clamp(34px,6vw,64px);line-height:1.02;margin:6px 0 4px}
.role{font-size:clamp(18px,3vw,26px);font-weight:700;color:var(--accent);min-height:1.2em}
.tagline{color:var(--soft);font-size:18px;margin-top:10px;max-width:44ch}
.hero-meta{margin-top:14px;color:var(--soft);font-weight:600}
.hero-actions{display:flex;gap:12px;margin-top:22px;flex-wrap:wrap}
.btn{padding:12px 20px;border-radius:12px;font-weight:700;cursor:pointer;border:1px solid var(--line);transition:transform .15s,box-shadow .2s}
.btn:hover{transform:translateY(-2px)}
.btn-primary{background:var(--accent);color:#fff;border-color:transparent;box-shadow:0 14px 30px -12px var(--accent)}
.btn-ghost{background:transparent;color:var(--ink)}
.socials{display:flex;gap:10px;flex-wrap:wrap;margin-top:20px}
.chip{padding:8px 14px;border:1px solid var(--line);border-radius:999px;font-weight:600;font-size:14px;color:var(--soft)}
.chip:hover{color:var(--ink);border-color:var(--accent)}
.hero-art{display:grid;place-items:center}
.avatar{width:240px;height:240px;border-radius:28px;object-fit:cover;border:1px solid var(--line);
  box-shadow:0 30px 60px -24px var(--accent)}
.avatar-fallback{display:grid;place-items:center;font-size:64px;font-weight:800;color:#fff;
  background:linear-gradient(135deg,var(--accent),#000)}
@media(max-width:820px){.hero{grid-template-columns:1fr;text-align:center}.socials,.hero-actions,.hero-meta{justify-content:center;display:flex}.tagline{margin-inline:auto}}

/* sections */
.section{padding:46px 0;border-top:1px solid var(--line)}
.section-title{font-size:26px;display:flex;align-items:center;gap:12px;margin-bottom:24px}
.section-title span{font-family:var(--mono);font-size:14px;color:var(--accent);
  border:1px solid var(--line);border-radius:8px;padding:4px 8px}
.prose p{color:var(--soft);max-width:70ch;margin-bottom:12px;font-size:17px}

.skills-grid{list-style:none;display:flex;flex-wrap:wrap;gap:10px}
.skill{padding:9px 16px;border-radius:12px;background:var(--card);border:1px solid var(--line);font-weight:600}
.skill:hover{border-color:var(--accent);color:var(--accent)}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-4px);border-color:var(--accent)}
.card h3{font-size:20px;margin-bottom:8px}
.card p{color:var(--soft);font-size:15px;margin-bottom:14px}
.tech{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.tech span{font-family:var(--mono);font-size:12px;padding:4px 8px;border-radius:6px;background:color-mix(in srgb,var(--accent) 14%,transparent);color:var(--accent)}
.card-links{display:flex;gap:14px;font-weight:700;color:var(--accent)}

.timeline{list-style:none;position:relative;padding-left:28px}
.timeline::before{content:"";position:absolute;left:7px;top:6px;bottom:6px;width:2px;background:var(--line)}
.timeline li{position:relative;padding:0 0 26px 18px}
.t-dot{position:absolute;left:-25px;top:6px;width:14px;height:14px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 25%,transparent)}
.t-head{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.t-period{font-family:var(--mono);font-size:13px;color:var(--soft)}
.t-sub{color:var(--accent);font-weight:600;margin:2px 0 6px}
.t-body p{color:var(--soft);font-size:15px}

.contact-card{display:grid;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;max-width:560px}
.contact-row{display:flex;justify-content:space-between;padding:18px 22px;border-bottom:1px solid var(--line);font-weight:600}
.contact-row:last-child{border-bottom:0}
.contact-row span{color:var(--soft);font-weight:600}
.contact-row:hover{background:color-mix(in srgb,var(--accent) 8%,transparent)}

.footer{text-align:center;padding:40px 24px;color:var(--soft);border-top:1px solid var(--line);font-size:14px}

.reveal{opacity:0;transform:translateY(16px);transition:opacity .6s,transform .6s}
.reveal.in{opacity:1;transform:none}

/* ---- theme: neon ---- */
body.theme-neon{--bg:#07060f}
body.theme-neon .display{text-shadow:0 0 28px color-mix(in srgb,var(--accent) 60%,transparent)}
body.theme-neon .card:hover{box-shadow:0 0 0 1px var(--accent),0 18px 50px -20px var(--accent)}
body.theme-neon .nav{background:rgba(7,6,15,.65)}

/* ---- theme: minimal ---- */
body.theme-minimal{--bg:#ffffff;--ink:#0b0b0c;--soft:#6b7280;--card:#fafafa;--line:#ececf0}
body.theme-minimal .avatar{border-radius:50%}
body.theme-minimal .brand-badge,body.theme-minimal .btn-primary{border-radius:8px}
body.theme-minimal .card,body.theme-minimal .skill{border-radius:10px}
body.theme-minimal .display{font-weight:700}

/* ---- theme: terminal ---- */
body.theme-terminal{--bg:#0b1021;--ink:#d7e0ff;--soft:#7c87b8;--card:#11182f;--font:var(--mono)}
body.theme-terminal h1,body.theme-terminal h2,body.theme-terminal h3,body.theme-terminal .display{font-family:var(--mono)}
body.theme-terminal .kicker::before{content:"$ "}
body.theme-terminal .role::before{content:"> ";color:var(--soft)}
body.theme-terminal .card,body.theme-terminal .skill,body.theme-terminal .contact-card{border-radius:6px}
body.theme-terminal .section-title span{border-radius:4px}
body.theme-terminal .avatar{border-radius:8px}
"""


# --------------------------------------------------------------------------- #
# JS
# --------------------------------------------------------------------------- #
def render_script_js(data) -> str:
    return _BASE_JS


_BASE_JS = r"""
// year
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// localStorage is unavailable in a sandboxed iframe (live preview) and in some
// private-browsing modes; guard every access so the rest of the script runs.
const store = {
  get(k){ try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v){ try { localStorage.setItem(k, v); } catch {} },
};

// theme toggle (persists when storage is available)
const toggle = document.getElementById('themeToggle');
const KEY = 'pf-mode';
if (store.get(KEY) === 'light') document.body.classList.add('light');
toggle && toggle.addEventListener('click', () => {
  document.body.classList.toggle('light');
  store.set(KEY, document.body.classList.contains('light') ? 'light' : 'dark');
});

// scroll reveal
const io = new IntersectionObserver((entries) => {
  entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach(el => io.observe(el));

// typed effect on role
const typed = document.getElementById('typed');
if (typed) {
  const full = typed.dataset.text || typed.textContent;
  typed.textContent = '';
  let i = 0;
  (function type(){
    if (i <= full.length) { typed.textContent = full.slice(0, i++); setTimeout(type, 55); }
    else { typed.style.borderRight = 'none'; }
  })();
}
"""


# --------------------------------------------------------------------------- #
# HTML documents
# --------------------------------------------------------------------------- #
def _doc(data, head_extra, css_link, js_link):
    name = e(data.get("fullName") or "Portfolio")
    title = e(data.get("title") or "")
    desc = e((data.get("tagline") or data.get("about") or "Personal portfolio")[:160])
    body_class = f"theme-{theme_of(data)}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{name} — {title}</title>
  <meta name="description" content="{desc}" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  {head_extra}
  {css_link}
</head>
<body class="{body_class}">
{_body(data)}
{js_link}
</body>
</html>"""


def render_index_html(data) -> str:
    return _doc(
        data,
        head_extra="",
        css_link='<link rel="stylesheet" href="styles.css" />',
        js_link='<script src="script.js"></script>',
    )


def render_preview_html(data) -> str:
    """Single self-contained file for an <iframe srcdoc>.

    The preview iframe is sandboxed (allow-scripts only), so the scroll-reveal
    observer can't always run and the page is shown inside a fixed frame — both
    of which would otherwise leave `.reveal` sections (projects, experience,
    education) stuck invisible. We neutralise the reveal animation here so the
    full portfolio is always visible in the preview. The generated site keeps
    the real scroll animation.
    """
    reveal_override = ".reveal{opacity:1 !important;transform:none !important}"
    css = f"<style>{render_styles_css(data)}{reveal_override}</style>"
    js = f"<script>{render_script_js(data)}</script>"
    return _doc(data, head_extra=css, css_link="", js_link=js)
