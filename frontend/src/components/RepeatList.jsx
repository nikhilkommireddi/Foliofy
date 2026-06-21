import React from "react";
import { AnimatePresence, motion } from "framer-motion";

// Generic repeatable section: projects, experience, education, socials.
// `fields` describes the inputs; `render` draws one row.
export default function RepeatList({ items = [], onChange, emptyItem, render, addLabel }) {
  const update = (i, patch) =>
    onChange(items.map((it, j) => (j === i ? { ...it, ...patch } : it)));
  const remove = (i) => onChange(items.filter((_, j) => j !== i));
  const add = () => onChange([...items, { ...emptyItem }]);
  const move = (i, dir) => {
    const j = i + dir;
    if (j < 0 || j >= items.length) return;
    const next = items.slice();
    [next[i], next[j]] = [next[j], next[i]];
    onChange(next);
  };

  return (
    <div className="repeat">
      <AnimatePresence initial={false}>
        {items.map((item, i) => (
          <motion.div
            key={i}
            className="repeat-item"
            layout
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.97 }}
          >
            <div className="repeat-head">
              <span className="repeat-index">#{i + 1}</span>
              <div className="repeat-tools">
                <button type="button" onClick={() => move(i, -1)} disabled={i === 0}>↑</button>
                <button type="button" onClick={() => move(i, 1)} disabled={i === items.length - 1}>↓</button>
                <button type="button" className="danger" onClick={() => remove(i)}>Remove</button>
              </div>
            </div>
            {render(item, (patch) => update(i, patch))}
          </motion.div>
        ))}
      </AnimatePresence>
      <button type="button" className="add-btn" onClick={add}>
        + {addLabel}
      </button>
    </div>
  );
}
