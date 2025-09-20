// src/pages/index.tsx
import React, { useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [jobDesc, setJobDesc] = useState<string>("");

  async function handleUpload() {
    if (!files) return alert("Choose files first");
    setLoading(true);

    try {
      const fd = new FormData();
      const userId = process.env.NEXT_PUBLIC_DEMO_USER_ID || "";
      for (let i = 0; i < files.length; i++) {
        fd.append("file", files[i]);
      }
      fd.append("user_id", userId);

      await axios.post(`${process.env.NEXT_PUBLIC_API_BASE}/upload`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert("Uploaded resumes successfully ✅");
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload failed ❌ — check backend logs.");
    } finally {
      setLoading(false);
    }
  }

  async function handleRank() {
    const job = prompt("Enter job description / job title") || "";
    if (!job.trim()) return;

    setLoading(true);
    setJobDesc(job);

    try {
      const resp = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE}/rank`,
        {
          job_title: "Hiring - " + job.slice(0, 30),
          job_description: job,
          created_by: process.env.NEXT_PUBLIC_DEMO_USER_ID || null,
        }
      );

      if (resp.data?.results) {
        setResults(resp.data.results);
      } else {
        alert("No ranking results returned ❌");
        setResults([]);
      }
    } catch (err) {
      console.error("Rank error:", err);
      alert("Ranking failed ❌ — check backend logs.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 24 }}>
      <h1>AI Resume Ranker</h1>

      <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      <button onClick={handleRank} disabled={loading}>
        {loading ? "Ranking..." : "Rank"}
      </button>

      {jobDesc && (
        <div style={{ marginTop: 20 }}>
          <h3>Job Description:</h3>
          <p>{jobDesc}</p>
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        {results.length > 0 ? (
          results.map((r: any, idx: number) => (
            <div
              key={r.resume?.id || idx}
              style={{
                borderBottom: "1px solid #ddd",
                padding: 8,
                marginBottom: 4,
              }}
            >
              <strong>{r.resume?.filename || "Unknown resume"}</strong> — score:{" "}
              {(r.score * 100).toFixed(2)}%
            </div>
          ))
        ) : (
          <p>No results yet</p>
        )}
      </div>
    </div>
  );
}
