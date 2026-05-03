/**
 * ExplainabilityCard — opens when a user clicks the "Why?" button on an alert.
 * Renders the GNNExplainer subgraph (top-k contributing nodes/edges) and SHAP feature scores.
 */
export default function ExplainabilityCard({ alertId }: { alertId: string }) {
  return (
    <div style={{ background: "#11141d", borderRadius: 8, padding: 12 }}>
      <h4 style={{ margin: 0 }}>Why was this flagged?</h4>
      <div style={{ fontSize: 12, color: "#8a91a3" }}>Alert {alertId}</div>
      {/* TODO(frontend): GET /alerts/:id/explain → render subgraph + SHAP bar chart */}
    </div>
  );
}
