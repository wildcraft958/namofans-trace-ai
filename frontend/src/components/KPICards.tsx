import { useEffect, useState } from "react";
import { api } from "../api/client";

interface KPI {
  label: string;
  value: string;
  sub?: string;
  color?: string;
  icon: string;
}

export default function KPICards() {
  const [kpis, setKpis] = useState<KPI[]>([
    { label: "Alerts Today", value: "—", icon: "🚨" },
    { label: "CRITICAL / HIGH", value: "—", icon: "🔴", color: "#c0392b" },
    { label: "Est. False Positive Rate", value: "~5%", sub: "vs. 95% rule-only", icon: "✅", color: "#27ae60" },
    { label: "STRs Queued", value: "—", icon: "📄" },
  ]);

  useEffect(() => {
    api.get("/alerts").then((res) => {
      const alerts = res.data as any[];
      const critical = alerts.filter((a) => a.risk_level === "CRITICAL").length;
      const high = alerts.filter((a) => a.risk_level === "HIGH").length;
      const medium = alerts.filter((a) => a.risk_level === "MEDIUM").length;
      const strQueued = alerts.filter(
        (a) => ["CRITICAL", "HIGH"].includes(a.risk_level) && a.status === "open"
      ).length;
      setKpis([
        {
          label: "Alerts Today",
          value: String(alerts.length),
          sub: `${medium} medium`,
          icon: "🚨",
          color: "#e6e8ee",
        },
        {
          label: "CRITICAL / HIGH",
          value: `${critical} / ${high}`,
          sub: "require immediate action",
          icon: "🔴",
          color: "#e67e22",
        },
        {
          label: "Est. False Positive Rate",
          value: "~5%",
          sub: "vs. 95% rule-only systems",
          icon: "✅",
          color: "#27ae60",
        },
        {
          label: "STRs Queued",
          value: String(strQueued),
          sub: "pending compliance review",
          icon: "📄",
          color: "#7aa2ff",
        },
      ]);
    }).catch(() => {});
  }, []);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
      {kpis.map((c) => (
        <div
          key={c.label}
          style={{
            background: "linear-gradient(135deg, #11141d 0%, #151822 100%)",
            borderRadius: 10,
            padding: "14px 16px",
            border: "1px solid #1c1f2a",
            boxShadow: c.color ? `0 0 12px ${c.color}18` : "none",
            transition: "box-shadow 0.3s",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span style={{ fontSize: 16 }}>{c.icon}</span>
            <span style={{ fontSize: 11, color: "#6b7280", textTransform: "uppercase", letterSpacing: 0.8 }}>
              {c.label}
            </span>
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, color: c.color ?? "#e6e8ee", letterSpacing: -0.5 }}>
            {c.value}
          </div>
          {c.sub && (
            <div style={{ fontSize: 11, color: "#4b5563", marginTop: 3 }}>{c.sub}</div>
          )}
        </div>
      ))}
    </div>
  );
}
