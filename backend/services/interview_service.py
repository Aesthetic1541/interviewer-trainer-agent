"""
Interview Service
Generates interview questions via RAG + IBM Granite,
evaluates user answers, and computes session scores.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from backend.services.llm_service   import get_llm
from backend.services.rag_service   import get_rag
from backend.prompts.prompt_templates import (
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    CHATBOT_INTERVIEW_PROMPT,
)

logger = logging.getLogger(__name__)


class InterviewService:
    """Orchestrates end-to-end interview preparation logic."""

    def __init__(self):
        self._llm = get_llm()
        self._rag = get_rag()

    # ── 1. Generate question set ───────────────────────────────────────────────
    def generate_questions(
        self,
        job_role:       str,
        experience:     str,
        resume_text:    str = "",
        num_technical:  int = 5,
        num_hr:         int = 5,
    ) -> Dict[str, List[str]]:
        """
        Use RAG to retrieve relevant context then ask Granite to generate
        a tailored question set.

        Returns:
            {"technical": [...], "hr": [...]}
        """
        # Step 1: RAG retrieval
        query   = f"{job_role} {experience} interview questions"
        context = self._rag.retrieve(query, k=8)
        context_text = "\n".join(
            [f"- {c['text'][:300]}" for c in context[:6]]
        ) or "No specific context available."

        # Step 2: Build prompt
        prompt = QUESTION_GENERATION_PROMPT.format(
            job_role=job_role,
            experience=experience,
            resume_summary=resume_text[:800] if resume_text else "Not provided",
            context=context_text,
            num_technical=num_technical,
            num_hr=num_hr,
        )

        # Step 3: Call Granite
        raw = self._llm.generate(prompt)

        # Step 4: Parse JSON response
        return self._parse_questions(raw, job_role, experience)

    # ── 2. Get model answer for a question ────────────────────────────────────
    def get_model_answer(self, question: str, job_role: str, experience: str) -> str:
        """Retrieve or generate a model answer for a given question."""
        # Try DB first
        from backend.models.database import QuestionBank
        match = QuestionBank.query.filter(
            QuestionBank.question.ilike(f"%{question[:60]}%"),
        ).first()
        if match and match.model_answer:
            return match.model_answer

        # Otherwise ask Granite
        context_docs = self._rag.retrieve(question, k=3)
        ctx = "\n".join(d["text"][:200] for d in context_docs)
        prompt = (
            f"You are an expert {job_role} interviewer.\n"
            f"Provide a strong model answer for a {experience}-level candidate.\n\n"
            f"Question: {question}\n\n"
            f"Relevant context:\n{ctx}\n\n"
            f"Model Answer (3-5 sentences, structured and professional):"
        )
        return self._llm.generate(prompt)

    # ── 3. Evaluate a candidate's answer ──────────────────────────────────────
    def evaluate_answer(
        self,
        question:     str,
        user_answer:  str,
        model_answer: str,
        job_role:     str,
        category:     str,
    ) -> Dict:
        """
        Ask Granite to score and provide feedback on `user_answer`.

        Returns:
            {"score": int, "strengths": [...], "improvements": [...], "model_tip": str}
        """
        prompt = ANSWER_EVALUATION_PROMPT.format(
            job_role=job_role,
            category=category,
            question=question,
            user_answer=user_answer,
            model_answer=model_answer,
        )
        raw = self._llm.generate(prompt)
        return self._parse_feedback(raw)

    # ── 4. Chatbot interview turn ──────────────────────────────────────────────
    def chat_interview(
        self,
        session_id:    int,
        user_message:  str,
        history:       List[Dict],
        job_role:      str,
        experience:    str,
    ) -> str:
        """
        Conduct a conversational mock interview.
        `history` is a list of {"role": "user"/"assistant", "content": ...}
        """
        # Build history string
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in history[-8:]
        )

        # Retrieve relevant context
        ctx_docs = self._rag.retrieve(user_message, k=3)
        context  = "\n".join(d["text"][:200] for d in ctx_docs)

        prompt = CHATBOT_INTERVIEW_PROMPT.format(
            job_role=job_role,
            experience=experience,
            history=history_text,
            user_message=user_message,
            context=context,
        )
        return self._llm.generate(prompt)

    # ── 5. Finalize session score ──────────────────────────────────────────────
    def compute_session_score(self, session_id: int) -> Dict:
        """
        Aggregate scores from all answered SessionQuestion rows
        and update the InterviewSession record.
        """
        from backend.models.database import db, InterviewSession, SessionQuestion

        session = InterviewSession.query.get(session_id)
        if not session:
            return {"error": "Session not found"}

        questions = SessionQuestion.query.filter_by(
            session_id=session_id, answered=True
        ).all()

        total_score = sum(q.score     for q in questions)
        max_score   = sum(q.max_score for q in questions)

        session.total_score  = total_score
        session.max_score    = max_score
        session.status       = "completed"
        session.completed_at = datetime.utcnow()
        db.session.commit()

        return {
            "total_score": total_score,
            "max_score":   max_score,
            "score_pct":   session.score_pct,
            "grade":       self._grade(session.score_pct),
        }

    # ── Internal parsers ───────────────────────────────────────────────────────
    def _parse_questions(self, raw: str, job_role: str, experience: str) -> Dict:
        """Parse JSON from Granite response, fallback to DB lookup on failure."""
        try:
            data = json.loads(raw)
            if "technical" in data and "hr" in data:
                return data
        except Exception:
            pass

        # Try to extract JSON block from prose response
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if "technical" in data and "hr" in data:
                    return data
            except Exception:
                pass

        # Fallback: fetch from question bank
        return self._fallback_questions(job_role, experience)

    def _fallback_questions(self, job_role: str, experience: str) -> Dict:
        """Return questions from the local question bank as a fallback."""
        from backend.models.database import QuestionBank

        def fetch(cat):
            qs = QuestionBank.query.filter(
                QuestionBank.job_role.ilike(f"%{job_role}%"),
                QuestionBank.category == cat,
            ).limit(5).all()
            if not qs:
                qs = QuestionBank.query.filter_by(category=cat).limit(5).all()
            return [q.question for q in qs]

        return {
            "technical": fetch("technical") or ["Explain your technical background."],
            "hr":        fetch("hr")        or ["Tell me about yourself."],
        }

    def _parse_feedback(self, raw: str) -> Dict:
        """Parse score + feedback JSON from Granite response."""
        try:
            data = json.loads(raw)
            data.setdefault("score", 5)
            data.setdefault("strengths", [])
            data.setdefault("improvements", [])
            data.setdefault("model_tip", "")
            return data
        except Exception:
            pass

        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        # Generic fallback
        return {
            "score":        5,
            "strengths":    ["Answer received."],
            "improvements": ["Provide more detail with specific examples."],
            "model_tip":    raw[:400] if raw else "No feedback available.",
        }

    @staticmethod
    def _grade(pct: float) -> str:
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B"
        if pct >= 60: return "C"
        if pct >= 50: return "D"
        return "F"