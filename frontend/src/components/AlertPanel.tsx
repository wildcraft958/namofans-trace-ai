import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAlertWebSocket } from "../hooks/useWebSocket";

const RISK_STYLE: Record<string, { bg: string; color: string; glow: string }> = {
  CRITICAL: { bg: "#2d0f0f", color: "#e74c3c", glow: "0 0 8px #e74c3c60" },
  HIGH: { bg: "#2d1a0a", color: "#e67e22", glow: "0 0 8px #e67e2260" },
  MEDIUM: { bg: "#2d2800", color: "#f1c40f", glow: "0 0 8px #f1c40f40" },
  LOW: { bg: "#0a2d14", color: "#2ecc71", glow: "none" },
};

interface Alert {
  alert_id: string;
  account_id: string;
  risk_level: string;
  composite_score: number;
  pattern_matches: Record<string, boolean>;
  status: string;
  timestamp: string;
}

interface Props {
  onSelect?: (alertId: string) => void;
  selectedAlertId?: string | null;
}

export default function AlertPanel({ onSelect, selectedAlertId }: Props) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const { wsAlerts, connected } = useAlertWebSocket();

  useEffect(() => {
    api.get<Alert[]>("/alerts")
      .then((r) => setAlerts(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Merge WebSocket new alerts into the list
  useEffect(() => {
    if (wsAlerts.length === 0) return;
    const latest = wsAlerts[0];
    if (latest.type !== "alert" || !latest.alert_id) return;
    setAlerts((prev) => {
      const exists = prev.find((a) => a.alert_id === latest.alert_id);
      if (exists) return prev;
      return [
        {
          alert_id: latest.alert_id!,
          account_id: latest.account_id ?? "—",
          risk_level: latest.risk_level ?? "MEDIUM",
          composite_score: latest.composite_score ?? 0,
          pattern_matches: {},
          status: "open",
          timestamp: new Date().toISOString().slice(0, 10),
        },
        ...prev,
      ].slice(0, 100);
    });
  }, [wsAlerts]);

  const acknowledge = async (alertId: string) => {
    await api.post(`/alerts/${alertId}/acknowledge`);
    setAlerts((prev) =>
      prev.map((a) => (a.alert_id === alertId ? { ...a, status: "acknowledged" } : a))
    );
  };

  const patterns = (alert: Alert) =>
    Object.entries(alert.pattern_matches ?? {})
      .filter(([, v]) => v)
      .map(([k]) => k.replace(/_/g, " "))
      .slice(0, 2);

  return (
    <div
      style={{
        background: "#100e0b",
        borderRadius: 10,
        border: "1px solid #1c1510",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        height: "100%",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "10px 14px",
          borderBottom: "1px solid #1c1510",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexShrink: 0,
        }}
      >
        <span style={{ fontWeight: 700, fontSize: 13, letterSpacing: 0.3 }}>
          🚨 Alert Queue
        </span>
        <span
          style={{
            fontSize: 11,
            display: "flex",
            alignItems: "center",
            gap: 5,
            color: connected ? "#2ecc71" : "#e74c3c",
          }}
        >
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: connected ? "#2ecc71" : "#e74c3c",
              boxShadow: connected ? "0 0 6px #2ecc71" : "none",
              display: "inline-block",
              animation: connected ? "pulse 2s infinite" : "none",
            }}
          />
          {connected ? "Live" : "Reconnecting…"}
        </span>
      </div>

      {/* Alert list */}
      <div style={{ overflow: "auto", flex: 1, padding: "6px 0" }}>
        {loading && (
          <div style={{ padding: 16, textAlign: "center", color: "#4b5563", fontSize: 13 }}>
            Loading alerts…
          </div>
        )}
        {!loading && alerts.length === 0 && (
          <div style={{ padding: 16, textAlign: "center", color: "#4b5563", fontSize: 13 }}>
            No alerts — system healthy
          </div>
        )}
        {alerts.map((alert) => {
          const rs = RISK_STYLE[alert.risk_level] ?? RISK_STYLE.LOW;
          const isSelected = alert.alert_id === selectedAlertId;
          return (
            <div
              key={alert.alert_id}
              onClick={() => onSelect?.(alert.alert_id)}
              style={{
                padding: "10px 14px",
                borderBottom: "1px solid #1a1510",
                cursor: "pointer",
                background: isSelected ? "#1a1208" : "transparent",
                borderLeft: isSelected ? `3px solid ${rs.color}` : "3px solid transparent",
                transition: "background 0.15s",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                {/* Risk pill */}
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 10,
                    background: rs.bg,
                    color: rs.color,
                    boxShadow: rs.glow,
                    letterSpacing: 0.5,
                  }}
                >
                  {alert.risk_level}
                </span>
                <span style={{ fontSize: 10, color: "#4b5563" }}>
                  {(alert.composite_score * 100).toFixed(0)}%
                </span>
              </div>

              <div style={{ fontSize: 12, color: "#d1d5db", fontFamily: "monospace" }}>
                {alert.account_id}
              </div>

              {patterns(alert).length > 0 && (
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                  {patterns(alert).map((p) => (
                    <span
                      key={p}
                      style={{
                        fontSize: 9,
                        padding: "1px 6px",
                        background: "#1a1510",
                        color: "#6b7280",
                        borderRadius: 8,
                      }}
                    >
                      {p}
                    </span>
                  ))}
                </div>
              )}

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginTop: 6,
                }}
              >
                <span style={{ fontSize: 10, color: "#374151" }}>{alert.timestamp}</span>
                <div style={{ display: "flex", gap: 6 }}>
                  {alert.status === "open" && (
                    <button
                      onClick={(e) => { e.stopPropagation(); acknowledge(alert.alert_id); }}
                      style={{
                        fontSize: 10,
                        padding: "2px 8px",
                        background: "#1c2d1c",
                        color: "#4ade80",
                        border: "1px solid #2d4a2d",
                        borderRadius: 5,
                        cursor: "pointer",
                      }}
                    >
                      ✓ ACK
                    </button>
                  )}
                  {alert.status === "acknowledged" && (
                    <span style={{ fontSize: 10, color: "#2ecc71" }}>✓ Acked</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
