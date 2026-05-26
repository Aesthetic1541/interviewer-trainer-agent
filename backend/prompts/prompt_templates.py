"""
Prompt Templates for IBM Granite (granite-13b-instruct-v2)
Granite uses <|user|> / <|assistant|> instruction format.
"""

# ── 1. Question Generation ─────────────────────────────────────────────────────
QUESTION_GENERATION_PROMPT = """<|system|>
You are an expert technical interviewer and HR specialist. Generate a tailored, role-specific interview question set in strict JSON format.
<|user|>
Generate interview questions for the following candidate profile:

Job Role: {job_role}
Experience Level: {experience}
Resume Summary: {resume_summary}

Retrieved Context (use for relevance):
{context}

Requirements:
- Generate exactly {num_technical} technical questions specific to {job_role}
- Generate exactly {num_hr} HR/behavioral questions
- Scale difficulty to {experience} level
- Questions must be practical, realistic, and commonly asked in real interviews
- Return ONLY valid JSON, no preamble or explanation

Output Format (strict JSON):
{{
  "technical": [
    "Question 1",
    "Question 2",
    ...
  ],
  "hr": [
    "Question 1",
    "Question 2",
    ...
  ]
}}
<|assistant|>
"""

# ── 2. Answer Evaluation ───────────────────────────────────────────────────────
ANSWER_EVALUATION_PROMPT = """<|system|>
You are a senior interviewer evaluating a candidate's response. Provide honest, constructive, structured feedback in JSON format.
<|user|>
Evaluate the following interview response:

Job Role: {job_role}
Question Category: {category}
Question: {question}

Candidate's Answer:
{user_answer}

Model Answer (reference):
{model_answer}

Scoring Criteria (out of 10):
- Accuracy & Correctness (3 pts)
- Depth & Completeness (3 pts)
- Communication Clarity (2 pts)
- Practical Examples (2 pts)

Return ONLY valid JSON, no preamble.

Output Format:
{{
  "score": <integer 0-10>,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "model_tip": "A 1-2 sentence expert tip to strengthen the answer"
}}
<|assistant|>
"""

# ── 3. Chatbot Interview Mode ─────────────────────────────────────────────────
CHATBOT_INTERVIEW_PROMPT = """<|system|>
You are a professional interviewer conducting a live mock interview for a {experience}-level {job_role} position. 
Stay in character as an interviewer. Ask follow-up questions, probe deeper, give brief encouraging acknowledgments, 
and naturally progress through technical and behavioral topics. Keep responses concise (2-4 sentences max).
<|user|>
Interview Context:
Role: {job_role}
Level: {experience}

Conversation History:
{history}

Relevant context for this topic:
{context}

Candidate just said: "{user_message}"

Respond as the interviewer (follow up, probe, or move to next topic naturally):
<|assistant|>
"""

# ── 4. Resume Analysis ────────────────────────────────────────────────────────
RESUME_ANALYSIS_PROMPT = """<|system|>
You are an expert resume analyst and career coach. Analyze the resume and provide actionable insights.
<|user|>
Analyze this resume for a candidate applying for: {job_role}

Resume Text:
{resume_text}

Provide:
1. Overall assessment (2-3 sentences)
2. Top 3 strengths for this role
3. Top 3 gaps/weaknesses
4. 3 specific improvement suggestions
5. Interview readiness score (0-10)

Return ONLY valid JSON:
{{
  "overall": "...",
  "strengths": ["...", "...", "..."],
  "gaps": ["...", "...", "..."],
  "suggestions": ["...", "...", "..."],
  "readiness_score": <0-10>
}}
<|assistant|>
"""

# ── 5. Improvement Tips ───────────────────────────────────────────────────────
IMPROVEMENT_TIPS_PROMPT = """<|system|>
You are a career coach specializing in interview preparation. Give specific, actionable, encouraging tips.
<|user|>
A candidate is preparing for a {experience}-level {job_role} interview.

Their weak areas based on mock interview:
{weak_areas}

Their strong areas:
{strong_areas}

Provide 5 specific, actionable preparation tips tailored to their profile.
Return ONLY valid JSON:
{{
  "tips": [
    {{"title": "...", "detail": "..."}},
    ...
  ]
}}
<|assistant|>
"""