# Interview Trainer Agent

AI-powered Interview Preparation Platform using IBM Granite Models, RAG, LangChain, and Flask.

## Problem Statement

The Interview Trainer Agent helps candidates prepare for technical and HR interviews through personalized AI-driven interview practice. The system uses Retrieval-Augmented Generation (RAG) and IBM Granite Models to generate role-specific interview questions, evaluate answers, and provide real-time feedback.

---

# Features

- Resume Upload & Parsing
- Technical + HR Interview Questions
- AI-Based Answer Evaluation
- Interview Scoring & Feedback
- Conversational Mock Interview Chatbot
- RAG-Based Knowledge Retrieval
- Session History Tracking
- Modern Responsive UI
- IBM Granite Model Integration

---

# Tech Stack

## Frontend
- HTML
- CSS
- JavaScript

## Backend
- Flask
- SQLite
- SQLAlchemy

## AI & RAG
- IBM Granite Models
- IBM watsonx.ai
- LangChain
- FAISS Vector Database

---

# Architecture

```text
User Uploads Resume
        ↓
Resume Parsing
        ↓
RAG Retrieval (FAISS + LangChain)
        ↓
IBM Granite Model
        ↓
Question Generation & Feedback
        ↓
Chatbot Interview + Analytics
```

---

# Folder Structure

```text
backend/
│
├── app.py
├── requirements.txt
│
├── routes/
├── services/
├── utils/
├── database/
├── templates/
├── static/
├── uploads/
└── vector_store/
```

---

# Modules

## Resume Parsing Module
Extracts:
- Skills
- Experience
- Education
- Projects

from uploaded resumes.

## RAG Pipeline
Uses:
- LangChain
- FAISS
- IBM Embeddings

to retrieve relevant interview knowledge.

## IBM Granite Integration
Generates:
- Technical Questions
- HR Questions
- AI Feedback
- Mock Interview Responses

## Interview Evaluation
Provides:
- Scores
- Strengths
- Weaknesses
- Improvement Suggestions

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-username/interview-trainer-agent.git
cd interview-trainer-agent
```

---

## Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows
```bash
venv\Scripts\activate
```

#### Mac/Linux
```bash
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create `.env`

```env
IBM_API_KEY=your_api_key
IBM_PROJECT_ID=your_project_id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=secret_key
```

---

# Run Application

```bash
python app.py
```

Server:
```text
http://localhost:5000
```

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /upload-resume | Upload Resume |
| POST | /generate-questions | Generate Interview Questions |
| POST | /submit-answer | Evaluate Candidate Answer |
| POST | /chat | Conversational Interview |
| GET | /history | Fetch Interview History |

---

# IBM Cloud Services Used

- IBM watsonx.ai
- IBM Granite Models
- IBM Cloud Lite
- IBM Embeddings

---

# Future Enhancements

- Voice-based Interviews
- Video Interview Analysis
- ATS Resume Scoring
- Multi-language Support
- Emotion Detection
- Company-Specific Interview Datasets

---

# Screenshots

## Landing Page
(Add Screenshot Here)

## Dashboard
(Add Screenshot Here)

## Chatbot Interview
(Add Screenshot Here)

---

# Contributors

- Aditya Singh Khagi

---

# License

This project is developed for the IBM Agentic AI Hackathon.
