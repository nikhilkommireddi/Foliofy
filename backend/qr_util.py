"""
qr_util.py — build an SVG QR code for the portfolio's primary link.

Uses the `qrcode` library if available; otherwise returns a clearly-labelled
placeholder SVG so the rest of the pipeline keeps working.
"""

from __future__ import annotations

import html


def primary_link(data: dict) -> str:
    """Best link to encode: website > first social url > mailto."""
    website = (data.get("website") or "").strip()
    if website:
        return website
    for s in data.get("socials") or []:
        if s.get("url"):
            return s["url"].strip()
    email = (data.get("email") or "").strip()
    if email:
        return f"mailto:{email}"
    return "https://example.com"


def make_qr_svg(link: str) -> str:
    """Return an SVG string encoding `link`."""
    try:
        import qrcode
        import qrcode.image.svg as svg

        factory = svg.SvgPathImage
        img = qrcode.make(link, image_factory=factory, box_size=12, border=2)
        # qrcode returns a BytesIO-writable image; render to string
        import io

        buf = io.BytesIO()
        img.save(buf)
        return buf.getvalue().decode("utf-8")
    except Exception:
        safe = html.escape(link)
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" width="240" height="260" '
            'viewBox="0 0 240 260" role="img">'
            '<rect width="240" height="260" fill="#0e0f1a"/>'
            '<rect x="20" y="20" width="200" height="200" fill="none" '
            'stroke="#6d5efc" stroke-width="3" rx="12"/>'
            '<text x="120" y="120" fill="#a6abce" font-family="monospace" '
            'font-size="12" text-anchor="middle">QR unavailable</text>'
            f'<text x="120" y="245" fill="#6d5efc" font-family="monospace" '
            f'font-size="9" text-anchor="middle">{safe[:34]}</text>'
            "</svg>"
        )
