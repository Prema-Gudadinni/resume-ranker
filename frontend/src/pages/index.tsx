// src/pages/index.tsx
import React, { useState } from "react";
import { Toaster } from "react-hot-toast";
import Header from "../components/Header";
import UploadSection from "../components/UploadSection";
import RankingSection from "../components/RankingSection";
import ResultsSection from "../components/ResultsSection";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [jobDesc, setJobDesc] = useState<string>("");
  const [showJobInput, setShowJobInput] = useState(false);
  const [jobInput, setJobInput] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      <Toaster position="top-right" />
      
      <Header />

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <UploadSection 
            files={files}
            setFiles={setFiles}
            loading={loading}
            setLoading={setLoading}
          />
          
          <RankingSection
            loading={loading}
            setLoading={setLoading}
            setJobDesc={setJobDesc}
            setResults={setResults}
            showJobInput={showJobInput}
            setShowJobInput={setShowJobInput}
            jobInput={jobInput}
            setJobInput={setJobInput}
          />
        </div>

        <ResultsSection 
          results={results}
          jobDesc={jobDesc}
          loading={loading}
        />
      </div>
    </div>
  );
}
