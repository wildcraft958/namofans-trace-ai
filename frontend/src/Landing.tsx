import { Link } from "react-router-dom";
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
    desc: "FIU-IND compliant 8-section Suspicious Transaction Reports, generated in one click via ReportLab. No other PS3 team has this.",
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
    desc: "River HalfSpaceTrees + ADWIN detect distribution shifts in real time. Inject a pattern and watch the timeline react.",
    accent: "#f97316",
  },
];

const STATS = [
  { value: "₹71,543 Cr", label: "Annual bank fraud (RBI 2023-24)" },
  { value: "95%", label: "False positive rate in rule-based systems" },
  { value: "AUC 1.0", label: "XGBoost on seeded fraud rings" },
  { value: "<2 s", label: "Alert latency over WebSocket" },
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
      {/* traffic lights */}
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
      {/* code body */}
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

export default function Landing() {
  return (
    <>
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
        @keyframes shimmer {
          0%   { background-position: -400px 0; }
          100% { background-position: 400px 0; }
        }
        .fade-1 { animation: fadeUp 0.7s ease both; }
        .fade-2 { animation: fadeUp 0.7s 0.12s ease both; }
        .fade-3 { animation: fadeUp 0.7s 0.24s ease both; }
        .fade-4 { animation: fadeUp 0.7s 0.36s ease both; }
        .fade-5 { animation: fadeUp 0.7s 0.48s ease both; }
        .nav-link {
          color: #9ca3af; font-size: 14px; font-weight: 500;
          cursor: pointer; transition: color 0.2s;
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
          transition: background 0.2s;
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
      `}</style>

      <div style={{
        minHeight: "100vh",
        background: "#0c0700",
        backgroundImage: "radial-gradient(ellipse 80% 50% at 50% -5%, #4a1e00 0%, #0c0700 65%)",
        color: "#fff",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        overflowX: "hidden",
      }}>

        {/* ── Nav ─────────────────────────────────────────────── */}
        <header style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "18px 48px", maxWidth: 1280, margin: "0 auto",
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
            {["Platform", "Features", "Architecture", "Team"].map((l) => (
              <span key={l} className="nav-link">{l}</span>
            ))}
          </nav>

          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            <Link to="/dashboard" style={{ textDecoration: "none" }}>
              <button className="btn-nav">Launch App</button>
            </Link>
            <button style={{
              background: "transparent", color: "#9ca3af",
              border: "1px solid rgba(255,255,255,0.12)",
              padding: "9px 20px", borderRadius: 20,
              fontSize: 13, fontWeight: 600, cursor: "pointer",
            }}>Sign In</button>
          </div>
        </header>

        {/* ── Hero ────────────────────────────────────────────── */}
        <main style={{
          textAlign: "center", padding: "80px 24px 60px",
          maxWidth: 820, margin: "0 auto",
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
            <button className="btn-ghost">View Architecture</button>
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
          maxWidth: 1100, margin: "0 auto 80px",
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

        {/* ── Features ────────────────────────────────────────── */}
        <section style={{ maxWidth: 1100, margin: "0 auto 100px", padding: "0 24px" }}>
          <h2 style={{
            textAlign: "center", fontSize: "clamp(1.6rem, 3vw, 2rem)",
            fontWeight: 700, marginBottom: 12, letterSpacing: -0.5,
          }}>Everything the judge needs to see</h2>
          <p style={{
            textAlign: "center", color: "#6b7280", fontSize: 15,
            marginBottom: 48, maxWidth: 520, margin: "0 auto 48px",
          }}>
            Four differentiators no other PS3 team will demo.
          </p>

          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 20,
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
              Open Live Dashboard →
            </button>
          </Link>
          <div style={{ marginTop: 48, color: "#374151", fontSize: 12, letterSpacing: 0.5 }}>
            Team NamoFans · IIT Kharagpur · iDEA 2.0 Hackathon
          </div>
        </section>

      </div>
    </>
  );
}
