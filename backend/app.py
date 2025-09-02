# backend/app.py

import os
import logging
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from model import rank_resumes, extract_text  # local functions

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_MB = 25
ALLOWED_EXTENSIONS = {".pdf", ".txt"}

# ---------------- APP SETUP ----------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024  # Limit file size
CORS(app)  # Enable Cross-Origin Resource Sharing

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("server.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# ---------------- ERROR HANDLER ----------------
@app.errorhandler(Exception)
def handle_exception(e):
    """Global error handler"""
    logger.exception("Unhandled exception occurred")
    return jsonify({
        "error": str(e),
        "trace": traceback.format_exc()
    }), 500

# ---------------- HEALTH CHECK ROUTE ----------------
@app.route("/health", methods=["GET"])
def health():
    """Check server health"""
    logger.info("Health check requested")
    return jsonify({"status": "ok"}), 200

# ---------------- RESUME RANKING ROUTE ----------------
@app.route("/rank", methods=["POST"])
def rank():
    """Uploads resumes, extracts text, and ranks candidates"""
    files = request.files.getlist("files")

    if not files:
        logger.warning("No files uploaded")
        return jsonify({"error": "No files provided"}), 400

    saved_files = []
    for file in files:
        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        # Check allowed extensions
        if ext not in ALLOWED_EXTENSIONS:
            logger.warning("Rejected file due to unsupported extension: %s", filename)
            continue

        # Save file
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)
        logger.info("Saved file: %s (%d bytes)", save_path, os.path.getsize(save_path))

        # Optional: Verify text extraction
        extracted_text = extract_text(save_path)
        if not extracted_text.strip():
            logger.warning("No extractable text found in: %s", save_path)

        saved_files.append(save_path)

    if not saved_files:
        logger.error("No valid resumes found")
        return jsonify({"error": "No valid resumes uploaded"}), 400

    # Rank resumes using your model function
    try:
        results = rank_resumes(app.config["UPLOAD_FOLDER"])
        logger.info("Ranking completed successfully")
        return jsonify(results), 200
    except Exception as e:
        logger.exception("Error while ranking resumes")
        return jsonify({"error": str(e)}), 500

# ---------------- START SERVER ----------------
if __name__ == "__main__":
    logger.info("Starting Flask server...")
    app.run(host="127.0.0.1", port=5000, debug=True)
