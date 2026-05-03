/**
 * STRDownload — one-click FIU-IND STR PDF download for an alert.
 */
export default function STRDownload({ alertId }: { alertId: string }) {
  const url = `/api/reports/str/${alertId}`;
  return (
    <a href={url} target="_blank" rel="noreferrer" style={{ color: "#7aa2ff" }}>
      Download STR (FIU-IND PDF) →
    </a>
  );
}
