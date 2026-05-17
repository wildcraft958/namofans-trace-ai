import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";

interface KPI {
  label: string;
  value: string;
  numericValue?: number;
  sub?: string;
  color: string;
  bg: string;
  border: string;
  icon: string;
  suffix?: string;
  benchmark?: string;
}

function useCountUp(target: number, duration = 900) {
  const [displayed, setDisplayed] = useState(0);
  const frame = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (target === 0) { setDisplayed(0); return; }
    const start = Date.now();
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(Math.round(eased * target));
      if (progress < 1) frame.current = setTimeout(tick, 16);
    };
    frame.current = setTimeout(tick, 16);
    return () => { if (frame.current) clearTimeout(frame.current); };
  }, [target, duration]);

  return displayed;
}

function KPICard({ kpi }: { kpi: KPI }) {
  const numeric = useCountUp(kpi.numericValue ?? 0);
  const displayValue = kpi.numericValue !== undefined
    ? `${numeric}${kpi.suffix ?? ""}`
    : kpi.value;

  return (
    <div style={{
      background: kpi.bg,
      borderRadius: 12,
      padding: "16px 18px 14px",
      border: `1px solid ${kpi.border}`,
      borderLeft: `3px solid ${kpi.color}`,
      boxShadow: `0 0 20px ${kpi.color}14, 0 2px 8px rgba(0,0,0,0.4)`,
      display: "flex",
      flexDirection: "column",
      gap: 4,
      position: "relative",
      overflow: "hidden",
    }}>
      {/* glow orb background */}
      <div style={{
        position: "absolute", top: -20, right: -20,
        width: 80, height: 80, borderRadius: "50%",
        background: kpi.color, opacity: 0.06, filter: "blur(20px)",
        pointerEvents: "none",
      }} />

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{
          fontSize: 10, color: "#5a6175",
          textTransform: "uppercase", letterSpacing: 1, fontWeight: 600,
        }}>{kpi.label}</span>
        <span style={{ fontSize: 14, opacity: 0.8 }}>{kpi.icon}</span>
      </div>

      <div style={{
        fontSize: 28, fontWeight: 800, color: kpi.color,
        letterSpacing: -1, lineHeight: 1.1,
      }}>
        {displayValue}
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        {kpi.sub && (
          <div style={{ fontSize: 10, color: "#4b5563", lineHeight: 1.4 }}>{kpi.sub}</div>
        )}
        {kpi.benchmark && (
          <div style={{
            fontSize: 9, color: "#22c55e",
            background: "rgba(34,197,94,0.1)",
            border: "1px solid rgba(34,197,94,0.2)",
            borderRadius: 10, padding: "1px 7px", fontWeight: 700, whiteSpace: "nowrap",
          }}>{kpi.benchmark}</div>
        )}
      </div>
    </div>
  );
}

const DEFAULTS: KPI[] = [
  {
    label: "Alerts Today", value: "—", icon: "🚨",
    color: "#f97316", bg: "linear-gradient(135deg,#1a0f00,#130d00)",
    border: "#2a1a00",
  },
  {
    label: "Critical / High", value: "—", icon: "⚠",
    color: "#ef4444", bg: "linear-gradient(135deg,#1a0a0a,#130808)",
    border: "#2a1010",
  },
  {
    label: "False Positive Rate", value: "~5%", icon: "✓",
    color: "#22c55e", bg: "linear-gradient(135deg,#05150a,#040e08)",
    border: "#0d2a15",
  },
  {
    label: "STRs Queued", value: "—", icon: "📄",
    color: "#818cf8", bg: "linear-gradient(135deg,#0d0e1a,#090a14)",
    border: "#1a1c2e",
  },
];

export default function KPICards() {
  const [kpis, setKpis] = useState<KPI[]>(DEFAULTS);

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
          numericValue: alerts.length,
          sub: `${medium} medium risk`,
          icon: "🚨",
          color: "#f97316",
          bg: "linear-gradient(135deg,#1a0f00,#130d00)",
          border: "#2a1a00",
        },
        {
          label: "Critical / High",
          value: `${critical} / ${high}`,
          numericValue: critical + high,
          suffix: "",
          sub: "immediate action required",
          icon: "⚠",
          color: "#ef4444",
          bg: "linear-gradient(135deg,#1a0a0a,#130808)",
          border: "#2a1010",
        },
        {
          label: "False Positive Rate",
          value: "~5%",
          numericValue: 5,
          suffix: "%",
          sub: "vs 95% in rule-only systems",
          icon: "✓",
          color: "#22c55e",
          bg: "linear-gradient(135deg,#05150a,#040e08)",
          border: "#0d2a15",
          benchmark: "90% reduction",
        },
        {
          label: "STRs Queued",
          value: String(strQueued),
          numericValue: strQueued,
          sub: "pending compliance review",
          icon: "📄",
          color: "#818cf8",
          bg: "linear-gradient(135deg,#0d0e1a,#090a14)",
          border: "#1a1c2e",
          benchmark: "FIU-IND",
        },
      ]);
    }).catch(() => {});
  }, []);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
      {kpis.map((c) => <KPICard key={c.label} kpi={c} />)}
    </div>
  );
}
