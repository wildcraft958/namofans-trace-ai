import { useState } from "react";

export default function InvestigationPanel() {
  const [q, setQ] = useState("");
  return (
    <div style={{ background: "#11141d", borderRadius: 8, padding: 12, display: "grid", gridTemplateRows: "auto 1fr auto", gap: 8 }}>
      <h3 style={{ margin: 0 }}>Investigation Copilot</h3>
      <div style={{ overflow: "auto", fontSize: 13, color: "#8a91a3" }}>
        Try: <em>"Show all circular flows above ₹5L in the last 7 days"</em>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          // TODO(frontend): POST /investigate with nl_query and render result subgraph
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Ask in plain English…"
          style={{ width: "100%", padding: 8, background: "#0b0d12", color: "#e6e8ee", border: "1px solid #1c1f2a", borderRadius: 6 }}
        />
      </form>
    </div>
  );
}
