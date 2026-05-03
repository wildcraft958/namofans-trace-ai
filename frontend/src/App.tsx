import GraphVisualization from "./components/GraphVisualization";
import AlertPanel from "./components/AlertPanel";
import InvestigationPanel from "./components/InvestigationPanel";
import KPICards from "./components/KPICards";

export default function App() {
  return (
    <div style={{ display: "grid", gridTemplateRows: "auto 1fr", height: "100vh", background: "#0b0d12", color: "#e6e8ee" }}>
      <header style={{ padding: "12px 20px", borderBottom: "1px solid #1c1f2a" }}>
        <h1 style={{ margin: 0, fontSize: 18, letterSpacing: 0.5 }}>TRACE.ai · Transaction Risk Analysis & Compliance Engine</h1>
      </header>
      <main style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 12, padding: 12, overflow: "hidden" }}>
        <section style={{ display: "grid", gridTemplateRows: "auto 1fr", gap: 12, minHeight: 0 }}>
          <KPICards />
          <GraphVisualization />
        </section>
        <aside style={{ display: "grid", gridTemplateRows: "1fr 1fr", gap: 12, minHeight: 0 }}>
          <AlertPanel />
          <InvestigationPanel />
        </aside>
      </main>
    </div>
  );
}
