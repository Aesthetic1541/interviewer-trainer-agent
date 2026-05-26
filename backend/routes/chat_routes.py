"""
Chat Routes – Conversational Interview Mode
POST /api/chat/message   – Send a message to the AI interviewer
GET  /api/chat/history   – Get chat history for a session
POST /api/chat/reset     – Clear chat history for a session
"""

import logging
from flask import Blueprint, request, jsonify

from backend.models.database          import db, ChatMessage, InterviewSession
from backend.services.interview_service import InterviewService

logger  = logging.getLogger(__name__)
chat_bp = Blueprint("chat", __name__)
svc     = InterviewService()


# ── POST /api/chat/message ────────────────────────────────────────────────────
@chat_bp.route("/message", methods=["POST"])
def chat_message():
    """
    Body (JSON):
        session_id  : int   (required)
        message     : str   (required)
        job_role    : str   (optional, fallback to session)
        experience  : str   (optional, fallback to session)
    """
    data       = request.get_json(force=True)
    session_id = data.get("session_id")
    message    = data.get("message", "").strip()

    if not session_id or not message:
        return jsonify({"error": "session_id and message are required."}), 400

    # Load session context
    session = InterviewSession.query.get(session_id)
    if not session:
        return jsonify({"error": "Session not found."}), 404

    job_role   = data.get("job_role")   or session.job_role
    experience = data.get("experience") or session.experience

    # Load chat history
    history_rows = ChatMessage.query.filter_by(
        session_id=session_id
    ).order_by(ChatMessage.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in history_rows]

    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=message)
    db.session.add(user_msg)
    db.session.flush()

    # Get AI response
    try:
        ai_response = svc.chat_interview(
            session_id   = session_id,
            user_message = message,
            history      = history,
            job_role     = job_role,
            experience   = experience,
        )
    except Exception as exc:
        logger.error(f"Chat error: {exc}")
        ai_response = (
            "I appreciate your response. Let's continue — could you walk me through "
            "a specific example from your experience that demonstrates this skill?"
        )

    # Save assistant message
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=ai_response)
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        "session_id": session_id,
        "user_message": message,
        "ai_response":  ai_response,
        "message_id":   ai_msg.id,
    })


# ── GET /api/chat/history ─────────────────────────────────────────────────────
@chat_bp.route("/history", methods=["GET"])
def chat_history():
    """Query params: session_id"""
    session_id = request.args.get("session_id", type=int)
    if not session_id:
        return jsonify({"error": "session_id required."}), 400

    messages = ChatMessage.query.filter_by(
        session_id=session_id
    ).order_by(ChatMessage.created_at).all()

    return jsonify({
        "session_id": session_id,
        "messages":   [m.to_dict() for m in messages],
        "count":      len(messages),
    })


# ── POST /api/chat/reset ──────────────────────────────────────────────────────
@chat_bp.route("/reset", methods=["POST"])
def reset_chat():
    """Body: {"session_id": int}"""
    data       = request.get_json(force=True)
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required."}), 400

    deleted = ChatMessage.query.filter_by(session_id=session_id).delete()
    db.session.commit()
    return jsonify({"message": f"Cleared {deleted} messages for session {session_id}."})