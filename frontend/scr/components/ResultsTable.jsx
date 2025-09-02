// frontend/src/components/ResultsTable.jsx
import React from "react";

export default function ResultsTable({ data }) {
  return (
    <table style={{ width: "100%", marginTop: 12, borderCollapse: "collapse" }}>
      <thead>
        <tr>
          <th style={{ textAlign: "left" }}>Resume</th>
          <th style={{ textAlign: "left" }}>Score (%)</th>
          <th style={{ textAlign: "left" }}>Note</th>
        </tr>
      </thead>
      <tbody>
        {data.map((r, i) => (
          <tr key={i} style={{ borderTop: "1px solid #111827" }}>
            <td>{r.name}</td>
            <td>{r.score}</td>
            <td>{r.note || ""}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
