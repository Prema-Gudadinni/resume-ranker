// frontend/src/App.jsx
import React, { useState } from "react";
import axios from "axios";
import UploadBox from "./components/UploadBox";
import ResultsTable from "./components/ResultsTable";
import ScoreChart from "./components/ScoreChart";
import "./index.css";

export default function App() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleUpload(files) {
    const fd = new FormData();
    for (let f of files) fd.append("files", f);
    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:5000/rank", fd, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setResults(res.data);
    } catch (e) {
      alert("Upload failed: " + (e.response?.data?.error || e.message));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>AI Resume Ranker</h1>
      <div className="card">
        <UploadBox onUpload={handleUpload} />
        {loading && <p>Processing...</p>}
        {results.length > 0 && (
          <>
            <ResultsTable data={results} />
            <ScoreChart data={results} />
          </>
        )}
      </div>
    </div>
  );
}
