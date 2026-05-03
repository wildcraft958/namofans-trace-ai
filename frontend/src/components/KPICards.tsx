export default function KPICards() {
  const cards = [
    { label: "Alerts today", value: "—" },
    { label: "High-risk accounts", value: "—" },
    { label: "False-positive rate", value: "—" },
    { label: "STRs generated", value: "—" },
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
      {cards.map((c) => (
        <div key={c.label} style={{ background: "#11141d", borderRadius: 8, padding: 12 }}>
          <div style={{ fontSize: 12, color: "#8a91a3" }}>{c.label}</div>
          <div style={{ fontSize: 22, marginTop: 4 }}>{c.value}</div>
        </div>
      ))}
    </div>
  );
}
