"""
Interview Routes
POST /api/interview/start          – Create a new session + generate questions
GET  /api/interview/<session_id>   – Get session + questions
POST /api/interview/answer         – Submit answer, get feedback + score
POST /api/interview/complete       – Finalize session score
GET  /api/interview/model-answer   – Get model answer for a question
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from backend.models.database          import db, InterviewSession, SessionQuestion, Resume
from backend.services.interview_service import InterviewService
from backend.services.rag_service       import get_rag

logger       = logging.getLogger(__name__)
interview_bp = Blueprint("interview", __name__)
svc          = InterviewService()


# ── POST /api/interview/start ─────────────────────────────────────────────────
@interview_bp.route("/start", methods=["POST"])
def start_session():
    """
    Body (JSON):
        job_role    : str  (required)
        experience  : str  junior|mid|senior  (required)
        resume_id   : int  (optional)
        num_technical: int (default 5)
        num_hr       : int (default 5)
    """
    data = request.get_json(force=True)
    job_role   = data.get("job_role", "").strip()
    experience = data.get("experience", "mid").strip()
    resume_id  = data.get("resume_id")
    num_tech   = int(data.get("num_technical", 5))
    num_hr     = int(data.get("num_hr", 5))

    if not job_role:
        return jsonify({"error": "job_role is required."}), 400

    # Fetch resume text if provided
    resume_text = ""
    if resume_id:
        resume = Resume.query.get(resume_id)
        if resume:
            resume_text = resume.raw_text or ""

    # Ensure question bank is indexed
    try:
        rag = get_rag()
        if not rag._vector_store:
            rag.index_question_bank()
    except Exception as exc:
        logger.warning(f"RAG index warning: {exc}")

    # Generate questions via RAG + Granite
    questions_data = svc.generate_questions(
        job_role=job_role,
        experience=experience,
        resume_text=resume_text,
        num_technical=num_tech,
        num_hr=num_hr,
    )

    # Create session
    session = InterviewSession(
        job_role   = job_role,
        experience = experience,
        resume_id  = resume_id,
        status     = "in_progress",
    )
    db.session.add(session)
    db.session.flush()   # get session.id

    # Persist questions
    order = 0
    session_questions = []
    for q_text in questions_data.get("technical", []):
        model_ans = svc.get_model_answer(q_text, job_role, experience)
        sq = SessionQuestion(
            session_id    = session.id,
            question_text = q_text,
            category      = "technical",
            model_answer  = model_ans,
            order_index   = order,
        )
        db.session.add(sq)
        session_questions.append(sq)
        order += 1

    for q_text in questions_data.get("hr", []):
        model_ans = svc.get_model_answer(q_text, job_role, experience)
        sq = SessionQuestion(
            session_id    = session.id,
            question_text = q_text,
            category      = "hr",
            model_answer  = model_ans,
            order_index   = order,
        )
        db.session.add(sq)
        session_questions.append(sq)
        order += 1

    db.session.commit()

    return jsonify({
        "message":    "Interview session started.",
        "session_id": session.id,
        "session":    session.to_dict(),
        "questions":  [q.to_dict() for q in session_questions],
    }), 201


# ── GET /api/interview/<int:session_id> ───────────────────────────────────────
@interview_bp.route("/<int:session_id>", methods=["GET"])
def get_session(session_id: int):
    session = InterviewSession.query.get_or_404(session_id)
    questions = SessionQuestion.query.filter_by(
        session_id=session_id
    ).order_by(SessionQuestion.order_index).all()

    return jsonify({
        "session":   session.to_dict(),
        "questions": [q.to_dict() for q in questions],
    })


# ── POST /api/interview/answer ────────────────────────────────────────────────
@interview_bp.route("/answer", methods=["POST"])
def submit_answer():
    """
    Body (JSON):
        question_id  : int
        user_answer  : str
    """
    data        = request.get_json(force=True)
    question_id = data.get("question_id")
    user_answer = data.get("user_answer", "").strip()

    if not question_id or not user_answer:
        return jsonify({"error": "question_id and user_answer are required."}), 400

    sq = SessionQuestion.query.get_or_404(question_id)
    session = InterviewSession.query.get_or_404(sq.session_id)

    # Evaluate with Granite
    feedback = svc.evaluate_answer(
        question     = sq.question_text,
        user_answer  = user_answer,
        model_answer = sq.model_answer or "",
        job_role     = session.job_role,
        category     = sq.category,
    )

    score = min(10.0, max(0.0, float(feedback.get("score", 5))))

    # Update DB
    sq.user_answer = user_answer
    sq.ai_feedback = json.dumps(feedback)
    sq.score       = score
    sq.answered    = True
    db.session.commit()

    return jsonify({
        "question_id": question_id,
        "score":       score,
        "max_score":   sq.max_score,
        "feedback":    feedback,
    })


# ── POST /api/interview/complete ──────────────────────────────────────────────
@interview_bp.route("/complete", methods=["POST"])
def complete_session():
    """Body: {"session_id": int}"""
    data       = request.get_json(force=True)
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required."}), 400

    result = svc.compute_session_score(session_id)
    return jsonify(result)


# ── GET /api/interview/model-answer ──────────────────────────────────────────
@interview_bp.route("/model-answer", methods=["GET"])
def model_answer():
    """Query params: question, job_role, experience"""
    question   = request.args.get("question", "")
    job_role   = request.args.get("job_role", "Software Engineer")
    experience = request.args.get("experience", "mid")
    if not question:
        return jsonify({"error": "question param required."}), 400
    answer = svc.get_model_answer(question, job_role, experience)
    return jsonify({"model_answer": answer})


# ── GET /api/interview/health ─────────────────────────────────────────────────
@interview_bp.route("/health", methods=["GET"])
def health():
    from backend.services.llm_service import get_llm
    llm = get_llm()
    return jsonify({"status": "ok", "llm": llm.health_check()})