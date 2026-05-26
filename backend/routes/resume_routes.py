"""
Resume Routes
POST /api/resume/upload   – Upload and parse a PDF resume
GET  /api/resume/<id>     – Get parsed resume data
GET  /api/resume/list     – List all resumes
DELETE /api/resume/<id>   – Delete a resume
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from backend.models.database    import db, Resume
from backend.services.resume_service import ResumeParser
from backend.services.rag_service    import get_rag

logger    = logger = logging.getLogger(__name__)
resume_bp = Blueprint("resume", __name__)
parser    = ResumeParser()

ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── POST /api/resume/upload ───────────────────────────────────────────────────
@resume_bp.route("/upload", methods=["POST"])
def upload_resume():
    """
    Accept a resume file (multipart/form-data).
    Parse it and store results in SQLite.
    Returns parsed data + resume_id for use in interview sessions.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use key 'file' in form-data."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type. Use PDF or TXT."}), 415

    # Save file
    filename   = secure_filename(file.filename)
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file_path  = os.path.join(upload_dir, filename)
    file.save(file_path)

    # Parse
    try:
        parsed = parser.parse_file(file_path)
    except Exception as exc:
        logger.error(f"Resume parse error: {exc}")
        return jsonify({"error": f"Failed to parse resume: {str(exc)}"}), 500

    if "error" in parsed:
        return jsonify(parsed), 422

    # Persist to DB
    resume = Resume(
        filename       = filename,
        file_path      = file_path,
        raw_text       = parsed["raw_text"][:50000],   # cap at 50k chars
        parsed_skills  = json.dumps(parsed["skills"]),
        parsed_exp     = json.dumps(parsed["experience"]),
        parsed_edu     = json.dumps(parsed["education"]),
        experience_yrs = parsed["experience_yrs"],
        job_title      = parsed["job_title"],
    )
    db.session.add(resume)
    db.session.commit()

    # Index resume in RAG vector store
    try:
        rag = get_rag()
        rag.index_resume(parsed["raw_text"], parsed["job_title"])
    except Exception as exc:
        logger.warning(f"RAG indexing skipped: {exc}")

    return jsonify({
        "message":    "Resume uploaded and parsed successfully.",
        "resume_id":  resume.id,
        "filename":   resume.filename,
        "parsed":     resume.to_dict(),
    }), 201


# ── GET /api/resume/<int:resume_id> ──────────────────────────────────────────
@resume_bp.route("/<int:resume_id>", methods=["GET"])
def get_resume(resume_id: int):
    resume = Resume.query.get_or_404(resume_id)
    return jsonify(resume.to_dict())


# ── GET /api/resume/list ──────────────────────────────────────────────────────
@resume_bp.route("/list", methods=["GET"])
def list_resumes():
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).limit(20).all()
    return jsonify([r.to_dict() for r in resumes])


# ── DELETE /api/resume/<int:resume_id> ───────────────────────────────────────
@resume_bp.route("/<int:resume_id>", methods=["DELETE"])
def delete_resume(resume_id: int):
    resume = Resume.query.get_or_404(resume_id)
    # Remove file
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    db.session.delete(resume)
    db.session.commit()
    return jsonify({"message": f"Resume {resume_id} deleted."})


# ── GET /api/resume/job-roles ─────────────────────────────────────────────────
@resume_bp.route("/job-roles", methods=["GET"])
def get_job_roles():
    """Return list of supported job roles."""
    roles = [
        "Software Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "DevOps Engineer",
        "Cloud Architect",
        "Product Manager",
        "Data Analyst",
        "Android Developer",
        "iOS Developer",
        "QA Engineer",
        "Cybersecurity Analyst",
        "Database Administrator",
    ]
    return jsonify({"roles": roles})