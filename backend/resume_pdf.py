"""
resume_pdf.py — render a clean one/two-page PDF résumé from portfolio data.

Uses fpdf2 if installed. Returns PDF bytes, or None if the library is missing
(the generator then falls back to bundling a printable resume.html instead).
"""

from __future__ import annotations


def _list(data, key):
    val = data.get(key)
    return val if isinstance(val, list) else []


def _ascii(text) -> str:
    """fpdf core fonts are latin-1; drop anything they can't encode."""
    return ("" if text is None else str(text)).encode("latin-1", "ignore").decode("latin-1")


def build_resume_pdf(data: dict):
    try:
        from fpdf import FPDF
    except Exception:
        return None

    accent = (data.get("accent") or "#6d5efc").lstrip("#")
    try:
        r, g, b = int(accent[0:2], 16), int(accent[2:4], 16), int(accent[4:6], 16)
    except Exception:
        r, g, b = 109, 94, 252

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_margins(16, 16, 16)

    # Header
    pdf.set_text_color(r, g, b)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 11, _ascii(data.get("fullName") or "Your Name"), ln=True)
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 7, _ascii(data.get("title") or ""), ln=True)

    contact_bits = [
        data.get("email"), data.get("phone"), data.get("location"), data.get("website")
    ]
    contact = "  |  ".join(_ascii(c) for c in contact_bits if c)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(110, 110, 110)
    if contact:
        pdf.cell(0, 6, contact, ln=True)
    pdf.ln(2)

    def heading(text):
        pdf.ln(2)
        pdf.set_text_color(r, g, b)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, _ascii(text).upper(), ln=True)
        y = pdf.get_y()
        pdf.set_draw_color(r, g, b)
        pdf.line(16, y, 196, y)
        pdf.ln(2)
        pdf.set_text_color(40, 40, 40)

    def body(text, size=10):
        pdf.set_font("Helvetica", "", size)
        # Pin x to the left margin and use the full page width. Passing width 0
        # ("to right margin") can yield a near-zero width if the cursor drifted,
        # which makes wrapmode="CHAR" spin forever on long tokens (e.g. URLs).
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(pdf.epw, 5, _ascii(text), wrapmode="CHAR")

    about = (data.get("about") or "").strip()
    if about:
        heading("Summary")
        body(about)

    skills = _list(data, "skills")
    if skills:
        heading("Skills")
        body(", ".join(_ascii(s) for s in skills))

    experience = _list(data, "experience")
    if experience:
        heading("Experience")
        for it in experience:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, _ascii(f"{it.get('role','')} — {it.get('company','')}"), ln=True)
            if it.get("period"):
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(120, 120, 120)
                pdf.cell(0, 5, _ascii(it.get("period")), ln=True)
                pdf.set_text_color(40, 40, 40)
            if it.get("description"):
                body(it.get("description"))
            pdf.ln(1)

    projects = _list(data, "projects")
    if projects:
        heading("Projects")
        for p in projects:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, _ascii(p.get("name", "")), ln=True)
            if p.get("description"):
                body(p.get("description"))
            extra = []
            if p.get("tech"):
                extra.append("Tech: " + ", ".join(_ascii(t) for t in p.get("tech")))
            if p.get("link"):
                extra.append("Link: " + _ascii(p.get("link")))
            if extra:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(120, 120, 120)
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(pdf.epw, 5, "  |  ".join(extra), wrapmode="CHAR")
                pdf.set_text_color(40, 40, 40)
            pdf.ln(1)

    education = _list(data, "education")
    if education:
        heading("Education")
        for it in education:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, _ascii(f"{it.get('degree','')} — {it.get('school','')}"), ln=True)
            if it.get("period"):
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(120, 120, 120)
                pdf.cell(0, 5, _ascii(it.get("period")), ln=True)
                pdf.set_text_color(40, 40, 40)

    out = pdf.output(dest="S")
    # fpdf2 returns bytearray; older returns str
    if isinstance(out, str):
        return out.encode("latin-1")
    return bytes(out)
