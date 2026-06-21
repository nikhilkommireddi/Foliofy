import React, { useState } from "react";

const DEVICES = {
  desktop: { w: "100%", label: "🖥 Desktop" },
  tablet: { w: "768px", label: "📱 Tablet" },
  mobile: { w: "390px", label: "📲 Mobile" },
};

export default function LivePreview({ html, loading }) {
  const [device, setDevice] = useState("desktop");

  return (
    <div className="preview">
      <div className="preview-bar">
        <div className="dots"><span /><span /><span /></div>
        <div className="device-switch">
          {Object.entries(DEVICES).map(([k, d]) => (
            <button
              key={k}
              className={device === k ? "active" : ""}
              onClick={() => setDevice(k)}
              title={d.label}
            >
              {d.label.split(" ")[0]}
            </button>
          ))}
        </div>
        {loading && <span className="preview-loading">updating…</span>}
      </div>
      <div className="preview-stage">
        <iframe
          title="Portfolio preview"
          srcDoc={html || "<p style='font-family:sans-serif;padding:40px;color:#888'>Start filling the form to see your portfolio…</p>"}
          style={{ width: DEVICES[device].w }}
          sandbox="allow-scripts"
        />
      </div>
    </div>
  );
}
