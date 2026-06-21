import React from "react";
import { motion } from "framer-motion";

export default function ScorePanel({ score }) {
  if (!score) return null;
  const { score: pct, grade, breakdown = [], suggestions = [] } = score;
  const hue = pct >= 80 ? 152 : pct >= 60 ? 45 : 0;
  const color = `hsl(${hue} 80% 45%)`;
  const circ = 2 * Math.PI * 52;

  return (
    <div className="score-panel">
      <div className="score-head">
        <svg width="132" height="132" viewBox="0 0 132 132" className="ring">
          <circle cx="66" cy="66" r="52" className="ring-bg" />
          <motion.circle
            cx="66"
            cy="66"
            r="52"
            className="ring-fg"
            stroke={color}
            strokeDasharray={circ}
            initial={{ strokeDashoffset: circ }}
            animate={{ strokeDashoffset: circ - (circ * pct) / 100 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
          <text x="66" y="60" className="ring-num">{pct}</text>
          <text x="66" y="82" className="ring-sub">/ 100</text>
        </svg>
        <div>
          <span className="grade" style={{ color }}>{grade}</span>
          <p className="muted">Completeness score</p>
        </div>
      </div>

      <ul className="checklist">
        {breakdown.map((b) => (
          <li key={b.label} className={b.ok ? "ok" : "miss"}>
            <span className="tick">{b.ok ? "✓" : "○"}</span>
            {b.label}
            <em>{b.points}/{b.max}</em>
          </li>
        ))}
      </ul>

      {suggestions.length > 0 && (
        <div className="suggestions">
          <h4>💡 To improve</h4>
          <ul>
            {suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
