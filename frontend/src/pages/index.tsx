// src/pages/index.tsx
import React, { useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [results, setResults] = useState<any[]>([]);

  async function handleUpload() {
    if (!files) return alert("Choose files");
    const fd = new FormData();
    // use a sample user/profile id from supabase for demo or let user sign in
    const userId = process.env.NEXT_PUBLIC_DEMO_USER_ID || "";
    for (let i = 0; i < files.length; i++) fd.append("file", files[i]);
    fd.append("user_id", userId);
    const resp = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE}/upload`, fd, {
      headers: {'Content-Type': 'multipart/form-data'}
    });
    alert("Uploaded");
  }

  async function handleRank() {
    const job = prompt("Enter job description / job title") || "";
    const resp = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE}/rank`, {
      job_title: "Hiring - " + job.slice(0, 30),
      job_description: job,
      created_by: process.env.NEXT_PUBLIC_DEMO_USER_ID || null
    });
    setResults(resp.data.results || []);
  }

  return (
    <div style={{ padding: 24 }}>
      <h1>AI Resume Ranker</h1>
      <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      <button onClick={handleUpload}>Upload</button>
      <button onClick={handleRank}>Rank</button>

      <div style={{ marginTop: 20 }}>
        {results.map((r: any) => (
          <div key={r.resume.id} style={{ borderBottom: "1px solid #ddd", padding: 8 }}>
            <strong>{r.resume.filename}</strong> — score: {(r.score*100).toFixed(2)}%
          </div>
        ))}
      </div>
    </div>
  );
}


