import React from "react";

const THEMES = [
  { id: "aurora", name: "Aurora", swatch: "#6d5efc", note: "Soft gradients, playful" },
  { id: "neon", name: "Neon", swatch: "#13f1c4", note: "Dark, glowing, bold" },
  { id: "minimal", name: "Minimal", swatch: "#111827", note: "Clean, editorial" },
  { id: "terminal", name: "Terminal", swatch: "#33ff8a", note: "Monospace hacker vibe" },
];

const ACCENTS = ["#6d5efc", "#13f1c4", "#ff5fa2", "#f5a623", "#33ff8a", "#3b82f6", "#ef4444"];

export default function ThemePicker({ theme, accent, onTheme, onAccent }) {
  return (
    <div className="theme-picker">
      <div className="theme-grid">
        {THEMES.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`theme-card ${theme === t.id ? "active" : ""}`}
            onClick={() => onTheme(t.id)}
          >
            <span className="theme-dot" style={{ background: t.swatch }} />
            <strong>{t.name}</strong>
            <small>{t.note}</small>
          </button>
        ))}
      </div>

      <div className="accent-row">
        <span className="field-label">Accent colour</span>
        <div className="accent-swatches">
          {ACCENTS.map((c) => (
            <button
              key={c}
              type="button"
              className={`accent ${accent === c ? "active" : ""}`}
              style={{ background: c }}
              onClick={() => onAccent(c)}
              aria-label={c}
            />
          ))}
          <input
            type="color"
            value={accent || "#6d5efc"}
            onChange={(e) => onAccent(e.target.value)}
            className="accent-custom"
            aria-label="Custom accent"
          />
        </div>
      </div>
    </div>
  );
}
