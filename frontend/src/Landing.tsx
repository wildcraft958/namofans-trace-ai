import { Link, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";

const CODE = `def analyze_fund_flow(g, account_id, threshold=0.82):
    pattern = pattern_matcher.score(g, account_id)
    anomaly  = online_scorer.predict(account_id)
    if pattern["score"] > threshold:
        raise SuspiciousActivity(
            ring=pattern["matches"], score=pattern["score"]
        )
    audit_log.record(account_id, pattern, anomaly)
    return risk_fusion.fuse(pattern=pattern, anomaly=anomaly)`;

const FEATURES = [
  {
    icon: "⬡",
    title: "5 Fraud Pattern Detectors",
    desc: "Circular flow, layering chains, structuring clusters, mule fan-in/fan-out, dormant burst — all running on live NetworkX graphs.",
    accent: "#f97316",
  },
  {
    icon: "📄",
    title: "Auto-STR Generation",
    desc: "FIU-IND compliant 8-section Suspicious Transaction Reports generated in one click via ReportLab. 4–6 hours reduced to 5 minutes.",
    accent: "#22c55e",
  },
  {
    icon: "⚡",
    title: "SHAP Explainability",
    desc: "TreeExplainer on XGBoost surfaces the top-5 graph features driving every alert. Investigators see why, not just what.",
    accent: "#fb923c",
  },
  {
    icon: "〜",
    title: "Live Drift Detection",
    desc: "River HalfSpaceTrees + ADWIN detect distribution shifts in real time with <1ms latency. Eliminates model staleness automatically.",
    accent: "#f97316",
  },
  {
    icon: "💬",
    title: "NL Investigation Copilot",
    desc: "Ask questions in plain English — translated to graph queries returning instant visual highlights and risk scores. No Cypher or SQL needed.",
    accent: "#c084fc",
  },
  {
    icon: "🔥",
    title: "Hot-Reload Compliance Engine",
    desc: "YAML-defined CTR, KYC, and RBI rules update in real time without code changes or restarts. New rules take effect immediately.",
    accent: "#fb923c",
  },
];

const STATS = [
  { value: "₹71,543 Cr", label: "Annual bank fraud (RBI 2024-25)" },
  { value: "95%+", label: "False positive rate in rule-based systems" },
  { value: "AUC 0.70", label: "TGN on IBM AMLSim 20K-node graph" },
  { value: "<2 s", label: "Alert latency over WebSocket" },
];

const ARCH_LAYERS = [
  {
    label: "Layer 0 — Data Ingestion",
    color: "#f97316",
    items: ["CBS Feeds · NEFT/RTGS/UPI/IMPS · IBM AMLSim", "(sender, receiver, amount, timestamp, channel)"],
  },
  {
    label: "Layer 1 — Graph Engine",
    color: "#22c55e",
    items: ["NetworkX MultiDiGraph · Neo4j (production)", "Nodes = Accounts · Edges = Transactions"],
  },
  {
    label: "Layer 2 — Detection Engine",
    color: "#fb923c",
    items: [
      "A: Pattern Matcher (5 AML typologies)",
      "B: Temporal GNN — TGNMemory + TransformerConv (PyG 2.7)",
      "C: Online Anomaly Scorer — River HST + ADWIN",
      "D: Compliance Rule Engine (YAML, hot-reload)",
      "E: Risk Fusion — pattern(0.30) + GNN(0.30) + anomaly(0.20) + compliance(0.20)",
    ],
  },
  {
    label: "Layer 3 — Intelligence",
    color: "#c084fc",
    items: [
      "F: LLM Copilot (Gemini 2.5 Flash — NL→Graph Query)",
      "G: Auto-STR Generator (FIU-IND compliant PDF via ReportLab)",
      "H: GNN Explainer (gradient saliency — top-k contributing edges)",
    ],
  },
  {
    label: "Layer 4 — Delivery",
    color: "#7dd3fc",
    items: [
      "FastAPI (REST + WebSocket)",
      "React: 3D Force Graph · Alert Stream · Copilot Chat · KPI Dashboard · One-click STR Download",
    ],
  },
];

const TECH_STACK = [
  { layer: "Data", tech: "IBM AMLSim · Pandas · Faker" },
  { layer: "Graph Engine", tech: "NetworkX · Neo4j Community + GDS" },
  { layer: "GNN", tech: "PyTorch Geometric — TGNMemory + TransformerConv (ChronoWave-inspired)" },
  { layer: "Imbalance", tech: "GraphSMOTE · Focal Loss" },
  { layer: "Online ML", tech: "River — HalfSpaceTrees · ADWIN" },
  { layer: "Compliance", tech: "YAML rule engine (hot-reloadable)" },
  { layer: "LLM", tech: "Gemini 2.5 Flash (Google AI — NL copilot + STR)" },
  { layer: "NL→Query", tech: "Vanna.ai-inspired NL→Cypher/NetworkX" },
  { layer: "Reporting", tech: "ReportLab (FIU-IND STR PDFs)" },
  { layer: "Backend", tech: "FastAPI · WebSocket · SQLite" },
  { layer: "Frontend", tech: "React · react-force-graph-3d (Three.js)" },
  { layer: "Deploy", tech: "Docker Compose · Google Cloud Run" },
];

const TEAM = [
  {
    name: "Animesh Raj",
    role: "ML/AI & Graph Neural Networks",
    avatar: "AR",
    color: "#f97316",
    bio: "Leads temporal GNN architecture, graph pattern matching engine, and drift detection pipeline.",
  },
  {
    name: "Devansh Gupta",
    role: "Backend Engineering & System Design",
    avatar: "DG",
    color: "#22c55e",
    bio: "Owns FastAPI service layer, WebSocket streaming, Docker orchestration, and Cloud Run deployment.",
  },
  {
    name: "Prem Agarwal",
    role: "Full-Stack & Data Visualization",
    avatar: "PA",
    color: "#c084fc",
    bio: "Builds the React investigator dashboard — 3D force graph, KPI cards, real-time alert stream.",
  },
  {
    name: "MD. Faizan Khan",
    role: "NLP, LLMs & Compliance",
    avatar: "FK",
    color: "#fb923c",
    bio: "Develops the NL investigation copilot, LLM alert explainer, and auto-STR FIU-IND generation.",
  },
];

function CodeWindow() {
  const [typed, setTyped] = useState(0);
  const raf = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let i = 0;
    const tick = () => {
      i += 2;
      setTyped(i);
      if (i < CODE.length) raf.current = setTimeout(tick, 18);
    };
    raf.current = setTimeout(tick, 600);
    return () => { if (raf.current) clearTimeout(raf.current); };
  }, []);

  const partial = CODE.slice(0, typed);
  const lines = partial.split("\n");

  const highlight = (raw: string) =>
    raw
      .replace(/("[^"]*")/g, '\x00STR\x00$1\x00/STR\x00')
      .replace(/\b(def|if|return|raise)\b/g, '<span style="color:#fb923c">$1</span>')
      .replace(/\b(pattern_matcher|online_scorer|risk_fusion|audit_log)\b/g,
               '<span style="color:#c084fc">$1</span>')
      .replace(/\b(0\.\d+)\b/g, '<span style="color:#7dd3fc">$1</span>')
      .replace(/\x00STR\x00("[^"]*")\x00\/STR\x00/g, '<span style="color:#86efac">$1</span>');

  return (
    <div style={{
      background: "#111318",
      border: "1px solid #2a2e3a",
      borderRadius: 14,
      overflow: "hidden",
      boxShadow: "0 40px 80px -20px rgba(0,0,0,0.7), 0 0 120px rgba(249,115,22,0.12)",
      animation: "float 6s ease-in-out infinite",
    }}>
      <div style={{
        display: "flex", alignItems: "center", gap: 7,
        padding: "12px 18px", background: "#1a1d26",
        borderBottom: "1px solid #2a2e3a",
      }}>
        {["#ff5f56","#ffbd2e","#27c93f"].map((c) => (
          <div key={c} style={{ width: 12, height: 12, borderRadius: "50%", background: c }} />
        ))}
        <span style={{ marginLeft: 12, fontFamily: "monospace", fontSize: 12, color: "#6b7280" }}>
          trace_pipeline.py
        </span>
      </div>
      <div style={{
        padding: "20px 0",
        fontFamily: "'Fira Code', 'Menlo', 'Consolas', monospace",
        fontSize: 13,
        lineHeight: 1.75,
        minHeight: 240,
        overflowX: "auto",
      }}>
        {lines.map((line, idx) => {
          const isRed = idx === 3;
          return (
            <div key={idx} style={{
              display: "flex",
              background: isRed ? "rgba(239,68,68,0.14)" : "transparent",
              borderLeft: isRed ? "3px solid #ef4444" : "3px solid transparent",
              transition: "background 0.3s",
            }}>
              <span style={{
                width: 44, textAlign: "right", paddingRight: 16,
                color: isRed ? "#f87171" : "#3f4455",
                userSelect: "none", fontSize: 12,
              }}>{idx + 1}</span>
              <span
                style={{ paddingLeft: 4, whiteSpace: "pre", color: "#d1d5db" }}
                dangerouslySetInnerHTML={{ __html: highlight(line) }}
              />
              {idx === lines.length - 1 && typed < CODE.length && (
                <span style={{
                  display: "inline-block", width: 2, height: "1em",
                  background: "#f97316", verticalAlign: "text-bottom",
                  animation: "blink 1s step-end infinite",
                }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function DemoLoginModal({ onClose }: { onClose: () => void }) {
  const navigate = useNavigate();
  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 1000,
      background: "rgba(0,0,0,0.75)", backdropFilter: "blur(6px)",
      display: "flex", alignItems: "center", justifyContent: "center",
    }} onClick={onClose}>
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#16180f",
          border: "1px solid rgba(249,115,22,0.25)",
          borderRadius: 18, padding: "40px 44px", width: 380,
          boxShadow: "0 40px 80px rgba(0,0,0,0.6)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, #f97316, #dc2626)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontWeight: 900, fontSize: 16,
          }}>T</div>
          <span style={{ fontWeight: 800, fontSize: 16, color: "#f9fafb" }}>TRACE.ai</span>
        </div>
        <h3 style={{ fontWeight: 700, fontSize: 20, color: "#f9fafb", marginBottom: 4, marginTop: 16 }}>
          Sign in to your account
        </h3>
        <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 28 }}>
          Demo credentials pre-filled below.
        </p>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6, fontWeight: 600 }}>
            Email
          </label>
          <input
            defaultValue="demo@trace.ai"
            style={{
              width: "100%", padding: "10px 14px", borderRadius: 8,
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              color: "#f3f4f6", fontSize: 14, outline: "none",
            }}
          />
        </div>
        <div style={{ marginBottom: 28 }}>
          <label style={{ display: "block", fontSize: 12, color: "#9ca3af", marginBottom: 6, fontWeight: 600 }}>
            Password
          </label>
          <input
            type="password"
            defaultValue="demo1234"
            style={{
              width: "100%", padding: "10px 14px", borderRadius: 8,
              background: "rgba(255,255,255,0.06)",
              border: "1px solid rgba(255,255,255,0.12)",
              color: "#f3f4f6", fontSize: 14, outline: "none",
            }}
          />
        </div>

        <button
          onClick={() => navigate("/dashboard")}
          style={{
            width: "100%", padding: "13px", borderRadius: 8,
            background: "#f97316", color: "#fff", border: "none",
            fontWeight: 700, fontSize: 15, cursor: "pointer",
            boxShadow: "0 4px 20px rgba(249,115,22,0.4)",
            marginBottom: 12,
          }}
        >
          Sign In
        </button>
        <button
          onClick={() => navigate("/dashboard")}
          style={{
            width: "100%", padding: "13px", borderRadius: 8,
            background: "rgba(255,255,255,0.06)", color: "#e5e7eb",
            border: "1px solid rgba(255,255,255,0.14)",
            fontWeight: 600, fontSize: 14, cursor: "pointer",
          }}
        >
          Continue as Demo User
        </button>

        <p style={{ textAlign: "center", fontSize: 11, color: "#374151", marginTop: 20 }}>
          Hackathon demo — no real auth required
        </p>
      </div>
    </div>
  );
}

export default function Landing() {
  const [showLogin, setShowLogin] = useState(false);

  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <>
      {showLogin && <DemoLoginModal onClose={() => setShowLogin(false)} />}

      <style>{`
        html, body { margin: 0; padding: 0; background: #0c0700; }
        * { box-sizing: border-box; }
        @keyframes float {
          0%,100% { transform: translateY(0); }
          50%      { transform: translateY(-12px); }
        }
        @keyframes blink {
          0%,100% { opacity:1; } 50% { opacity:0; }
        }
        @keyframes fadeUp {
          from { opacity:0; transform:translateY(24px); }
          to   { opacity:1; transform:translateY(0); }
        }
        .fade-1 { animation: fadeUp 0.7s ease both; }
        .fade-2 { animation: fadeUp 0.7s 0.12s ease both; }
        .fade-3 { animation: fadeUp 0.7s 0.24s ease both; }
        .fade-4 { animation: fadeUp 0.7s 0.36s ease both; }
        .fade-5 { animation: fadeUp 0.7s 0.48s ease both; }
        .nav-link {
          color: #9ca3af; font-size: 14px; font-weight: 500;
          cursor: pointer; transition: color 0.2s; text-decoration: none;
        }
        .nav-link:hover { color: #f9fafb; }
        .btn-primary {
          background: #f97316; color: #fff; border: none;
          padding: 14px 28px; border-radius: 8px;
          font-size: 15px; font-weight: 700; cursor: pointer;
          box-shadow: 0 4px 20px rgba(249,115,22,0.4);
          transition: all 0.2s;
        }
        .btn-primary:hover {
          background: #ea6c0e;
          box-shadow: 0 6px 28px rgba(249,115,22,0.55);
          transform: translateY(-2px);
        }
        .btn-ghost {
          background: rgba(255,255,255,0.06); color: #e5e7eb;
          border: 1px solid rgba(255,255,255,0.14);
          padding: 14px 28px; border-radius: 8px;
          font-size: 15px; font-weight: 600; cursor: pointer;
          transition: all 0.2s;
        }
        .btn-ghost:hover {
          background: rgba(255,255,255,0.11);
          border-color: rgba(255,255,255,0.25);
          transform: translateY(-2px);
        }
        .btn-nav {
          background: #f97316; color: #fff; border: none;
          padding: 9px 20px; border-radius: 20px;
          font-size: 13px; font-weight: 700; cursor: pointer;
          transition: background 0.2s; text-decoration: none;
          display: inline-block;
        }
        .btn-nav:hover { background: #ea6c0e; }
        .feature-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 14px; padding: 28px 24px;
          transition: all 0.25s;
        }
        .feature-card:hover {
          background: rgba(255,255,255,0.06);
          border-color: rgba(249,115,22,0.3);
          transform: translateY(-4px);
          box-shadow: 0 16px 40px rgba(0,0,0,0.3);
        }
        .stat-card {
          padding: 24px 20px; text-align: center;
          border-right: 1px solid rgba(255,255,255,0.07);
        }
        .stat-card:last-child { border-right: none; }
        .section-label {
          color: #f97316; font-size: 11px; font-weight: 700;
          letter-spacing: 2px; text-transform: uppercase;
          margin-bottom: 16px;
        }
        .section-title {
          font-size: clamp(1.6rem, 3vw, 2.2rem);
          font-weight: 800; letter-spacing: -0.5px;
          margin-bottom: 16px; color: #f9fafb;
        }
        .section-sub {
          color: #6b7280; font-size: 15px; line-height: 1.65;
          max-width: 580px;
        }
        .arch-layer {
          border-radius: 12px; padding: 20px 24px; margin-bottom: 12px;
        }
        .tech-row:nth-child(even) { background: rgba(255,255,255,0.02); }
        .team-card {
          background: rgba(255,255,255,0.03);
          border: 1px solid rgba(255,255,255,0.07);
          border-radius: 16px; padding: 32px 28px;
          transition: all 0.25s;
        }
        .team-card:hover {
          background: rgba(255,255,255,0.05);
          transform: translateY(-4px);
          box-shadow: 0 16px 40px rgba(0,0,0,0.3);
        }
      `}</style>

      <div style={{
        minHeight: "100vh",
        background: "#0c0700",
        color: "#fff",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        overflowX: "hidden",
      }}>

        {/* ── Nav ─────────────────────────────────────────────── */}
        <header style={{
          position: "sticky", top: 0, zIndex: 100,
          background: "rgba(12,7,0,0.85)", backdropFilter: "blur(12px)",
          borderBottom: "1px solid rgba(255,255,255,0.05)",
        }}>
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "16px 48px", maxWidth: 1280, margin: "0 auto",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                background: "linear-gradient(135deg, #f97316, #dc2626)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 900, fontSize: 16,
              }}>T</div>
              <span style={{ fontWeight: 800, fontSize: 16, letterSpacing: 0.5 }}>TRACE.ai</span>
            </div>

            <nav style={{ display: "flex", gap: 32 }}>
              {[
                { label: "Platform", id: "platform" },
                { label: "Features", id: "features" },
                { label: "Architecture", id: "architecture" },
                { label: "Team", id: "team" },
              ].map(({ label, id }) => (
                <span key={id} className="nav-link" onClick={() => scrollTo(id)}>{label}</span>
              ))}
            </nav>

            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <Link to="/dashboard" className="btn-nav">Launch Dashboard</Link>
              <button
                onClick={() => setShowLogin(true)}
                style={{
                  background: "transparent", color: "#9ca3af",
                  border: "1px solid rgba(255,255,255,0.12)",
                  padding: "9px 20px", borderRadius: 20,
                  fontSize: 13, fontWeight: 600, cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >Sign In</button>
            </div>
          </div>
        </header>

        {/* ── Hero ────────────────────────────────────────────── */}
        <main style={{
          textAlign: "center", padding: "100px 24px 60px",
          maxWidth: 820, margin: "0 auto",
          backgroundImage: "radial-gradient(ellipse 80% 50% at 50% -5%, #4a1e00 0%, transparent 65%)",
        }}>
          <div className="fade-1" style={{
            color: "#f97316", fontSize: 11, fontWeight: 700,
            letterSpacing: "2px", textTransform: "uppercase", marginBottom: 24,
          }}>
            AML Detection Platform — iDEA 2.0 · PS3
          </div>

          <h1 className="fade-2" style={{
            fontSize: "clamp(2.8rem, 6vw, 4.6rem)",
            fontWeight: 800, lineHeight: 1.08,
            letterSpacing: "-1.5px", marginBottom: 28,
          }}>
            Autonomous AML at the<br />
            <span style={{
              background: "linear-gradient(90deg, #f97316, #fb923c, #fbbf24)",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>speed of transactions</span>
          </h1>

          <p className="fade-3" style={{
            fontSize: 17, color: "#9ca3af", lineHeight: 1.65,
            maxWidth: 660, margin: "0 auto 44px",
          }}>
            TRACE.ai detects illicit fund flows, explains every alert with SHAP
            evidence, auto-generates FIU-IND compliant STR PDFs, and retrains
            online — in one workflow your investigators will actually use.
          </p>

          <div className="fade-4" style={{ display: "flex", gap: 16, justifyContent: "center" }}>
            <Link to="/dashboard" style={{ textDecoration: "none" }}>
              <button className="btn-primary">Launch Dashboard</button>
            </Link>
            <button className="btn-ghost" onClick={() => scrollTo("architecture")}>
              View Architecture
            </button>
          </div>
        </main>

        {/* ── Code window ─────────────────────────────────────── */}
        <div className="fade-5" style={{
          maxWidth: 860, margin: "0 auto 80px", padding: "0 24px",
        }}>
          <CodeWindow />
        </div>

        {/* ── Stats bar ───────────────────────────────────────── */}
        <div style={{
          maxWidth: 1100, margin: "0 auto 100px",
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.07)",
          borderRadius: 16, display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
        }}>
          {STATS.map((s) => (
            <div key={s.label} className="stat-card">
              <div style={{
                fontSize: "clamp(1.6rem, 3vw, 2.2rem)",
                fontWeight: 800, color: "#f97316", marginBottom: 6,
              }}>{s.value}</div>
              <div style={{ fontSize: 12, color: "#6b7280", lineHeight: 1.4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* ══════════════════════════════════════════════════════
            PLATFORM
        ══════════════════════════════════════════════════════ */}
        <section id="platform" style={{
          maxWidth: 1100, margin: "0 auto 120px", padding: "0 24px",
          scrollMarginTop: 80,
        }}>
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <div className="section-label">Platform</div>
            <h2 className="section-title">Graph-Powered AML Intelligence</h2>
            <p className="section-sub" style={{ margin: "0 auto" }}>
              TRACE.ai — Transaction Risk Analysis &amp; Compliance Engine.
              Built for Indian PSBs, compliant with FIU-IND, powered by temporal graph networks.
            </p>
          </div>

          {/* Problem / Solution columns */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 40 }}>
            {/* Problem */}
            <div style={{
              background: "rgba(239,68,68,0.07)",
              border: "1px solid rgba(239,68,68,0.2)",
              borderRadius: 16, padding: 32,
            }}>
              <div style={{ color: "#f87171", fontWeight: 700, fontSize: 13, letterSpacing: 1, textTransform: "uppercase", marginBottom: 20 }}>
                The Problem
              </div>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: "#f97316", marginBottom: 8 }}>₹71,543 Cr</div>
              <div style={{ fontSize: 13, color: "#9ca3af", marginBottom: 24 }}>Lost to fraud in FY 24-25 (RBI)</div>
              <div style={{ fontSize: 14, color: "#d1d5db", lineHeight: 1.7 }}>
                Rule-based systems have <strong style={{ color: "#f87171" }}>95%+ false positives</strong>, missing complex patterns like:
              </div>
              <ul style={{ marginTop: 12, paddingLeft: 20, color: "#9ca3af", fontSize: 13, lineHeight: 2 }}>
                <li>Multi-hop layering across accounts</li>
                <li>Round-tripping through shell entities</li>
                <li>Account structuring below CTR thresholds</li>
              </ul>
              <div style={{ marginTop: 16, fontSize: 14, color: "#9ca3af" }}>
                Manual STR tracing takes <strong style={{ color: "#f87171" }}>4–6 hours</strong> per case.
              </div>
            </div>

            {/* Solution */}
            <div style={{
              background: "rgba(249,115,22,0.07)",
              border: "1px solid rgba(249,115,22,0.2)",
              borderRadius: 16, padding: 32,
            }}>
              <div style={{ color: "#f97316", fontWeight: 700, fontSize: 13, letterSpacing: 1, textTransform: "uppercase", marginBottom: 20 }}>
                The Solution: Dynamic Temporal Graphs
              </div>
              {[
                { n: "1", title: "Graph Pattern Matcher", desc: "NetworkX algorithms for money mule fan-in/out, circular flows, and structuring clusters." },
                { n: "2", title: "Temporal GNN", desc: "TGN (TGNMemory + TransformerConv) classifies suspicious nodes from evolving structural patterns. AUC 0.70 on IBM AMLSim." },
                { n: "3", title: "Online Anomaly Scorer", desc: "HalfSpaceTrees build per-account baselines via streaming learning. <1ms latency." },
                { n: "4", title: "LLM Copilot", desc: "Auto-generates FIU-IND compliant STR packages in <5 minutes." },
              ].map((item) => (
                <div key={item.n} style={{ display: "flex", gap: 14, marginBottom: 20 }}>
                  <div style={{
                    width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                    background: "rgba(249,115,22,0.2)", border: "1px solid rgba(249,115,22,0.4)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, fontWeight: 700, color: "#f97316",
                  }}>{item.n}</div>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "#f3f4f6", marginBottom: 4 }}>{item.title}</div>
                    <div style={{ fontSize: 12, color: "#6b7280", lineHeight: 1.5 }}>{item.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow */}
          <div style={{
            background: "rgba(255,255,255,0.02)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 16, padding: 32,
          }}>
            <div style={{ fontSize: 11, color: "#6b7280", fontWeight: 700, letterSpacing: 2, textTransform: "uppercase", textAlign: "center", marginBottom: 28 }}>
              TRACE.ai Architecture Workflow
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto" }}>
              {[
                { label: "Input Data", desc: "CBS / NEFT / RTGS / UPI Transactions", color: "#f97316" },
                { label: "3-Layer Graph", desc: "Accounts as Nodes, Txns as Edges", color: "#22c55e" },
                { label: "Detection Engine", desc: "Patterns + GNN + Online ML", color: "#c084fc" },
                { label: "Investigator Dash", desc: "3D Graph + Copilot + Auto-STR", color: "#7dd3fc" },
              ].map((step, i, arr) => (
                <div key={step.label} style={{ display: "flex", alignItems: "center", flex: 1, minWidth: 180 }}>
                  <div style={{
                    flex: 1, background: `${step.color}12`,
                    border: `1px solid ${step.color}30`,
                    borderRadius: 10, padding: "16px 20px", textAlign: "center",
                  }}>
                    <div style={{ fontWeight: 700, fontSize: 12, color: step.color, marginBottom: 6 }}>{step.label}</div>
                    <div style={{ fontSize: 11, color: "#6b7280", lineHeight: 1.5 }}>{step.desc}</div>
                  </div>
                  {i < arr.length - 1 && (
                    <div style={{ fontSize: 20, color: "#374151", padding: "0 8px", flexShrink: 0 }}>→</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════
            FEATURES
        ══════════════════════════════════════════════════════ */}
        <section id="features" style={{
          maxWidth: 1100, margin: "0 auto 120px", padding: "0 24px",
          scrollMarginTop: 80,
        }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div className="section-label">Features</div>
            <h2 className="section-title">Six differentiators. No other PS3 team has all six.</h2>
            <p className="section-sub" style={{ margin: "0 auto" }}>
              Five layers of innovation — not one. Temporal GNN, streaming online ML, NL investigation,
              automated regulatory reporting, and hot-reloadable compliance.
            </p>
          </div>

          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20,
          }}>
            {FEATURES.map((f) => (
              <div key={f.title} className="feature-card">
                <div style={{
                  width: 44, height: 44, borderRadius: 10, marginBottom: 18,
                  background: `${f.accent}18`,
                  border: `1px solid ${f.accent}30`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 20,
                }}>{f.icon}</div>
                <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 10, color: "#f3f4f6" }}>
                  {f.title}
                </div>
                <div style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.6 }}>{f.desc}</div>
              </div>
            ))}
          </div>

          {/* Impact metrics row */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 1,
            background: "rgba(255,255,255,0.05)",
            borderRadius: 14, overflow: "hidden", marginTop: 48,
          }}>
            {[
              { val: "37%", sub: "FP reduction vs static GNN baseline" },
              { val: "5 min", sub: "STR generation (was 4–6 hrs)" },
              { val: "Real-time", sub: "Fraud ID (IBM 2024: 277 days)" },
              { val: "AUC 0.70", sub: "TGN on IBM AMLSim 20K nodes" },
              { val: "<15%", sub: "Target false positive rate" },
            ].map((m) => (
              <div key={m.val} style={{
                padding: "24px 16px", textAlign: "center",
                background: "rgba(255,255,255,0.02)",
                borderRight: "1px solid rgba(255,255,255,0.05)",
              }}>
                <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "#f97316", marginBottom: 6 }}>{m.val}</div>
                <div style={{ fontSize: 11, color: "#6b7280", lineHeight: 1.4 }}>{m.sub}</div>
              </div>
            ))}
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════
            ARCHITECTURE
        ══════════════════════════════════════════════════════ */}
        <section id="architecture" style={{
          maxWidth: 1100, margin: "0 auto 120px", padding: "0 24px",
          scrollMarginTop: 80,
        }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div className="section-label">Architecture</div>
            <h2 className="section-title">5-Layer Modular Design</h2>
            <p className="section-sub" style={{ margin: "0 auto" }}>
              Each detection module operates independently with a standardized interface.
              Ground truth uses AMLSim-generated synthetic data with precision/recall at multiple risk thresholds.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
            {/* Architecture layers */}
            <div>
              <div style={{ fontSize: 12, color: "#6b7280", fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 16 }}>
                TRACE.ai Architecture
              </div>
              {ARCH_LAYERS.map((layer) => (
                <div
                  key={layer.label}
                  className="arch-layer"
                  style={{
                    background: `${layer.color}0d`,
                    border: `1px solid ${layer.color}25`,
                    marginBottom: 10,
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: 13, color: layer.color, marginBottom: 8 }}>
                    {layer.label}
                  </div>
                  {layer.items.map((item) => (
                    <div key={item} style={{ fontSize: 12, color: "#9ca3af", lineHeight: 1.8 }}>
                      · {item}
                    </div>
                  ))}
                </div>
              ))}
            </div>

            {/* Tech stack */}
            <div>
              <div style={{ fontSize: 12, color: "#6b7280", fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase", marginBottom: 16 }}>
                Tech Stack
              </div>
              <div style={{
                background: "rgba(255,255,255,0.02)",
                border: "1px solid rgba(255,255,255,0.07)",
                borderRadius: 12, overflow: "hidden",
              }}>
                <div style={{
                  display: "grid", gridTemplateColumns: "1fr 2fr",
                  padding: "10px 20px",
                  background: "rgba(255,255,255,0.04)",
                  borderBottom: "1px solid rgba(255,255,255,0.07)",
                }}>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", letterSpacing: 1 }}>LAYER</div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "#6b7280", letterSpacing: 1 }}>TECHNOLOGY</div>
                </div>
                {TECH_STACK.map((row) => (
                  <div
                    key={row.layer}
                    className="tech-row"
                    style={{
                      display: "grid", gridTemplateColumns: "1fr 2fr",
                      padding: "10px 20px",
                      borderBottom: "1px solid rgba(255,255,255,0.04)",
                    }}
                  >
                    <div style={{ fontSize: 12, color: "#9ca3af", fontWeight: 600 }}>{row.layer}</div>
                    <div style={{ fontSize: 12, color: "#d1d5db" }}>{row.tech}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ══════════════════════════════════════════════════════
            TEAM
        ══════════════════════════════════════════════════════ */}
        <section id="team" style={{
          maxWidth: 1100, margin: "0 auto 120px", padding: "0 24px",
          scrollMarginTop: 80,
        }}>
          <div style={{ textAlign: "center", marginBottom: 56 }}>
            <div className="section-label">Team</div>
            <h2 className="section-title">Team NamoFans</h2>
            <p className="section-sub" style={{ margin: "0 auto" }}>
              Four specialists. One submission. iDEA 2.0 Hackathon — PS3, Union Bank of India.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20 }}>
            {TEAM.map((member) => (
              <div key={member.name} className="team-card">
                <div style={{
                  width: 52, height: 52, borderRadius: 14, marginBottom: 20,
                  background: `${member.color}20`,
                  border: `1px solid ${member.color}40`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontWeight: 800, fontSize: 16, color: member.color,
                  letterSpacing: 0.5,
                }}>{member.avatar}</div>
                <div style={{ fontWeight: 700, fontSize: 16, color: "#f3f4f6", marginBottom: 4 }}>
                  {member.name}
                </div>
                <div style={{
                  fontSize: 12, color: member.color, fontWeight: 600,
                  marginBottom: 14, letterSpacing: 0.3,
                }}>
                  {member.role}
                </div>
                <div style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.65 }}>
                  {member.bio}
                </div>
              </div>
            ))}
          </div>

          <div style={{
            marginTop: 48,
            background: "rgba(255,255,255,0.02)",
            border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: 14, padding: "28px 36px",
            display: "flex", justifyContent: "space-between", alignItems: "center",
            flexWrap: "wrap", gap: 16,
          }}>
            <div>
              <div style={{ fontWeight: 700, color: "#f9fafb", marginBottom: 4 }}>PSBs Hackathon Series 2026</div>
              <div style={{ fontSize: 13, color: "#6b7280" }}>
                iDEA 2.0 · PS3 — Tracking of Funds within Bank for Fraud Detection
              </div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 13, color: "#6b7280" }}>Organized by</div>
              <div style={{ fontWeight: 600, color: "#d1d5db", fontSize: 14 }}>
                Union Bank of India · Somaiya Vidyavihar University
              </div>
              <div style={{ fontSize: 12, color: "#4b5563", marginTop: 2 }}>
                Dept. of Financial Services, Ministry of Finance, Govt. of India
              </div>
            </div>
          </div>
        </section>

        {/* ── CTA footer ──────────────────────────────────────── */}
        <section style={{
          textAlign: "center", padding: "80px 24px 100px",
          borderTop: "1px solid rgba(255,255,255,0.05)",
        }}>
          <h2 style={{
            fontSize: "clamp(1.8rem, 3.5vw, 2.4rem)",
            fontWeight: 800, marginBottom: 16, letterSpacing: -0.5,
          }}>
            Ready to trace the money?
          </h2>
          <p style={{ color: "#6b7280", fontSize: 15, marginBottom: 36 }}>
            Live on Google Cloud Run. No setup needed.
          </p>
          <Link to="/dashboard" style={{ textDecoration: "none" }}>
            <button className="btn-primary" style={{ fontSize: 16, padding: "16px 36px" }}>
              Launch Dashboard →
            </button>
          </Link>
          <div style={{ marginTop: 48, color: "#374151", fontSize: 12, letterSpacing: 0.5 }}>
            Team NamoFans · IIT Kharagpur · iDEA 2.0 Hackathon · PS3
          </div>
        </section>

      </div>
    </>
  );
}
