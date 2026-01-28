import os
import uuid
from openai import OpenAI 
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
print(f"Using OPENAI_API_KEY: {'set' if api_key else 'not set'}")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")

client = OpenAI(api_key=api_key)

MODEL = "gpt-4.1"  # pick a model you have access to

def generate_question(
        position, 
        subject, 
        difficulty, 
        persona, 
        num_followups, 
        clarification_allowance,     
        avoid_questions=None,
        ):
    avoid_questions = avoid_questions or []
    request_id = str(uuid.uuid4())  # nonce to reduce identical generations

    prompt = f"""
Create ONE interview question.

Parameters:
- Position: {position}
- Subject: {subject}
- Difficulty: {difficulty}
- Interviewer persona: {persona}
- Number of follow-ups: {num_followups}
- Clarification allowance: {clarification_allowance}

Do NOT repeat or closely paraphrase any of these previous questions:
{json.dumps(avoid_questions, ensure_ascii=False, indent=2)}

Diversity rule:
- Pick a different subtopic than the previous questions (e.g., ARC/retain cycles, concurrency, networking, testing, UIKit/SwiftUI, protocols/generics, performance).
- Use this request_id ONLY as a randomness source; do not output it: {request_id}

Return ONLY valid JSON with this exact shape:
{{
  "question": "string",
  "followups": ["string", "string"],
  "rubric": [
    {{"competency": "string", "weight": 0.0, "score_1": "string", "score_3": "string", "score_5": "string"}}
  ]
}}

Rules:
- Keep it concise.
- rubric weights must sum to 1.0
"""
    resp = client.responses.create(
        model=MODEL,
        input=prompt,
        temperature=0.7,
        max_output_tokens=800,
    )

    text = resp.output_text
    return json.loads(text)  # if model returns invalid JSON you'll get an exception


def grade_answer(question_obj, candidate_answer):
    prompt = f"""
You are grading an interview answer using the provided rubric.

QUESTION:
{question_obj["question"]}

RUBRIC (JSON):
{json.dumps(question_obj["rubric"], ensure_ascii=False)}

CANDIDATE ANSWER:
{candidate_answer}

Return ONLY valid JSON with this exact shape:
{{
  "overall_score": 1,
  "scores_by_competency": [
    {{"competency": "string", "score": 1, "rationale": "string"}}
  ],
  "final_feedback": "string"
}}

Rules:
- Score each competency 1-5.
- Compute overall_score as a weighted summary (round to nearest int).
- Be specific and actionable.
"""
    resp = client.responses.create(
        model=MODEL,
        input=prompt,
        temperature=0.2,
        max_output_tokens=900,
    )

    text = resp.output_text
    return json.loads(text)