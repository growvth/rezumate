from functools import lru_cache
from langchain_groq import ChatGroq


@lru_cache(maxsize=1)
def get_model():
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)


def get_ai_response(job_description: str, resume_content: str, prompt: str) -> str:
    full_prompt = f"""
Job Description:
{job_description}

Resume Content:
{resume_content}

Instructions:
{prompt}
"""
    response = get_model().invoke(full_prompt)
    return response.content


def get_comparison_response(job_description: str, resume1: str, resume2: str, prompt: str) -> str:
    full_prompt = f"""
Job Description:
{job_description}

Resume 1:
{resume1}

Resume 2:
{resume2}

Instructions:
{prompt}
"""
    response = get_model().invoke(full_prompt)
    return response.content


def get_ranking_response(job_description: str, resumes: list[dict], prompt: str) -> str:
    resumes_text = ""
    for i, resume in enumerate(resumes, 1):
        resumes_text += f"\n--- Resume {i}: {resume['filename']} ---\n{resume['content']}\n"

    full_prompt = f"""
Job Description:
{job_description}

Resumes to Rank:
{resumes_text}

Instructions:
{prompt}
"""
    response = get_model().invoke(full_prompt)
    return response.content


def get_chat_response(job_description: str, resume_content: str, chat_history: list[dict], user_message: str) -> str:
    history_text = ""
    for msg in chat_history:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    full_prompt = f"""
You are a professional career coach and resume expert. You are helping a user improve their resume for a specific job.

Job Description:
{job_description}

User's Resume:
{resume_content}

Previous Conversation:
{history_text}

User's New Message: {user_message}

Provide helpful, actionable advice. Be specific and reference the actual content from the resume and job description. Keep responses concise but thorough.
"""
    response = get_model().invoke(full_prompt)
    return response.content


SCORE_PROMPT = """
You are a calibrated ATS scanner combined with an expert Technical Sourcer. Your task is to calculate a precise, conservative match score.

STEPS YOU MUST FOLLOW:
1. Extract ALL hard skills, tools, frameworks, years of experience, certifications, and domain requirements explicitly stated in the job description.
2. For each item, determine if the resume contains:
   - Full match (explicitly stated with similar or greater proficiency/level)
   - Partial match (mentioned but weaker/less experience)
   - No match
3. Scoring: Full = 1.0 point, Partial = 0.5 points, None = 0
4. Final % = (total points / total requirements) x 100 -> round down to nearest integer

CRITICAL RULES:
- Never assume unstated experience
- Company names/projects alone do not count as skill proof
- Be strictly conservative on partial matches

Output EXACTLY in this format:

**Match Percentage: XX%**

**Overall Fit:** Strong Match (80%+) / Moderate (65-79%) / Weak (50-64%) / Poor (<50%)

**Fully Matched Requirements:**
- skill/tool (evidence from resume)
- ...

**Partially Matched (count as 50%):**
- skill/tool - weakness in resume
- ...

**Missing Requirements (0%):**
- skill/tool/experience
- ...

**Strengths:**
- Key strength 1
- Key strength 2
- ...

**Areas for Improvement:**
- Specific improvement suggestion 1
- Specific improvement suggestion 2
- ...
"""


COMPARE_PROMPT = """
You are an impartial senior Technical Recruiter with 15+ years of experience. Compare both resumes objectively against the job description.

CRITICAL RULES:
- Base every statement exclusively on explicit content present in the resumes and job description
- Never infer or assume unstated skills/experience
- Be direct and critical when evidence is missing

Output EXACTLY in this format:

**Winner: [Resume 1 / Resume 2 / Tie]**

**Resume 1 Score: XX%**
**Resume 2 Score: XX%**

**Resume 1 Analysis:**
Strengths:
- ...
Weaknesses:
- ...

**Resume 2 Analysis:**
Strengths:
- ...
Weaknesses:
- ...

**Key Differentiators:**
- What makes the winner stand out (or why it's a tie)

**Recommendation:**
Brief recommendation for hiring decision
"""


RANK_PROMPT = """
You are a calibrated ATS scanner and expert Technical Recruiter. Rank all provided resumes against the job description.

CRITICAL RULES:
- Score each resume independently first
- Base rankings solely on explicit evidence
- Never assume unstated experience
- Be strictly conservative

For each resume, calculate a match percentage using:
- Full match = 1.0 point
- Partial match = 0.5 points
- No match = 0

Output EXACTLY in this format:

**Rankings:**

1. [Filename] - XX% Match
   - Key strengths: ...
   - Key gaps: ...

2. [Filename] - XX% Match
   - Key strengths: ...
   - Key gaps: ...

(Continue for all resumes)

**Summary:**
Brief summary of the ranking results and recommendation for which candidates to advance.
"""
