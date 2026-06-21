import React from "react";
import { AnimatePresence, motion } from "framer-motion";
import { api } from "../api";

export default function History({ items, stats, onLoad, onDelete }) {
  return (
    <div className="history">
      <div className="history-stats">
        <Stat label="Generated" value={stats?.total ?? 0} />
        <Stat label="Avg score" value={stats?.avg_score ?? 0} />
        <Stat label="Best" value={stats?.best ?? 0} />
      </div>

      {(!items || items.length === 0) && (
        <p className="muted empty">No portfolios yet — generate your first one!</p>
      )}

      <AnimatePresence initial={false}>
        {items?.map((it) => (
          <motion.div
            key={it.id}
            className="history-row"
            layout
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 8 }}
          >
            <div className="history-main">
              <strong>{it.full_name || "Untitled"}</strong>
              <span className="muted">{it.title}</span>
            </div>
            <span className={`pill theme-${it.theme}`}>{it.theme}</span>
            <span className="pill score">{it.score} · {it.grade}</span>
            <div className="history-actions">
              <button onClick={() => onLoad(it.id)} title="Load into editor">Edit</button>
              <a className="btn-mini" href={api.downloadUrl(it.id)}>ZIP</a>
              <button className="danger" onClick={() => onDelete(it.id)} title="Delete">✕</button>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}
