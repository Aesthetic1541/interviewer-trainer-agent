"""
Resume Parser Service
Extracts structured data (skills, experience, education, job title) from PDF/text resumes.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Common skill keywords ─────────────────────────────────────────────────────
TECH_SKILLS = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab",
    # Web
    "react", "angular", "vue", "node", "express", "django", "flask", "fastapi",
    "spring", "html", "css", "sass", "tailwind", "bootstrap",
    # Data / AI
    "machine learning", "deep learning", "nlp", "computer vision", "tensorflow",
    "pytorch", "scikit-learn", "pandas", "numpy", "spark", "hadoop", "kafka",
    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "sqlite", "oracle",
    # Other
    "git", "rest api", "graphql", "microservices", "agile", "scrum",
]

SOFT_SKILLS = [
    "leadership", "communication", "teamwork", "problem solving", "analytical",
    "critical thinking", "adaptability", "time management", "creativity",
    "collaboration", "presentation", "mentoring", "project management",
]

DEGREE_PATTERNS = ["b.tech", "b.e.", "b.sc", "m.tech", "m.sc", "mba", "phd",
                   "bachelor", "master", "doctorate", "b.s.", "m.s."]


class ResumeParser:
    """Parses PDF or plain-text resumes into structured JSON."""

    # ── Public API ─────────────────────────────────────────────────────────────
    def parse_file(self, file_path: str) -> Dict:
        """
        Main entry point. Accepts path to a PDF or .txt file.
        Returns a dict with raw_text, skills, experience, education, etc.
        """
        ext = Path(file_path).suffix.lower()
        raw_text = ""

        if ext == ".pdf":
            raw_text = self._extract_pdf(file_path)
        elif ext in (".txt", ".md"):
            raw_text = Path(file_path).read_text(errors="replace")
        else:
            logger.warning(f"Unsupported file type: {ext}. Attempting PDF extraction.")
            raw_text = self._extract_pdf(file_path)

        if not raw_text.strip():
            return {"error": "Could not extract text from the resume."}

        return self._parse_text(raw_text)

    def parse_text(self, text: str) -> Dict:
        """Parse already-extracted plain text."""
        return self._parse_text(text)

    # ── PDF extraction ─────────────────────────────────────────────────────────
    def _extract_pdf(self, path: str) -> str:
        text = ""
        # Try pdfplumber first (better layout fidelity)
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            logger.debug(f"pdfplumber failed: {e}")

        # Fallback to PyPDF2
        try:
            import PyPDF2
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
        except Exception as e:
            logger.error(f"PyPDF2 failed: {e}")

        return text

    # ── Core text parser ───────────────────────────────────────────────────────
    def _parse_text(self, text: str) -> Dict:
        clean = self._clean(text)

        return {
            "raw_text":        text,
            "skills":          self._extract_skills(clean),
            "experience":      self._extract_experience(clean),
            "education":       self._extract_education(clean),
            "experience_yrs":  self._estimate_experience_years(clean),
            "job_title":       self._extract_latest_title(clean),
            "contact":         self._extract_contact(clean),
            "summary":         self._extract_summary(clean),
        }

    # ── Helpers ────────────────────────────────────────────────────────────────
    @staticmethod
    def _clean(text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.lower().strip()

    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        tech  = [s for s in TECH_SKILLS  if s in text]
        soft  = [s for s in SOFT_SKILLS  if s in text]
        return {"technical": list(dict.fromkeys(tech)), "soft": list(dict.fromkeys(soft))}

    def _extract_experience(self, text: str) -> List[str]:
        """Heuristic: grab lines that look like job titles/companies."""
        lines   = text.split("\n") if "\n" in text else text.split(". ")
        results = []
        job_kws = ["engineer", "developer", "analyst", "manager", "intern",
                   "architect", "consultant", "lead", "scientist", "designer"]
        for line in lines:
            line = line.strip()
            if any(kw in line for kw in job_kws) and 10 < len(line) < 120:
                results.append(line.title())
                if len(results) >= 5:
                    break
        return results

    def _extract_education(self, text: str) -> List[str]:
        results = []
        for deg in DEGREE_PATTERNS:
            idx = text.find(deg)
            if idx != -1:
                snippet = text[max(0, idx - 20) : idx + 80].strip()
                results.append(snippet.title())
        return list(dict.fromkeys(results))[:4]

    def _estimate_experience_years(self, text: str) -> float:
        """Find year ranges like 2018-2023 and sum them."""
        year_ranges = re.findall(r"(20\d{2})\s*[-–to]+\s*(20\d{2}|present|current)", text)
        import datetime
        current_year = datetime.datetime.now().year
        total = 0.0
        for start, end in year_ranges:
            s = int(start)
            e = current_year if end in ("present", "current") else int(end)
            total += max(0, e - s)
        # If we couldn't parse, guess from keywords
        if total == 0:
            if "senior" in text or "lead" in text or "principal" in text:
                return 6.0
            if "mid" in text:
                return 3.0
            return 1.0
        return min(total, 30.0)

    def _extract_latest_title(self, text: str) -> str:
        roles = {
            "software engineer": "Software Engineer",
            "data scientist":    "Data Scientist",
            "ml engineer":       "ML Engineer",
            "frontend developer":"Frontend Developer",
            "backend developer": "Backend Developer",
            "full stack":        "Full Stack Developer",
            "devops":            "DevOps Engineer",
            "product manager":   "Product Manager",
            "data analyst":      "Data Analyst",
            "android developer": "Android Developer",
            "ios developer":     "iOS Developer",
        }
        for key, title in roles.items():
            if key in text:
                return title
        return "Software Professional"

    def _extract_contact(self, text: str) -> Dict:
        email = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone = re.search(r"[\+\(]?\d[\d\s\-\(\)]{8,14}\d", text)
        return {
            "email": email.group() if email else None,
            "phone": phone.group() if phone else None,
        }

    def _extract_summary(self, text: str) -> str:
        """Return first ~300 characters as a rough summary."""
        words = text.split()[:60]
        return " ".join(words).strip().title()