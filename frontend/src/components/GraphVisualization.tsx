import { useGraphData } from "../hooks/useGraphData";

export default function GraphVisualization() {
  const { data, loading } = useGraphData();
  return (
    <div style={{ position: "relative", borderRadius: 8, background: "#11141d", overflow: "hidden" }}>
      {loading && <div style={{ position: "absolute", top: 12, left: 12 }}>Loading graph…</div>}
      {/* TODO(frontend): wire react-force-graph-3d here using `data` */}
      <pre style={{ padding: 12, fontSize: 12 }}>{JSON.stringify(data?.summary ?? {}, null, 2)}</pre>
    </div>
  );
}
