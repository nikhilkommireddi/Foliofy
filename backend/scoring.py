"""
scoring.py — rates how complete / hireable a portfolio is and returns
actionable suggestions. Pure heuristics, no external services.
"""

from __future__ import annotations


def _list(data, key):
    val = data.get(key)
    return val if isinstance(val, list) else []


def _txt(data, key):
    return (data.get(key) or "").strip()


def score_portfolio(data: dict) -> dict:
    """Return {score, grade, breakdown:[{label,points,max,ok}], suggestions:[..]}."""
    breakdown = []
    suggestions = []

    def check(label, ok, points, max_pts, tip=None):
        breakdown.append(
            {"label": label, "points": points if ok else 0, "max": max_pts, "ok": bool(ok)}
        )
        if not ok and tip:
            suggestions.append(tip)

    name = _txt(data, "fullName")
    title = _txt(data, "title")
    tagline = _txt(data, "tagline")
    about = _txt(data, "about")
    email = _txt(data, "email")
    location = _txt(data, "location")
    avatar = _txt(data, "avatarUrl")
    socials = _list(data, "socials")
    skills = _list(data, "skills")
    projects = _list(data, "projects")
    experience = _list(data, "experience")
    education = _list(data, "education")

    check("Name", bool(name), 5, 5, "Add your full name.")
    check("Professional title", bool(title), 5, 5, "Add a title like 'Full-Stack Developer'.")
    check("Tagline", bool(tagline), 4, 4, "A short one-line tagline makes a strong first impression.")
    check("About (120+ chars)", len(about) >= 120, 10, 10,
          "Expand your About section to at least a couple of sentences.")
    check("Email", bool(email), 5, 5, "Add a contact email so recruiters can reach you.")
    check("Location", bool(location), 3, 3, "Add your city/region.")
    check("Avatar / photo", bool(avatar), 4, 4, "Add an avatar image URL for a personal touch.")
    check("2+ social links", len(socials) >= 2, 8, 8,
          "Link at least two profiles (GitHub, LinkedIn, etc.).")
    check("5+ skills", len(skills) >= 5, 10, 10, "List at least 5 skills.")

    # projects: presence + quality
    proj_ok = len(projects) >= 2
    check("2+ projects", proj_ok, 12, 12, "Showcase at least 2 projects.")
    detailed = sum(
        1 for p in projects
        if (p.get("description") or "").strip() and (p.get("tech") or []) and (p.get("link") or p.get("repo"))
    )
    rich_ok = detailed >= 2
    check("Projects have detail + links", rich_ok, 12, 12,
          "Give projects a description, tech tags and a live/repo link.")

    check("Experience", len(experience) >= 1, 12, 12, "Add at least one work/experience entry.")
    check("Education", len(education) >= 1, 8, 8, "Add an education entry.")

    website_ok = bool(_txt(data, "website")) or any(s.get("url") for s in socials)
    check("Web presence", website_ok, 2, 2, "Add a website or live links.")

    score = sum(b["points"] for b in breakdown)
    max_score = sum(b["max"] for b in breakdown)
    pct = round(score / max_score * 100) if max_score else 0

    if pct >= 90:
        grade = "A+"
    elif pct >= 80:
        grade = "A"
    elif pct >= 70:
        grade = "B"
    elif pct >= 55:
        grade = "C"
    else:
        grade = "D"

    return {
        "score": pct,
        "grade": grade,
        "breakdown": breakdown,
        "suggestions": suggestions[:6],
    }
