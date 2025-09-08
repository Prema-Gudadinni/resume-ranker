"use client";
import React, { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import toast, { Toaster } from "react-hot-toast";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Handle resume upload
  async function handleUpload() {
    if (!files) {
      toast.error("Please select resumes first!");
      return;
    }
    try {
      setLoading(true);
      const fd = new FormData();
      const userId = process.env.NEXT_PUBLIC_DEMO_USER_ID || "";
      for (let i = 0; i < files.length; i++) fd.append("file", files[i]);
      fd.append("user_id", userId);

      await axios.post(`${process.env.NEXT_PUBLIC_API_BASE}/upload`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast.success("Resumes uploaded successfully!");
    } catch (err) {
      toast.error("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  // Handle resume ranking
  async function handleRank() {
    const job = prompt("Enter job description / job title") || "";
    if (!job) return;

    try {
      setLoading(true);
      const resp = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE}/rank`, {
        job_title: "Hiring - " + job.slice(0, 30),
        job_description: job,
        created_by: process.env.NEXT_PUBLIC_DEMO_USER_ID || null,
      });

      setResults(resp.data.results || []);
      toast.success("Resumes ranked successfully!");
    } catch (err) {
      toast.error("Failed to rank resumes.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-white to-blue-200 flex flex-col items-center py-10 px-6">
      <Toaster position="top-center" />

      {/* Heading */}
      <motion.h1
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-4xl md:text-5xl font-bold text-gray-800 mb-4"
      >
        AI Resume Ranker
      </motion.h1>
      <p className="text-gray-600 text-lg mb-8 text-center max-w-2xl">
        Upload multiple resumes, enter the job description, and let AI rank them based on suitability.
      </p>

      {/* File Upload */}
      <div className="flex flex-col items-center bg-white shadow-lg rounded-2xl p-6 border border-gray-200 w-full max-w-lg">
        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          className="border-2 border-dashed border-gray-300 p-4 rounded-lg w-full cursor-pointer hover:border-blue-400"
        />
        <motion.button
          onClick={handleUpload}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={loading}
          className={`mt-4 w-full py-3 px-6 rounded-xl font-semibold transition-colors duration-300 ${
            loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          {loading ? "Uploading..." : "Upload Resumes"}
        </motion.button>

        <motion.button
          onClick={handleRank}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          disabled={loading}
          className={`mt-3 w-full py-3 px-6 rounded-xl font-semibold transition-colors duration-300 ${
            loading ? "bg-gray-400 cursor-not-allowed" : "bg-green-600 text-white hover:bg-green-700"
          }`}
        >
          {loading ? "Ranking..." : "Rank Resumes"}
        </motion.button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="mt-10 w-full max-w-3xl bg-white rounded-xl shadow-xl p-6 border border-gray-100">
          <h2 className="text-2xl font-bold mb-4">Ranking Results</h2>
          <div className="space-y-4">
            {results.map((r: any, idx: number) => (
              <motion.div
                key={r.resume.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.1 }}
                className="bg-gray-50 rounded-lg p-4 shadow border border-gray-200 flex items-center justify-between"
              >
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">
                    {r.resume.filename}
                  </h3>
                  <p className="text-gray-600">
                    Score: <span className="font-bold">{(r.score * 100).toFixed(2)}%</span>
                  </p>
                </div>
                <div className="w-40 bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{ width: `${r.score * 100}%` }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

