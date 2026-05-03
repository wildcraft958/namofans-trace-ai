export default function AlertPanel() {
  return (
    <div style={{ background: "#11141d", borderRadius: 8, padding: 12, overflow: "auto" }}>
      <h3 style={{ marginTop: 0 }}>Alerts</h3>
      {/* TODO(frontend): connect WebSocket /ws/alerts and render incoming alerts with risk pill */}
      <p style={{ color: "#8a91a3", fontSize: 13 }}>Awaiting alert stream…</p>
    </div>
  );
}
