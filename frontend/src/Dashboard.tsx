import { useState } from "react";
import GraphVisualization from "./components/GraphVisualization";
import AlertPanel from "./components/AlertPanel";
import InvestigationPanel from "./components/InvestigationPanel";
import KPICards from "./components/KPICards";
import ExplainabilityCard from "./components/ExplainabilityCard";
import DriftTimeline from "./components/DriftTimeline";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const [selectedAlertId, setSelectedAlertId] = useState<string | null>(null);
  const [focusAccountId, setFocusAccountId] = useState<string | null>(null);

  const handleAlertSelect = (alertId: string) => {
    setSelectedAlertId(alertId);
  };

  const handleSubgraphFocus = (accountIds: string[]) => {
    if (accountIds.length > 0) {
      setFocusAccountId(accountIds[0]);
    }
  };

  const handleNodeClick = (accountId: string) => {
    setFocusAccountId(accountId);
  };

  return (
    <>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        html, body { margin: 0; padding: 0; background: #0b0d12; }
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0b0d12; }
        ::-webkit-scrollbar-thumb { background: #1c1f2a; border-radius: 4px; }
        input:focus { border-color: #f97316 !important; }
      `}</style>

      <div
        style={{
          display: "grid",
          gridTemplateRows: "auto 1fr auto",
          height: "100vh",
          background: "#0b0d12",
          color: "#e6e8ee",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <header
          style={{
            padding: "10px 20px",
            borderBottom: "1px solid #1c1f2a",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            background: "linear-gradient(90deg, #0b0d12 0%, #0e1220 100%)",
            flexShrink: 0,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <Link to="/" style={{ textDecoration: 'none' }}>
              <div
                style={{
                  width: 32,
                  height: 32,
                  background: "linear-gradient(135deg, #f97316 0%, #dc2626 100%)",
                  borderRadius: 8,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 16,
                  fontWeight: 900,
                  color: "#fff",
                  flexShrink: 0,
                  cursor: "pointer",
                }}
              >
                T
              </div>
            </Link>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15, letterSpacing: 0.5, color: "#e6e8ee" }}>
                TRACE.ai
              </div>
              <div style={{ fontSize: 10, color: "#4b5563", letterSpacing: 0.3 }}>
                Transaction Risk Analysis & Compliance Engine
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ fontSize: 11, color: "#4b5563", display: "flex", gap: 8 }}>
              <span>PS3</span><span>·</span>
              <span>Team NamoFans</span><span>·</span>
              <span>iDEA 2.0</span>
            </div>
            <span style={{
              fontSize: 10, background: "#112211", color: "#4ade80",
              border: "1px solid #1a3a1a", borderRadius: 20,
              padding: "3px 10px", fontWeight: 600, letterSpacing: 0.5,
            }}>LIVE</span>
            <Link to="/" style={{
              textDecoration: "none", color: "#6b7280", fontSize: 11,
              border: "1px solid #1c1f2a", borderRadius: 16,
              padding: "4px 12px", transition: "color 0.2s, border-color 0.2s",
            }}
            onMouseOver={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = "#e5e7eb"; (e.currentTarget as HTMLAnchorElement).style.borderColor = "#374151"; }}
            onMouseOut={(e) => { (e.currentTarget as HTMLAnchorElement).style.color = "#6b7280"; (e.currentTarget as HTMLAnchorElement).style.borderColor = "#1c1f2a"; }}
            >← Home</Link>
          </div>
        </header>

        {/* Main content */}
        <main
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 360px",
            gap: 10,
            padding: "10px 12px 0",
            overflow: "hidden",
            minHeight: 0,
          }}
        >
          {/* Left column: KPIs + Graph */}
          <section
            style={{
              display: "grid",
              gridTemplateRows: "auto 1fr",
              gap: 10,
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            <KPICards />
            <div style={{
              display: "grid", gridTemplateRows: "auto 1fr",
              minHeight: 0, overflow: "hidden",
              background: "#0e1117", border: "1px solid #1c1f2a", borderRadius: 10,
            }}>
              <div style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "8px 14px",
                borderBottom: "1px solid #1c1f2a",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{
                    width: 7, height: 7, borderRadius: "50%",
                    background: "#f97316", boxShadow: "0 0 6px #f97316",
                    animation: "pulse 2s ease-in-out infinite",
                  }} />
                  <span style={{ fontWeight: 700, fontSize: 12, color: "#d1d5db", letterSpacing: 0.3 }}>
                    Fund Flow Graph
                  </span>
                </div>
                <div style={{ display: "flex", gap: 12, fontSize: 10, color: "#4b5563" }}>
                  <span>1,500+ nodes</span>
                  <span>·</span>
                  <span>8 fraud rings</span>
                  <span>·</span>
                  <span style={{ color: "#22c55e" }}>XGBoost AUC 1.0</span>
                </div>
              </div>
              <GraphVisualization
                focusAccountId={focusAccountId}
                onNodeClick={handleNodeClick}
              />
            </div>
          </section>

          {/* Right column: Alerts + Investigation */}
          <aside
            style={{
              display: "grid",
              gridTemplateRows: "1fr 1fr",
              gap: 10,
              minHeight: 0,
              overflow: "hidden",
            }}
          >
            <AlertPanel
              onSelect={handleAlertSelect}
              selectedAlertId={selectedAlertId}
            />
            <InvestigationPanel onSubgraphFocus={handleSubgraphFocus} />
          </aside>
        </main>

        {/* Drift timeline footer */}
        <footer style={{ padding: "8px 12px 10px", flexShrink: 0 }}>
          <DriftTimeline />
        </footer>
      </div>

      {/* Explainability modal */}
      {selectedAlertId && (
        <ExplainabilityCard
          alertId={selectedAlertId}
          onClose={() => setSelectedAlertId(null)}
        />
      )}
    </>
  );
}
