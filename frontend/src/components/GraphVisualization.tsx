import { useCallback, useEffect, useRef } from "react";
import ForceGraph3D from "react-force-graph-3d";
import * as THREE from "three";
import { useGraphData } from "../hooks/useGraphData";

const RISK_COLOR: Record<string, string> = {
  CRITICAL: "#e74c3c",
  HIGH: "#e67e22",
  MEDIUM: "#f1c40f",
  LOW: "#2ecc71",
  UNKNOWN: "#4b5563",
};

interface Props {
  focusAccountId?: string | null;
  onNodeClick?: (accountId: string) => void;
}

export default function GraphVisualization({ focusAccountId, onNodeClick }: Props) {
  const { data, loading } = useGraphData(focusAccountId ?? undefined);
  const graphRef = useRef<any>(null);
  const fittedRef = useRef(false);

  const handleEngineStop = useCallback(() => {
    if (!fittedRef.current && graphRef.current) {
      graphRef.current.zoomToFit(800, 60);
      fittedRef.current = true;
    }
  }, []);

  useEffect(() => {
    fittedRef.current = false;
  }, [data?.nodes.length]);

  const nodeColor = useCallback((node: any) => {
    return RISK_COLOR[node.risk_level as string] ?? RISK_COLOR.UNKNOWN;
  }, []);

  const nodeVal = useCallback((node: any) => {
    const risk = node.risk_level as string;
    if (risk === "CRITICAL") return 6;
    if (risk === "HIGH") return 4;
    if (risk === "MEDIUM") return 2.5;
    return 1.5;
  }, []);

  const linkColor = useCallback((link: any) => {
    const amount = Number(link.amount ?? 0);
    if (amount >= 1_000_000) return "rgba(231,76,60,0.6)";
    if (amount >= 500_000) return "rgba(230,126,34,0.5)";
    return "rgba(99,102,241,0.2)";
  }, []);

  const linkWidth = useCallback((link: any) => {
    const amount = Number(link.amount ?? 0);
    if (amount >= 1_000_000) return 2;
    if (amount >= 500_000) return 1.2;
    return 0.4;
  }, []);

  const handleNodeClick = useCallback(
    (node: any) => {
      onNodeClick?.(node.id as string);
      graphRef.current?.cameraPosition(
        { x: node.x, y: node.y, z: (node.z ?? 0) + 120 },
        { x: node.x, y: node.y, z: node.z ?? 0 },
        600
      );
    },
    [onNodeClick]
  );

  const nodeThreeObject = useCallback(
    (node: any) => {
      const risk = (node.risk_level as string) ?? "UNKNOWN";
      const radius = nodeVal(node) * 1.5;
      const color = nodeColor(node);
      const geometry = new THREE.SphereGeometry(radius, 16, 16);
      const material = new THREE.MeshLambertMaterial({
        color,
        emissive: color,
        emissiveIntensity: risk === "CRITICAL" ? 0.6 : 0.3,
      });
      const sphere = new THREE.Mesh(geometry, material);
      if (risk === "CRITICAL" || risk === "HIGH") {
        const light = new THREE.PointLight(color, 2, 40);
        sphere.add(light);
      }
      return sphere;
    },
    [nodeColor, nodeVal]
  );

  const graphData = data
    ? { nodes: data.nodes, links: data.links }
    : { nodes: [], links: [] };

  return (
    <div
      style={{
        position: "relative",
        borderRadius: 12,
        background: "radial-gradient(ellipse at center, #0d1117 0%, #0b0d12 100%)",
        overflow: "hidden",
        border: "1px solid #1c1f2a",
        height: "100%",
        minHeight: 400,
      }}
    >
      {/* Risk legend */}
      <div style={{ position: "absolute", top: 12, left: 12, zIndex: 10, display: "flex", gap: 8, flexWrap: "wrap" }}>
        {["CRITICAL", "HIGH", "MEDIUM", "LOW"].map((risk) => (
          <span
            key={risk}
            style={{
              fontSize: 10,
              display: "flex",
              alignItems: "center",
              gap: 4,
              background: "rgba(0,0,0,0.55)",
              padding: "3px 8px",
              borderRadius: 20,
              border: `1px solid ${RISK_COLOR[risk]}40`,
              backdropFilter: "blur(4px)",
            }}
          >
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: "50%",
                background: RISK_COLOR[risk],
                display: "inline-block",
                boxShadow: `0 0 6px ${RISK_COLOR[risk]}`,
              }}
            />
            {risk}
          </span>
        ))}
      </div>

      {/* Stats badge */}
      {data?.summary && (
        <div
          style={{
            position: "absolute",
            top: 12,
            right: 12,
            zIndex: 10,
            fontSize: 11,
            color: "#6b7280",
            background: "rgba(0,0,0,0.55)",
            padding: "4px 10px",
            borderRadius: 6,
            backdropFilter: "blur(4px)",
          }}
        >
          {data.summary.total_nodes} nodes · {data.summary.total_edges} edges
          {data.summary.flagged_nodes > 0 && (
            <span style={{ color: "#e67e22", marginLeft: 6 }}>· {data.summary.flagged_nodes} flagged</span>
          )}
        </div>
      )}

      {/* Loading overlay */}
      {loading && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(11,13,18,0.85)",
            zIndex: 20,
            flexDirection: "column",
            gap: 14,
          }}
        >
          <div
            style={{
              width: 36,
              height: 36,
              border: "3px solid #1c1f2a",
              borderTop: "3px solid #f97316",
              borderRadius: "50%",
              animation: "spin 0.8s linear infinite",
            }}
          />
          <span style={{ color: "#6b7280", fontSize: 13 }}>Loading transaction graph…</span>
        </div>
      )}

      {!loading && (
        <ForceGraph3D
          ref={graphRef}
          graphData={graphData}
          nodeColor={nodeColor}
          nodeVal={nodeVal}
          linkColor={linkColor}
          linkWidth={linkWidth}
          nodeThreeObject={nodeThreeObject}
          onNodeClick={handleNodeClick}
          backgroundColor="rgba(0,0,0,0)"
          nodeLabel={(node: any) =>
            `${node.id}\nRisk: ${node.risk_level ?? "LOW"} | KYC: ${node.kyc_risk ?? "LOW"}`
          }
          linkLabel={(link: any) =>
            `₹${Number(link.amount ?? 0).toLocaleString("en-IN")} · ${link.channel ?? ""}`
          }
          enableNodeDrag
          enableNavigationControls
          showNavInfo={false}
          warmupTicks={30}
          cooldownTime={3000}
          onEngineStop={handleEngineStop}
        />
      )}
    </div>
  );
}
