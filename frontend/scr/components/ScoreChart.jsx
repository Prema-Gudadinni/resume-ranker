// frontend/src/components/ScoreChart.jsx
import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ScoreChart({ data }) {
  const chartData = data.map((d) => ({ name: d.name, score: d.score }));
  return (
    <div style={{ width: "100%", height: 240, marginTop: 18 }}>
      <ResponsiveContainer>
        <BarChart data={chartData}>
          <XAxis dataKey="name" stroke="#9ca3af" />
          <YAxis stroke="#9ca3af" />
          <Tooltip />
          <Bar dataKey="score" fill="#6366f1" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
