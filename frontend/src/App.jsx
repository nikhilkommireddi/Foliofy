import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { api } from "./api";
import { Input, TextArea, TagInput } from "./components/Field";
import RepeatList from "./components/RepeatList";
import ThemePicker from "./components/ThemePicker";
import ScorePanel from "./components/ScorePanel";
import LivePreview from "./components/LivePreview";
import History from "./components/History";

const STORAGE_KEY = "foliofy-draft";

const SAMPLE = {
  fullName: "Ada Lovelace",
  title: "Full-Stack Engineer",
  tagline: "I build delightful, fast web apps — and the occasional analytical engine.",
  email: "ada@example.com",
  phone: "",
  location: "London, UK",
  website: "https://ada.dev",
  avatarUrl: "",
  about:
    "Engineer with a love for clean abstractions and pixel-perfect interfaces. I’ve shipped products end-to-end, from database schema to design system, and I care deeply about developer experience and accessibility.",
  socials: [
    { label: "GitHub", url: "https://github.com/ada" },
    { label: "LinkedIn", url: "https://linkedin.com/in/ada" },
  ],
  skills: ["React", "TypeScript", "Python", "Node.js", "PostgreSQL", "Docker"],
  projects: [
    {
      name: "Analytical Engine UI",
      description: "A visual programming environment for sequencing operations, with live simulation.",
      tech: ["React", "WebGL", "Zustand"],
      link: "https://ada.dev/engine",
      repo: "https://github.com/ada/engine",
    },
  ],
  experience: [
    {
      role: "Senior Engineer",
      company: "Babbage & Co.",
      period: "2022 — Present",
      description: "Led the frontend platform team and rebuilt the design system.",
    },
  ],
  education: [
    { degree: "B.Sc. Mathematics", school: "University of London", period: "2016 — 2019" },
  ],
  theme: "aurora",
  accent: "#6d5efc",
};

const EMPTY = {
  fullName: "", title: "", tagline: "", email: "", phone: "", location: "",
  website: "", avatarUrl: "", about: "", socials: [], skills: [],
  projects: [], experience: [], education: [], theme: "aurora", accent: "#6d5efc",
};

const STEPS = ["Basics", "About & Skills", "Projects", "Experience", "Design", "Generate"];

function loadDraft() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return { ...EMPTY, ...JSON.parse(raw) };
  } catch {}
  return null;
}

export default function App() {
  const [data, setData] = useState(() => loadDraft() || SAMPLE);
  const [step, setStep] = useState(0);
  const [preview, setPreview] = useState({ html: "" });
  const [score, setScore] = useState(null);
  const [previewing, setPreviewing] = useState(false);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [features, setFeatures] = useState({ pdf: true, qr: true });

  const set = useCallback((patch) => setData((d) => ({ ...d, ...patch })), []);

  // persist draft
  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); } catch {}
  }, [data]);

  // health + history on mount
  useEffect(() => {
    api.health().then((h) => setFeatures(h.features || {})).catch(() => {});
    refreshHistory();
  }, []);

  const refreshHistory = useCallback(() => {
    api.history().then(setHistory).catch(() => {});
    api.stats().then(setStats).catch(() => {});
  }, []);

  // debounced live preview whenever data changes
  const debounce = useRef();
  useEffect(() => {
    setPreviewing(true);
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => {
      api
        .preview(data)
        .then((res) => {
          setPreview(res);
          setScore(res.score);
        })
        .catch(() => {})
        .finally(() => setPreviewing(false));
    }, 450);
    return () => clearTimeout(debounce.current);
  }, [data]);

  const generate = async () => {
    setBusy(true);
    setError("");
    setResult(null);
    try {
      const res = await api.generate(data);
      setResult(res);
      refreshHistory();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const loadFromHistory = async (id) => {
    try {
      const item = await api.historyItem(id);
      setData({ ...EMPTY, ...item.data });
      setStep(0);
      setResult(null);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e.message);
    }
  };

  const deleteFromHistory = async (id) => {
    await api.deleteItem(id).catch(() => {});
    refreshHistory();
  };

  return (
    <div className="app">
      <Background />
      <header className="topbar">
        <div className="logo">
          <span className="logo-mark">P</span>
          <div>
            <strong>Foliofy</strong>
            <small>fill it in · preview live · download a deploy-ready ZIP</small>
          </div>
        </div>
        <div className="topbar-actions">
          <button className="ghost" onClick={() => setData(SAMPLE)}>Load sample</button>
          <button className="ghost" onClick={() => { setData(EMPTY); setStep(0); }}>Clear</button>
        </div>
      </header>

      <main className="layout">
        {/* ---------------- editor ---------------- */}
        <section className="editor card">
          <Stepper step={step} setStep={setStep} />

          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.22 }}
            >
              {step === 0 && <StepBasics data={data} set={set} />}
              {step === 1 && <StepAbout data={data} set={set} />}
              {step === 2 && <StepProjects data={data} set={set} />}
              {step === 3 && <StepHistorySections data={data} set={set} />}
              {step === 4 && (
                <div className="step">
                  <h2 className="step-title">Design</h2>
                  <p className="step-sub">Pick a theme and accent. The preview updates instantly.</p>
                  <ThemePicker
                    theme={data.theme}
                    accent={data.accent}
                    onTheme={(theme) => set({ theme })}
                    onAccent={(accent) => set({ accent })}
                  />
                </div>
              )}
              {step === 5 && (
                <StepGenerate
                  data={data}
                  busy={busy}
                  result={result}
                  error={error}
                  features={features}
                  onGenerate={generate}
                />
              )}
            </motion.div>
          </AnimatePresence>

          <div className="nav-buttons">
            <button className="ghost" disabled={step === 0} onClick={() => setStep((s) => s - 1)}>
              ← Back
            </button>
            {step < STEPS.length - 1 ? (
              <button className="primary" onClick={() => setStep((s) => s + 1)}>
                Next: {STEPS[step + 1]} →
              </button>
            ) : (
              <button className="primary" disabled={busy} onClick={generate}>
                {busy ? "Generating…" : "⚡ Generate ZIP"}
              </button>
            )}
          </div>
        </section>

        {/* ---------------- right rail ---------------- */}
        <aside className="rail">
          <LivePreview html={preview.html} loading={previewing} />
          <div className="card">
            <ScorePanel score={score} />
          </div>
        </aside>
      </main>

      <section className="history-wrap card">
        <h2 className="step-title">Your generated portfolios</h2>
        <History
          items={history}
          stats={stats}
          onLoad={loadFromHistory}
          onDelete={deleteFromHistory}
        />
      </section>

      <footer className="page-footer">
        <span>Foliofy · React + Flask + SQLite</span>
      </footer>
    </div>
  );
}

/* ----------------------------- steps ----------------------------- */
function StepBasics({ data, set }) {
  return (
    <div className="step">
      <h2 className="step-title">The basics</h2>
      <p className="step-sub">Who are you and how can people reach you?</p>
      <div className="grid-2">
        <Input label="Full name" value={data.fullName} onChange={(v) => set({ fullName: v })} placeholder="Ada Lovelace" />
        <Input label="Professional title" value={data.title} onChange={(v) => set({ title: v })} placeholder="Full-Stack Engineer" />
      </div>
      <Input label="Tagline" value={data.tagline} onChange={(v) => set({ tagline: v })} placeholder="One punchy line about you" hint="shows under your name" />
      <div className="grid-2">
        <Input label="Email" type="email" value={data.email} onChange={(v) => set({ email: v })} placeholder="you@example.com" />
        <Input label="Phone" value={data.phone} onChange={(v) => set({ phone: v })} placeholder="optional" />
      </div>
      <div className="grid-2">
        <Input label="Location" value={data.location} onChange={(v) => set({ location: v })} placeholder="City, Country" />
        <Input label="Website" value={data.website} onChange={(v) => set({ website: v })} placeholder="https://…" />
      </div>
      <Input label="Avatar image URL" value={data.avatarUrl} onChange={(v) => set({ avatarUrl: v })} placeholder="https://… (optional)" hint="square image works best" />

      <h3 className="sub-head">Social links</h3>
      <RepeatList
        items={data.socials}
        onChange={(socials) => set({ socials })}
        emptyItem={{ label: "", url: "" }}
        addLabel="Add link"
        render={(item, update) => (
          <div className="grid-2">
            <Input label="Label" value={item.label} onChange={(v) => update({ label: v })} placeholder="GitHub" />
            <Input label="URL" value={item.url} onChange={(v) => update({ url: v })} placeholder="https://github.com/you" />
          </div>
        )}
      />
    </div>
  );
}

function StepAbout({ data, set }) {
  return (
    <div className="step">
      <h2 className="step-title">About & skills</h2>
      <p className="step-sub">Tell your story and list what you're good at.</p>
      <TextArea
        label="About"
        rows={6}
        value={data.about}
        onChange={(v) => set({ about: v })}
        placeholder="A few sentences about your experience, focus and what you enjoy building…"
        hint="aim for 120+ characters"
      />
      <TagInput
        label="Skills"
        value={data.skills}
        onChange={(skills) => set({ skills })}
        placeholder="Type a skill and press Enter (comma to add several)"
        hint="5+ recommended"
      />
    </div>
  );
}

function StepProjects({ data, set }) {
  return (
    <div className="step">
      <h2 className="step-title">Projects</h2>
      <p className="step-sub">Your best work. Each becomes a card on the site.</p>
      <RepeatList
        items={data.projects}
        onChange={(projects) => set({ projects })}
        emptyItem={{ name: "", description: "", tech: [], link: "", repo: "" }}
        addLabel="Add project"
        render={(item, update) => (
          <>
            <Input label="Name" value={item.name} onChange={(v) => update({ name: v })} placeholder="Project name" />
            <TextArea label="Description" rows={2} value={item.description} onChange={(v) => update({ description: v })} placeholder="What it does and why it's cool" />
            <TagInput label="Tech" value={item.tech} onChange={(tech) => update({ tech })} placeholder="React, Node…" />
            <div className="grid-2">
              <Input label="Live link" value={item.link} onChange={(v) => update({ link: v })} placeholder="https://…" />
              <Input label="Repo" value={item.repo} onChange={(v) => update({ repo: v })} placeholder="https://github.com/…" />
            </div>
          </>
        )}
      />
    </div>
  );
}

function StepHistorySections({ data, set }) {
  return (
    <div className="step">
      <h2 className="step-title">Experience & education</h2>
      <p className="step-sub">Your timeline. Drag order with the arrows.</p>

      <h3 className="sub-head">Experience</h3>
      <RepeatList
        items={data.experience}
        onChange={(experience) => set({ experience })}
        emptyItem={{ role: "", company: "", period: "", description: "" }}
        addLabel="Add role"
        render={(item, update) => (
          <>
            <div className="grid-2">
              <Input label="Role" value={item.role} onChange={(v) => update({ role: v })} placeholder="Senior Engineer" />
              <Input label="Company" value={item.company} onChange={(v) => update({ company: v })} placeholder="Company" />
            </div>
            <Input label="Period" value={item.period} onChange={(v) => update({ period: v })} placeholder="2022 — Present" />
            <TextArea label="Description" rows={2} value={item.description} onChange={(v) => update({ description: v })} placeholder="What you did / impact" />
          </>
        )}
      />

      <h3 className="sub-head">Education</h3>
      <RepeatList
        items={data.education}
        onChange={(education) => set({ education })}
        emptyItem={{ degree: "", school: "", period: "" }}
        addLabel="Add education"
        render={(item, update) => (
          <>
            <div className="grid-2">
              <Input label="Degree" value={item.degree} onChange={(v) => update({ degree: v })} placeholder="B.Sc. Computer Science" />
              <Input label="School" value={item.school} onChange={(v) => update({ school: v })} placeholder="University" />
            </div>
            <Input label="Period" value={item.period} onChange={(v) => update({ period: v })} placeholder="2016 — 2019" />
          </>
        )}
      />
    </div>
  );
}

function StepGenerate({ data, busy, result, error, features, onGenerate }) {
  return (
    <div className="step">
      <h2 className="step-title">Generate</h2>
      <p className="step-sub">
        Build a complete, deploy-ready project for <strong>{data.fullName || "you"}</strong>.
      </p>

      <ul className="bundle-list">
        <li>✅ Responsive website (<code>index.html</code>, <code>styles.css</code>, <code>script.js</code>)</li>
        <li>{features.pdf ? "✅" : "⚠️"} {features.pdf ? "PDF résumé (resume.pdf)" : "Printable résumé (resume.html — install fpdf2 for PDF)"}</li>
        <li>{features.qr ? "✅" : "⚠️"} QR code (assets/qr.svg)</li>
        <li>✅ Proper README, MIT license, data.json</li>
        <li>✅ Deploy kit: GitHub Pages, Netlify, Vercel, Docker</li>
      </ul>

      {error && <div className="alert error">{error}</div>}

      {result && (
        <motion.div className="result" initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}>
          <div className="result-top">
            <span className="result-emoji">🎉</span>
            <div>
              <strong>Your portfolio is ready!</strong>
              <p className="muted">
                {result.filename} · {(result.size_bytes / 1024).toFixed(1)} KB · score {result.score.score} ({result.score.grade})
              </p>
            </div>
          </div>
          <a className="primary big" href={api.downloadUrl(result.id)}>⬇ Download ZIP</a>
        </motion.div>
      )}

      {!result && (
        <button className="primary big" disabled={busy} onClick={onGenerate}>
          {busy ? "Generating…" : "⚡ Generate my portfolio"}
        </button>
      )}
    </div>
  );
}

/* ----------------------------- stepper ----------------------------- */
function Stepper({ step, setStep }) {
  return (
    <div className="stepper">
      {STEPS.map((label, i) => (
        <button
          key={label}
          className={`step-pill ${i === step ? "active" : ""} ${i < step ? "done" : ""}`}
          onClick={() => setStep(i)}
        >
          <span className="step-num">{i < step ? "✓" : i + 1}</span>
          <span className="step-name">{label}</span>
        </button>
      ))}
    </div>
  );
}

function Background() {
  return (
    <div className="bg" aria-hidden>
      <div className="blob b1" />
      <div className="blob b2" />
      <div className="blob b3" />
      <div className="grid" />
    </div>
  );
}
