import { useEffect, useState } from "react";
import { api } from "../api/client";
import STRDownload from "./STRDownload";

interface ShapFeature {
  feature: string;
  shap_value: number;
}

interface ExplainData {
  alert_id: string;
  account_id: string;
  risk_level: string;
  composite_score: number;
  pattern_matches: Record<string, boolean>;
  risk_contributions: Record<string, number>;
  shap_features: ShapFeature[];
  llm_explanation: string;
  compliance_rules: { rule_id: string; action: string; severity: string }[];
}

const RISK_COLOR: Record<string, string> = {
  CRITICAL: "#e74c3c",
  HIGH: "#e67e22",
  MEDIUM: "#f1c40f",
  LOW: "#2ecc71",
};

const COMPONENT_LABEL: Record<string, string> = {
  pattern: "Pattern Detection",
  gnn: "XGBoost Classifier",
  anomaly: "Online Anomaly",
  compliance: "Compliance Rules",
};

interface Props {
  alertId: string;
  onClose: () => void;
}

export default function ExplainabilityCard({ alertId, onClose }: Props) {
  const [data, setData] = useState<ExplainData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!alertId) return;
    setLoading(true);
    api.get<ExplainData>(`/alerts/${alertId}/explain`)
      .then((r) => setData(r.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [alertId]);

  const riskColor = RISK_COLOR[data?.risk_level ?? "LOW"] ?? "#4b5563";

  const maxShap = data?.shap_features?.length
    ? Math.max(...data.shap_features.map((f) => Math.abs(f.shap_value)))
    : 1;

  const patterns = data
    ? Object.entries(data.pattern_matches ?? {}).filter(([, v]) => v).map(([k]) => k)
    : [];

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 1000,
        background: "rgba(0,0,0,0.75)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backdropFilter: "blur(3px)",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#100e0b",
          border: `1px solid ${riskColor}40`,
          borderRadius: 14,
          padding: 28,
          width: "min(680px, 95vw)",
          maxHeight: "88vh",
          overflow: "auto",
          boxShadow: `0 0 40px ${riskColor}30, 0 20px 60px rgba(0,0,0,0.8)`,
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 18, color: "#e6e8ee" }}>
              Why was this flagged?
            </h2>
            <div style={{ fontSize: 12, color: "#6b7280", marginTop: 4, fontFamily: "monospace" }}>
              {data?.account_id ?? alertId}
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {data?.risk_level && (
              <span
                style={{
                  padding: "4px 12px",
                  borderRadius: 20,
                  background: `${riskColor}20`,
                  color: riskColor,
                  fontWeight: 700,
                  fontSize: 13,
                  border: `1px solid ${riskColor}60`,
                  boxShadow: `0 0 10px ${riskColor}40`,
                }}
              >
                {data.risk_level}
              </span>
            )}
            <button
              onClick={onClose}
              style={{
                background: "none",
                border: "none",
                color: "#6b7280",
                cursor: "pointer",
                fontSize: 20,
                lineHeight: 1,
              }}
            >
              ×
            </button>
          </div>
        </div>

        {loading && (
          <div style={{ textAlign: "center", padding: 40, color: "#6b7280" }}>Loading explanation…</div>
        )}

        {!loading && data && (
          <>
            {/* Risk Score Breakdown */}
            <Section title="Risk Score Breakdown">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                {Object.entries(data.risk_contributions ?? {}).map(([key, val]) => (
                  <div key={key} style={{ background: "#120d08", borderRadius: 8, padding: "10px 12px" }}>
                    <div style={{ fontSize: 11, color: "#6b7280", marginBottom: 4 }}>
                      {COMPONENT_LABEL[key] ?? key}
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div
                        style={{
                          flex: 1,
                          height: 6,
                          background: "#2a1e0e",
                          borderRadius: 3,
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.min(100, val * 100 / 0.3)}%`,
                            height: "100%",
                            background: riskColor,
                            borderRadius: 3,
                            transition: "width 0.6s ease",
                          }}
                        />
                      </div>
                      <span style={{ fontSize: 12, color: "#d1d5db", minWidth: 36, textAlign: "right" }}>
                        {(val * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <div
                style={{
                  marginTop: 10,
                  padding: "8px 12px",
                  background: `${riskColor}15`,
                  borderRadius: 8,
                  border: `1px solid ${riskColor}30`,
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <span style={{ fontSize: 12, color: "#9ca3af" }}>Composite Score</span>
                <span style={{ fontSize: 16, fontWeight: 700, color: riskColor }}>
                  {(data.composite_score * 100).toFixed(1)}%
                </span>
              </div>
            </Section>

            {/* SHAP Feature Importances */}
            {data.shap_features?.length > 0 && (
              <Section title="SHAP Feature Importances">
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {data.shap_features.map((f) => {
                    const pct = Math.abs(f.shap_value) / maxShap;
                    const isPos = f.shap_value > 0;
                    return (
                      <div key={f.feature} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ fontSize: 11, color: "#9ca3af", minWidth: 160, textAlign: "right" }}>
                          {f.feature.replace(/_/g, " ")}
                        </span>
                        <div style={{ flex: 1, height: 12, background: "#2a1e0e", borderRadius: 4, overflow: "hidden", position: "relative" }}>
                          <div
                            style={{
                              width: `${pct * 100}%`,
                              height: "100%",
                              background: isPos ? "#e67e22" : "#2ecc71",
                              borderRadius: 4,
                              transition: "width 0.5s ease",
                            }}
                          />
                        </div>
                        <span style={{ fontSize: 11, color: isPos ? "#e67e22" : "#2ecc71", minWidth: 50, textAlign: "right" }}>
                          {isPos ? "+" : ""}{f.shap_value.toFixed(3)}
                        </span>
                      </div>
                    );
                  })}
                </div>
                <div style={{ fontSize: 10, color: "#374151", marginTop: 6 }}>
                  Orange = pushes toward fraud · Green = pushes toward clean
                </div>
              </Section>
            )}

            {/* Triggered Patterns */}
            {patterns.length > 0 && (
              <Section title="Triggered AML Patterns">
                <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                  {patterns.map((p) => (
                    <span
                      key={p}
                      style={{
                        padding: "4px 10px",
                        background: "#1c1208",
                        border: "1px solid #3a2010",
                        borderRadius: 8,
                        fontSize: 12,
                        color: "#fb923c",
                      }}
                    >
                      {p.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {/* LLM Explanation */}
            {data.llm_explanation && (
              <Section title="AI Analysis">
                <p
                  style={{
                    margin: 0,
                    fontSize: 13,
                    color: "#d1d5db",
                    lineHeight: 1.7,
                    fontStyle: "italic",
                    padding: "12px 14px",
                    background: "#0d0b08",
                    borderRadius: 8,
                    border: "1px solid #2a1e0e",
                  }}
                >
                  "{data.llm_explanation}"
                </p>
              </Section>
            )}

            {/* Compliance Rules */}
            {data.compliance_rules?.length > 0 && (
              <Section title="Compliance Rules Triggered">
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  {data.compliance_rules.map((r) => (
                    <div key={r.rule_id} style={{ display: "flex", justifyContent: "space-between", padding: "6px 10px", background: "#120d08", borderRadius: 6 }}>
                      <span style={{ fontSize: 12, color: "#d1d5db", fontFamily: "monospace" }}>{r.rule_id}</span>
                      <span style={{ fontSize: 11, color: RISK_COLOR[r.severity] ?? "#6b7280" }}>{r.severity}</span>
                    </div>
                  ))}
                </div>
              </Section>
            )}

            {/* Actions */}
            <div style={{ display: "flex", gap: 10, marginTop: 20, paddingTop: 16, borderTop: "1px solid #2a1e0e" }}>
              <STRDownload alertId={alertId} />
              <button
                onClick={onClose}
                style={{
                  padding: "6px 16px",
                  background: "#1a1510",
                  color: "#9ca3af",
                  border: "1px solid #2a1e0e",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontSize: 12,
                }}
              >
                Close
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <h4 style={{ margin: "0 0 10px", fontSize: 12, color: "#6b7280", textTransform: "uppercase", letterSpacing: 1 }}>
        {title}
      </h4>
      {children}
    </div>
  );
}
