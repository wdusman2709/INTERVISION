import json
import re
import streamlit as st
from google import genai
from google.genai import types


# ---------------------------------------------------------
# Gemini Client
# ---------------------------------------------------------

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


# ---------------------------------------------------------
# Structured Output Schema
# ---------------------------------------------------------

EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "relevance": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "correctness": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "completeness": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "clarity": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "depth": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "concept_coverage": {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        },
        "strengths": {
            "type": "array",
            "items": {"type": "string"}
        },
        "weaknesses": {
            "type": "array",
            "items": {"type": "string"}
        },
        "feedback": {
            "type": "string"
        },
        "ideal_answer_points": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "relevance",
        "correctness",
        "completeness",
        "clarity",
        "depth",
        "concept_coverage",
        "strengths",
        "weaknesses",
        "feedback",
        "ideal_answer_points"
    ]
}


# ---------------------------------------------------------
# Helper: Normalize Text
# ---------------------------------------------------------

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------
# Helper: Expected Concept Coverage
# ---------------------------------------------------------

def calculate_concept_coverage(answer, expected_concepts):

    if not expected_concepts:
        return 100

    normalized_answer = normalize_text(answer)

    matched = 0

    for concept in expected_concepts:
        concept_words = normalize_text(concept).split()

        if all(word in normalized_answer for word in concept_words):
            matched += 1

    return round((matched / len(expected_concepts)) * 100)


# ---------------------------------------------------------
# Main Evaluator
# ---------------------------------------------------------

def evaluate_answer(question, answer, expected_concepts=None):

    expected_concepts = expected_concepts or []

    # -----------------------------------------------------
    # Empty answer
    # -----------------------------------------------------

    if not answer or not answer.strip():

        return {
            "overall_score": 0,
            "relevance": 0,
            "correctness": 0,
            "completeness": 0,
            "clarity": 0,
            "depth": 0,
            "concept_coverage": 0,
            "strengths": [],
            "weaknesses": ["No answer was provided."],
            "feedback": "Please provide an answer that directly addresses the question.",
            "ideal_answer_points": expected_concepts
        }

    concept_coverage = calculate_concept_coverage(
        answer,
        expected_concepts
    )

    # -----------------------------------------------------
    # Strict Evaluation Prompt
    # -----------------------------------------------------

    prompt = f"""
You are a STRICT technical interview evaluator.

Evaluate the candidate's answer against the question.

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

EXPECTED CONCEPTS:
{expected_concepts}

IMPORTANT RULES:

1. Do NOT give high scores simply because the answer is fluent.
2. Technical correctness is more important than writing style.
3. Missing important concepts must reduce completeness.
4. Incorrect technical statements must reduce correctness significantly.
5. Irrelevant information must reduce relevance.
6. Very vague answers should receive low scores.
7. Short answers can score well ONLY if they contain the important concepts.
8. Do not assume information that the candidate did not state.
9. Do not reward repetition.
10. For technical questions, factual accuracy is mandatory.
11. Give realistic interview-level scores.
12. Identify specific strengths and weaknesses.
13. Give actionable feedback explaining how the candidate can improve.
14. Do not be overly generous.

SCORING:

Relevance:
90-100 = Directly answers the question
70-89  = Mostly relevant
50-69  = Partially relevant
30-49  = Mostly off-topic
0-29   = Does not answer the question

Correctness:
90-100 = Accurate and technically sound
70-89  = Mostly correct with minor issues
50-69  = Some important mistakes
30-49  = Major technical errors
0-29   = Fundamentally incorrect

Completeness:
90-100 = Covers all important concepts
70-89  = Covers most concepts
50-69  = Missing important concepts
30-49  = Very incomplete
0-29   = Almost no useful content

Clarity:
90-100 = Clear, concise and well structured
70-89  = Mostly clear
50-69  = Somewhat unclear
30-49  = Difficult to follow
0-29   = Very unclear

Depth:
90-100 = Strong explanation with reasoning/examples
70-89  = Good explanation
50-69  = Basic explanation
30-49  = Very shallow
0-29   = No meaningful explanation

Concept Coverage:
Evaluate how many of the expected concepts were actually addressed.

Return ONLY valid JSON matching the requested schema.
"""

    # -----------------------------------------------------
    # Gemini Request
    # -----------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EVALUATION_SCHEMA,
                temperature=0.1
            )
        )

        result = json.loads(response.text)

    except Exception as e:

        return {
            "overall_score": 0,
            "relevance": 0,
            "correctness": 0,
            "completeness": 0,
            "clarity": 0,
            "depth": 0,
            "concept_coverage": concept_coverage,
            "strengths": [],
            "weaknesses": [f"Evaluation failed: {str(e)}"],
            "feedback": "Unable to evaluate this answer. Please try again.",
            "ideal_answer_points": expected_concepts
        }

    # -----------------------------------------------------
    # Combine Gemini + Concept Coverage
    # -----------------------------------------------------

    relevance = int(result.get("relevance", 0))
    correctness = int(result.get("correctness", 0))
    completeness = int(result.get("completeness", 0))
    clarity = int(result.get("clarity", 0))
    depth = int(result.get("depth", 0))

    # Give concept coverage significant importance
    final_concept_coverage = round(
        (concept_coverage + int(result.get("concept_coverage", 0))) / 2
    )

    # -----------------------------------------------------
    # Weighted Overall Score
    # -----------------------------------------------------

    overall_score = round(
        relevance * 0.20 +
        correctness * 0.30 +
        completeness * 0.20 +
        clarity * 0.10 +
        depth * 0.10 +
        final_concept_coverage * 0.10
    )

    # -----------------------------------------------------
    # STRICT SCORE CAPS
    # -----------------------------------------------------

    # Very poor concept coverage
    if final_concept_coverage < 30:
        overall_score = min(overall_score, 40)

    elif final_concept_coverage < 50:
        overall_score = min(overall_score, 55)

    elif final_concept_coverage < 70:
        overall_score = min(overall_score, 70)

    # Major correctness problem
    if correctness < 40:
        overall_score = min(overall_score, 50)

    elif correctness < 60:
        overall_score = min(overall_score, 65)

    # Poor relevance
    if relevance < 40:
        overall_score = min(overall_score, 50)

    # Very incomplete answer
    if completeness < 40:
        overall_score = min(overall_score, 55)

    # -----------------------------------------------------
    # Score Classification
    # -----------------------------------------------------

    if overall_score >= 85:
        level = "Excellent"

    elif overall_score >= 70:
        level = "Good"

    elif overall_score >= 55:
        level = "Average"

    elif overall_score >= 40:
        level = "Needs Improvement"

    else:
        level = "Poor"

    # -----------------------------------------------------
    # Final Result
    # -----------------------------------------------------

    return {
        "overall_score": overall_score,
        "level": level,
        "relevance": relevance,
        "correctness": correctness,
        "completeness": completeness,
        "clarity": clarity,
        "depth": depth,
        "concept_coverage": final_concept_coverage,
        "strengths": result.get("strengths", []),
        "weaknesses": result.get("weaknesses", []),
        "feedback": result.get("feedback", ""),
        "ideal_answer_points": result.get(
            "ideal_answer_points",
            expected_concepts
        )
    }


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    question = "What is supervised learning?"

    answer = """
    Supervised learning uses labelled data to train a model
    so that it can make predictions on new data.
    """

    expected_concepts = [
        "labelled data",
        "training",
        "prediction"
    ]

    result = evaluate_answer(
        question,
        answer,
        expected_concepts
    )

    print(json.dumps(result, indent=2))