import json
import streamlit as st
from google import genai


# Create Gemini client
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


def evaluate_answer(question, answer, expected_concepts):

    prompt = f"""
You are an interview evaluator for an AI-powered
mock interview system called INTERVISION.

Evaluate the candidate's answer fairly.

Question:
{question}

Expected concepts:
{", ".join(expected_concepts)}

Candidate's answer:
{answer}

Return ONLY valid JSON using exactly this structure:

{{
    "overall_score": 0,
    "relevance": 0,
    "correctness": 0,
    "completeness": 0,
    "clarity": 0,
    "strengths": [],
    "weaknesses": [],
    "feedback": ""
}}

Scoring:
- Each score must be between 0 and 10.
- overall_score must represent the overall quality.
- relevance measures whether the answer addresses the question.
- correctness measures technical accuracy.
- completeness measures coverage of important concepts.
- clarity measures how clearly the answer is explained.
- strengths should contain 1 to 3 short points.
- weaknesses should contain 1 to 3 short points.
- feedback should be concise and useful for the candidate.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    # Remove markdown code fences if Gemini adds them
    if response_text.startswith("```"):
        response_text = response_text.replace(
            "```json", ""
        ).replace(
            "```", ""
        ).strip()

    return json.loads(response_text)
