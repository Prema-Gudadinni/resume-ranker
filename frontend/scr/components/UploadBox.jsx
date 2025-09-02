// frontend/src/components/UploadBox.jsx
import React from "react";

export default function UploadBox({ onUpload }) {
  const handleChange = (e) => {
    if (e.target.files.length === 0) return;
    onUpload(e.target.files);
  };
  return (
    <div style={{ marginBottom: 12 }}>
      <input type="file" multiple onChange={handleChange} />
      <p style={{ color: "#9ca3af" }}>Upload PDFs or TXT resumes</p>
    </div>
  );
}
