import { useState } from "react";
import GraphVisualization from "./components/GraphVisualization";
import AlertPanel from "./components/AlertPanel";
import InvestigationPanel from "./components/InvestigationPanel";
import KPICards from "./components/KPICards";
import ExplainabilityCard from "./components/ExplainabilityCard";
import DriftTimeline from "./components/DriftTimeline";

export default function App() {
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
        * { box-sizing: border-box; }
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: #0b0d12; }
        ::-webkit-scrollbar-thumb { background: #1c1f2a; border-radius: 4px; }
        input:focus { border-color: #7aa2ff !important; }
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
            <div
              style={{
                width: 32,
                height: 32,
                background: "linear-gradient(135deg, #7aa2ff 0%, #a78bfa 100%)",
                borderRadius: 8,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 16,
                fontWeight: 900,
                color: "#fff",
                flexShrink: 0,
              }}
            >
              T
            </div>
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
            <div
              style={{
                fontSize: 11,
                color: "#6b7280",
                display: "flex",
                gap: 12,
              }}
            >
              <span style={{ color: "#4b5563" }}>PS3</span>
              <span style={{ color: "#4b5563" }}>·</span>
              <span style={{ color: "#4b5563" }}>Team NamoFans</span>
              <span style={{ color: "#4b5563" }}>·</span>
              <span style={{ color: "#4b5563" }}>iDEA 2.0</span>
            </div>
            <span
              style={{
                fontSize: 10,
                background: "#112211",
                color: "#4ade80",
                border: "1px solid #1a3a1a",
                borderRadius: 20,
                padding: "3px 10px",
                fontWeight: 600,
                letterSpacing: 0.5,
              }}
            >
              LIVE
            </span>
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
            <GraphVisualization
              focusAccountId={focusAccountId}
              onNodeClick={handleNodeClick}
            />
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
