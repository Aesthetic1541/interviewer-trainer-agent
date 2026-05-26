"""
History Routes
GET  /api/history/sessions          – All completed sessions
GET  /api/history/session/<id>      – Full session detail with Q&A
GET  /api/history/stats             – Aggregate stats across all sessions
DELETE /api/history/session/<id>    – Delete a session record
"""

import logging
from flask import Blueprint, request, jsonify

from backend.models.database import db, InterviewSession, SessionQuestion, ChatMessage

logger     = logging.getLogger(__name__)
history_bp = Blueprint("history", __name__)


# ── GET /api/history/sessions ─────────────────────────────────────────────────
@history_bp.route("/sessions", methods=["GET"])
def list_sessions():
    limit  = request.args.get("limit", 20, type=int)
    offset = request.args.get("offset", 0, type=int)

    sessions = (
        InterviewSession.query
        .order_by(InterviewSession.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return jsonify({
        "sessions": [s.to_dict() for s in sessions],
        "total":    InterviewSession.query.count(),
    })


# ── GET /api/history/session/<int:session_id> ─────────────────────────────────
@history_bp.route("/session/<int:session_id>", methods=["GET"])
def session_detail(session_id: int):
    session = InterviewSession.query.get_or_404(session_id)
    questions = (
        SessionQuestion.query
        .filter_by(session_id=session_id)
        .order_by(SessionQuestion.order_index)
        .all()
    )
    messages = (
        ChatMessage.query
        .filter_by(session_id=session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    # Compute category breakdown
    tech_qs = [q for q in questions if q.category == "technical"]
    hr_qs   = [q for q in questions if q.category == "hr"]

    def avg_score(qs):
        answered = [q for q in qs if q.answered]
        if not answered:
            return 0.0
        return round(sum(q.score for q in answered) / len(answered), 1)

    return jsonify({
        "session":           session.to_dict(),
        "questions":         [q.to_dict() for q in questions],
        "chat_messages":     [m.to_dict() for m in messages],
        "breakdown": {
            "technical_avg": avg_score(tech_qs),
            "hr_avg":        avg_score(hr_qs),
            "answered":      sum(1 for q in questions if q.answered),
            "total":         len(questions),
        },
    })


# ── GET /api/history/stats ────────────────────────────────────────────────────
@history_bp.route("/stats", methods=["GET"])
def aggregate_stats():
    sessions   = InterviewSession.query.all()
    completed  = [s for s in sessions if s.status == "completed"]
    all_scores = [s.score_pct for s in completed if s.max_score > 0]

    avg_score  = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0
    best_score = max(all_scores, default=0.0)
    worst_score= min(all_scores, default=0.0)

    # Role distribution
    from collections import Counter
    role_counts = dict(Counter(s.job_role for s in sessions).most_common(5))

    return jsonify({
        "total_sessions":    len(sessions),
        "completed":         len(completed),
        "in_progress":       len(sessions) - len(completed),
        "average_score_pct": avg_score,
        "best_score_pct":    best_score,
        "worst_score_pct":   worst_score,
        "top_roles":         role_counts,
    })


# ── DELETE /api/history/session/<int:session_id> ──────────────────────────────
@history_bp.route("/session/<int:session_id>", methods=["DELETE"])
def delete_session(session_id: int):
    session = InterviewSession.query.get_or_404(session_id)

    # Cascade-delete questions and messages
    SessionQuestion.query.filter_by(session_id=session_id).delete()
    ChatMessage.query.filter_by(session_id=session_id).delete()
    db.session.delete(session)
    db.session.commit()

    return jsonify({"message": f"Session {session_id} deleted."})