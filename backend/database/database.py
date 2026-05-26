"""
Database Models – SQLAlchemy ORM definitions
Tables: User, Resume, InterviewSession, QuestionBank, SessionQuestion, ChatMessage
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# ─────────────────────────────────────────────────────────────────────────────
class User(db.Model):
    """Represents an application user / candidate."""
    __tablename__ = "users"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(200), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes  = db.relationship("Resume", backref="user", lazy=True)
    sessions = db.relationship("InterviewSession", backref="user", lazy=True)

    def to_dict(self):
        return {
            "id":         self.id,
            "name":       self.name,
            "email":      self.email,
            "created_at": self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
class Resume(db.Model):
    """Stores parsed resume data and the original file path."""
    __tablename__ = "resumes"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    filename        = db.Column(db.String(256), nullable=False)
    file_path       = db.Column(db.String(512), nullable=False)
    raw_text        = db.Column(db.Text, nullable=True)
    parsed_skills   = db.Column(db.Text, nullable=True)   # JSON string
    parsed_exp      = db.Column(db.Text, nullable=True)   # JSON string
    parsed_edu      = db.Column(db.Text, nullable=True)   # JSON string
    experience_yrs  = db.Column(db.Float, default=0.0)
    job_title       = db.Column(db.String(200), nullable=True)
    uploaded_at     = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("InterviewSession", backref="resume", lazy=True)

    def to_dict(self):
        import json
        return {
            "id":             self.id,
            "filename":       self.filename,
            "parsed_skills":  json.loads(self.parsed_skills or "[]"),
            "parsed_exp":     json.loads(self.parsed_exp or "[]"),
            "parsed_edu":     json.loads(self.parsed_edu or "[]"),
            "experience_yrs": self.experience_yrs,
            "job_title":      self.job_title,
            "uploaded_at":    self.uploaded_at.isoformat(),
        }


# ─────────────────────────────────────────────────────────────────────────────
class InterviewSession(db.Model):
    """One complete interview prep session for a user + role."""
    __tablename__ = "interview_sessions"

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resume_id     = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=True)
    job_role      = db.Column(db.String(200), nullable=False)
    experience    = db.Column(db.String(50), nullable=False)   # junior/mid/senior
    total_score   = db.Column(db.Float, default=0.0)
    max_score     = db.Column(db.Float, default=0.0)
    status        = db.Column(db.String(30), default="in_progress")  # in_progress/completed
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at  = db.Column(db.DateTime, nullable=True)

    questions     = db.relationship("SessionQuestion", backref="session", lazy=True)
    messages      = db.relationship("ChatMessage",     backref="session", lazy=True)

    @property
    def score_pct(self):
        if self.max_score == 0:
            return 0.0
        return round((self.total_score / self.max_score) * 100, 1)

    def to_dict(self):
        return {
            "id":           self.id,
            "job_role":     self.job_role,
            "experience":   self.experience,
            "total_score":  self.total_score,
            "max_score":    self.max_score,
            "score_pct":    self.score_pct,
            "status":       self.status,
            "created_at":   self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
class QuestionBank(db.Model):
    """Pre-loaded role-specific questions used for RAG retrieval."""
    __tablename__ = "question_bank"

    id            = db.Column(db.Integer, primary_key=True)
    job_role      = db.Column(db.String(200), nullable=False, index=True)
    category      = db.Column(db.String(50), nullable=False)   # technical / hr / behavioral
    experience    = db.Column(db.String(50), nullable=False)   # junior/mid/senior/all
    question      = db.Column(db.Text, nullable=False)
    model_answer  = db.Column(db.Text, nullable=True)
    difficulty    = db.Column(db.String(20), default="medium")  # easy/medium/hard
    tags          = db.Column(db.String(300), nullable=True)    # comma-separated

    def to_dict(self):
        return {
            "id":           self.id,
            "job_role":     self.job_role,
            "category":     self.category,
            "experience":   self.experience,
            "question":     self.question,
            "model_answer": self.model_answer,
            "difficulty":   self.difficulty,
            "tags":         self.tags.split(",") if self.tags else [],
        }


# ─────────────────────────────────────────────────────────────────────────────
class SessionQuestion(db.Model):
    """A question asked during an interview session, with user answer + feedback."""
    __tablename__ = "session_questions"

    id              = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), nullable=False)
    question_text   = db.Column(db.Text, nullable=False)
    category        = db.Column(db.String(50), nullable=False)
    model_answer    = db.Column(db.Text, nullable=True)
    user_answer     = db.Column(db.Text, nullable=True)
    ai_feedback     = db.Column(db.Text, nullable=True)
    score           = db.Column(db.Float, default=0.0)
    max_score       = db.Column(db.Float, default=10.0)
    answered        = db.Column(db.Boolean, default=False)
    order_index     = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "session_id":    self.session_id,
            "question_text": self.question_text,
            "category":      self.category,
            "model_answer":  self.model_answer,
            "user_answer":   self.user_answer,
            "ai_feedback":   self.ai_feedback,
            "score":         self.score,
            "max_score":     self.max_score,
            "answered":      self.answered,
            "order_index":   self.order_index,
        }


# ─────────────────────────────────────────────────────────────────────────────
class ChatMessage(db.Model):
    """Conversational chat messages within a session (chatbot interview mode)."""
    __tablename__ = "chat_messages"

    id         = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.id"), nullable=False)
    role       = db.Column(db.String(20), nullable=False)   # user / assistant
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "session_id": self.session_id,
            "role":       self.role,
            "content":    self.content,
            "created_at": self.created_at.isoformat(),
        }