"""
Interview Trainer Agent – Main Application Entry Point
IBM Agentic AI Hackathon | RAG-Based Interview Prep System
"""

import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from backend.models.database import db
from backend.routes.resume_routes import resume_bp
from backend.routes.interview_routes import interview_bp
from backend.routes.chat_routes import chat_bp
from backend.routes.history_routes import history_bp

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()


def create_app() -> Flask:
    """Application factory – creates and configures the Flask app."""
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )

    # ── Core config ─────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///interview_trainer.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(
        os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)
    )

    # ── Extensions ──────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    # ── Upload folder ────────────────────────────────────────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.getenv("VECTOR_STORE_PATH", "vector_store"), exist_ok=True)

    # ── Blueprints ───────────────────────────────────────────────────────────
    app.register_blueprint(resume_bp,    url_prefix="/api/resume")
    app.register_blueprint(interview_bp, url_prefix="/api/interview")
    app.register_blueprint(chat_bp,      url_prefix="/api/chat")
    app.register_blueprint(history_bp,   url_prefix="/api/history")

    # ── Frontend catch-all ───────────────────────────────────────────────────
    from flask import render_template

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/practice")
    def practice():
        return render_template("practice.html")

    @app.route("/history")
    def history_page():
        return render_template("history.html")

    # ── DB init ──────────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()
        _seed_sample_data()

    return app


def _seed_sample_data():
    """Seed role-specific interview question bank on first run."""
    from backend.models.database import QuestionBank, db as _db
    from backend.data.sample_questions import SAMPLE_QUESTIONS

    if QuestionBank.query.count() == 0:
        for q in SAMPLE_QUESTIONS:
            _db.session.add(QuestionBank(**q))
        _db.session.commit()
        print("✅  Sample question bank seeded.")


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    application = create_app()
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"🚀  Interview Trainer Agent running on http://localhost:{port}")
    application.run(host="0.0.0.0", port=port, debug=debug)