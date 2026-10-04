
import json
import random

import pandas as pd
import plotly.express as px
import streamlit as st

from modules.scorer import score_answer
from modules.evaluator import evaluate_answer
from modules.database import (
    initialize_database,
    create_candidate,
    create_interview,
    save_answer,
    update_interview_summary,
)
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="INTERVISION | AI Interview Simulator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

initialize_database()

# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"


def reset_interview():
    """Clear interview-specific state for a fresh interview."""
    keys_to_clear = [
        "interview_questions",
        "current_question",
        "answers",
        "evaluated_answers",
        "difficulty",
        "interview_type",
        "number_of_questions",
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)


def go_to(page):
    st.session_state.page = page
    st.rerun()


# ============================================================
# PROFESSIONAL UI THEME
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    .stApp {
        background: linear-gradient(
            135deg,
            #f8faff 0%,
            #eef2ff 100%
        );
        color: #172554;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #172554 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    p, label {
        line-height: 1.7;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #172554 0%,
            #3730a3 55%,
            #6366f1 100%
        );
        padding: 48px 32px;
        border-radius: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 40px rgba(49, 46, 129, 0.18);
        margin-bottom: 28px;
    }

    .hero-title {
        color: white !important;
        font-size: clamp(34px, 5vw, 52px);
        font-weight: 800;
        letter-spacing: -1.5px;
        margin: 8px 0;
    }

    .hero-subtitle {
        color: #e0e7ff !important;
        font-size: 17px;
        max-width: 680px;
        margin: 0 auto;
    }

    .eyebrow {
        color: #c7d2fe;
        text-transform: uppercase;
        letter-spacing: 3px;
        font-size: 12px;
        font-weight: 700;
    }

    .section-label {
        color: #6366f1;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .info-card {
        background: white;
        border: 1px solid #e0e7ff;
        border-radius: 18px;
        padding: 24px;
        min-height: 145px;
        box-shadow: 0 5px 20px rgba(30, 58, 138, 0.04);
    }

    .info-card-icon {
        font-size: 28px;
        margin-bottom: 10px;
    }

    .info-card-title {
        color: #172554;
        font-weight: 700;
        font-size: 17px;
        margin-bottom: 6px;
    }

    .info-card-description {
        color: #64748b;
        font-size: 14px;
        line-height: 1.6;
    }

    .question-card {
        background: white;
        border: 1px solid #dbe4ff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 28px rgba(30, 58, 138, 0.06);
        margin: 16px 0;
    }

    .question-label {
        color: #6366f1;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 1.5px;
        font-size: 12px;
        margin-bottom: 12px;
    }

    .question-text {
        color: #172554;
        font-weight: 700;
        font-size: 23px;
        line-height: 1.5;
    }

    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #6366f1);
        color: white;
        border: 1px solid transparent;
        border-radius: 11px;
        min-height: 44px;
        padding: 0.65rem 1.1rem;
        font-weight: 700;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #3730a3, #4f46e5);
        color: white;
        border-color: transparent;
        box-shadow: 0 5px 15px rgba(79, 70, 229, 0.2);
    }

    .stTextInput input,
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px;
        caret-color: #000000;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #6366f1 !important;
}

    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #e0e7ff;
        border-radius: 16px;
        box-shadow: 0 4px 18px rgba(30, 58, 138, 0.04);
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e0e7ff;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 18px rgba(30, 58, 138, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 600;
    }

    div[data-testid="stMetricValue"] {
        color: #4338ca;
        font-weight: 800;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4f46e5, #818cf8);
        border-radius: 10px;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid #e0e7ff;
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: #dbe4ff;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 1rem 2rem 1rem;
        }

        .hero {
            padding: 32px 18px;
        }

        .question-card {
            padding: 20px;
        }

        .question-text {
            font-size: 19px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# REUSABLE DISPLAY HELPERS
# ============================================================

def show_page_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div class="section-label">{eyebrow}</div>
            <h1 style="margin-bottom: 8px;">{title}</h1>
            <p style="color: #64748b; margin-top: 0;">
                {description}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_score(value):
    """Return a valid score between zero and ten."""
    try:
        return max(0.0, min(10.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Your career preparation partner</div>
            <div style="font-size: 48px; margin: 10px 0;">🎤</div>
            <div class="hero-title">INTERVISION</div>
            <p class="hero-subtitle">
                Your AI-powered interview practice platform.
                Practice confidently, receive personalized feedback,
                and improve your interview skills.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## Prepare. Practice. Improve.")
    st.markdown(
        "A structured interview practice experience powered by "
        "AI evaluation and performance analytics."
    )

    st.write("")

    feature1, feature2, feature3 = st.columns(3)

    with feature1:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-card-icon">🧠</div>
                <div class="info-card-title">Role-based Questions</div>
                <div class="info-card-description">
                    Practice questions selected for your target
                    job role and difficulty level.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature2:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-card-icon">🤖</div>
                <div class="info-card-title">AI Evaluation</div>
                <div class="info-card-description">
                    Receive feedback on relevance, correctness,
                    completeness, and clarity.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with feature3:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-card-icon">📊</div>
                <div class="info-card-title">Performance Insights</div>
                <div class="info-card-description">
                    Review scores, identify strengths, and
                    discover areas for improvement.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    center_left, center_button, center_right = st.columns(
        [1, 2, 1]
    )

    with center_button:
        if st.button(
            "🚀 Start Your Interview",
            use_container_width=True,
        ):
            go_to("profile")

    st.write("")
    st.caption(
        "INTERVISION · Practice with purpose. Interview with confidence."
    )


# ============================================================
# CANDIDATE PROFILE PAGE
# ============================================================

elif st.session_state.page == "profile":

    show_page_header(
        "STEP 01 · YOUR PROFILE",
        "Candidate Profile",
        "Tell us a little about yourself to personalize your interview.",
    )

    with st.container(border=True):
        st.markdown("### 👤 Personal Information")

        name = st.text_input(
            "Full Name",
            value=st.session_state.get("name", ""),
            placeholder="Enter your full name",
        )

        education = st.text_input(
            "Education",
            value=st.session_state.get("education", ""),
            placeholder="Example: B.E. Artificial Intelligence and Machine Learning",
        )

        col1, col2 = st.columns(2)

        with col1:
            skills = st.text_input(
                "Skills",
                value=st.session_state.get("skills", ""),
                placeholder="Python, SQL, Machine Learning",
            )

        with col2:
            job_roles = [
                "AI/ML Intern",
                "Python Developer",
                "Data Analyst",
                "Software Developer",
            ]

            saved_role = st.session_state.get(
                "job_role",
                "AI/ML Intern",
            )

            role_index = (
                job_roles.index(saved_role)
                if saved_role in job_roles
                else 0
            )

            job_role = st.selectbox(
                "Target Job Role",
                job_roles,
                index=role_index,
            )

        experience = st.text_area(
            "Projects and Experience",
            value=st.session_state.get("experience", ""),
            placeholder=(
                "Describe your projects, internships, "
                "experience, or relevant accomplishments."
            ),
            height=120,
        )

    st.write("")

    col_back, col_continue = st.columns(2)

    with col_back:
        if st.button("← Back to Home", use_container_width=True):
            go_to("home")

    with col_continue:
        if st.button("Continue to Setup →", use_container_width=True):
            if not name.strip():
                st.warning("Please enter your name.")
            elif not education.strip():
                st.warning("Please enter your education.")
            else:
                candidate_id = create_candidate(
                    name=name.strip(),
                    education=education.strip(),
                    skills=skills.strip(),
                    experience=experience.strip(),
                    job_role=job_role,
                )

                st.session_state.name = name.strip()
                st.session_state.education = education.strip()
                st.session_state.skills = skills.strip()
                st.session_state.experience = experience.strip()
                st.session_state.job_role = job_role
                st.session_state.candidate_id = candidate_id

                go_to("setup")


# ============================================================
# INTERVIEW SETUP PAGE
# ============================================================

elif st.session_state.page == "setup":

    show_page_header(
        "STEP 02 · CONFIGURATION",
        "Interview Setup",
        "Choose the interview settings that suit your preparation goals.",
    )

    with st.container(border=True):
        st.markdown("### ⚙️ Customize Your Session")

        difficulty_options = ["Easy", "Medium", "Hard"]
        type_options = ["HR", "Technical", "Mixed"]
        question_options = [5, 10]

        difficulty = st.selectbox(
            "Difficulty Level",
            difficulty_options,
            index=(
                difficulty_options.index(st.session_state.difficulty)
                if st.session_state.get("difficulty")
                in difficulty_options
                else 1
            ),
        )

        interview_type = st.selectbox(
            "Interview Type",
            type_options,
            index=(
                type_options.index(st.session_state.interview_type)
                if st.session_state.get("interview_type")
                in type_options
                else 2
            ),
        )

        number_of_questions = st.selectbox(
            "Number of Questions",
            question_options,
            index=(
                question_options.index(
                    st.session_state.number_of_questions
                )
                if st.session_state.get("number_of_questions")
                in question_options
                else 0
            ),
        )

        st.info(
            "Your answers will be evaluated by the configured AI "
            "evaluator. Make sure to write clear, complete answers."
        )

    st.write("")

    col_back, col_start = st.columns(2)

    with col_back:
        if st.button("← Back to Profile", use_container_width=True):
            go_to("profile")

    with col_start:
        if st.button(
            "🎤 Begin Interview",
            use_container_width=True,
        ):
            try:
                with open(
                    "data/questions.json",
                    "r",
                    encoding="utf-8",
                ) as file:
                    question_bank = json.load(file)

                role = st.session_state.job_role
                role_questions = question_bank.get(role, {})

                available_questions = role_questions.get(
                    difficulty,
                    [],
                )

                if not available_questions:
                    st.error(
                        "No questions are available for this role "
                        "and difficulty. Check data/questions.json."
                    )
                else:
                    st.session_state.difficulty = difficulty
                    st.session_state.interview_type = interview_type
                    st.session_state.number_of_questions = (
                        number_of_questions
                    )

                    # Start with a clean interview.
                    reset_interview()

                    st.session_state.difficulty = difficulty
                    st.session_state.interview_type = interview_type
                    st.session_state.number_of_questions = (
                        number_of_questions
                    )

                    # Prioritize questions matching the selected interview type.
                    # If there are not enough matching questions, fill the
                    # remaining slots with other questions of the same level.
                    filtered_questions = list(available_questions)

                    if interview_type in ("HR", "Technical"):
                        desired_category = interview_type.lower()

                        matching = [
                            question
                            for question in available_questions
                            if desired_category in str(
                                question.get("category", "")
                            ).lower()
                        ]

                        other_questions = [
                            question
                            for question in available_questions
                            if question not in matching
                        ]

                        filtered_questions = matching + other_questions

                    requested_count = int(number_of_questions)
                    question_count = min(
                        requested_count,
                        len(filtered_questions),
                    )

                    if question_count < requested_count:
                        st.warning(
                            f"You requested {requested_count} questions, "
                            f"but only {question_count} are available for "
                            f"{role} at {difficulty} difficulty."
                        )

                    if question_count == 0:
                        st.error("No usable questions were found for this interview.")
                    else:
                        selected_questions = random.sample(
                            filtered_questions,
                            question_count,
                        )

                        st.session_state.interview_questions = selected_questions
                        st.session_state.current_question = 0
                        st.session_state.answers = []
                        st.session_state.evaluated_answers = {}

                        # Create database record for this interview.
                        candidate_id = st.session_state.get("candidate_id")

                        if candidate_id:
                            interview_id = create_interview(
                                candidate_id=candidate_id,
                                difficulty=difficulty,
                                interview_type=interview_type,
                                number_of_questions=question_count,
                            )

                            st.session_state.interview_id = interview_id

                        go_to("interview")

            except (OSError, json.JSONDecodeError) as error:
                st.error(
                    f"Could not load interview questions: {error}"
                )
            except Exception as error:
                st.error(
                    f"Unable to start the interview: {error}"
                )


# ============================================================
# INTERVIEW PAGE
# ============================================================

elif st.session_state.page == "interview":

    if "interview_questions" not in st.session_state:
        st.warning("No active interview was found.")
        if st.button("Set Up an Interview"):
            go_to("setup")
        st.stop()

    questions = st.session_state.interview_questions
    question_number = st.session_state.get("current_question", 0)

    if question_number >= len(questions):
        go_to("results")

    current_question = questions[question_number]

    if "answers" not in st.session_state:
        st.session_state.answers = []

    if "evaluated_answers" not in st.session_state:
        st.session_state.evaluated_answers = {}

    saved_result = st.session_state.evaluated_answers.get(
        question_number
    )

    show_page_header(
        "STEP 03 · INTERVIEW SESSION",
        "Interview Practice",
        "Take your time, organize your thoughts, and answer clearly.",
    )

    progress = (question_number + 1) / len(questions)

    st.progress(
        progress,
        text=(
            f"Question {question_number + 1} of {len(questions)}"
        ),
    )

    meta1, meta2, meta3 = st.columns(3)

    with meta1:
        st.caption(
            f"💼 {st.session_state.get('job_role', 'N/A')}"
        )

    with meta2:
        st.caption(
            f"📊 {st.session_state.get('difficulty', 'N/A')} Difficulty"
        )

    with meta3:
        st.caption(
            f"📝 {st.session_state.get('interview_type', 'N/A')} Interview"
        )

    st.markdown(
        f"""
        <div class="question-card">
            <div class="question-label">
                QUESTION {question_number + 1:02d}
                &nbsp; · &nbsp;
                {current_question.get("category", "General")}
            </div>
            <div class="question-text">
                {current_question.get("question", "Question unavailable.")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if saved_result is None:

        answer = st.text_area(
            "Your Answer",
            placeholder=(
                "Write your answer here. Explain your reasoning, "
                "include relevant concepts, and use examples where useful."
            ),
            height=220,
            key=f"answer_{question_number}",
        )

        st.caption(
            "Tip: A clear answer with an explanation and example "
            "can help demonstrate your understanding."
        )

        if st.button(
            "Submit Answer for Evaluation →",
            use_container_width=True,
        ):
            if not answer.strip():
                st.warning(
                    "Please enter your answer before submitting."
                )
            else:
                try:
                    expected_concepts = current_question.get(
                        "expected_concepts",
                        [],
                    )

                    basic_result = score_answer(
                        answer,
                        expected_concepts,
                    )

                    with st.spinner(
                        "🤖 AI is evaluating your answer..."
                    ):
                        ai_result = evaluate_answer(
                            current_question["question"],
                            answer,
                            expected_concepts,
                        )

                    if not isinstance(ai_result, dict):
                        raise ValueError(
                            "The evaluator did not return a valid result."
                        )

                    result = {
                        "question": current_question["question"],
                        "answer": answer.strip(),
                        "category": current_question.get(
                            "category",
                            "General",
                        ),
                        "expected_concepts": expected_concepts,
                        "score": basic_result.get("score", 0),
                        "concepts_found": basic_result.get(
                            "concepts_found",
                            0,
                        ),
                        "total_concepts": basic_result.get(
                            "total_concepts",
                            len(expected_concepts),
                        ),
                        "ai_evaluation": ai_result,
                    }

                    st.session_state.evaluated_answers[
                        question_number
                    ] = result

                    st.session_state.answers.append(result)

                    # Save evaluated answer to database.
                    interview_id = st.session_state.get("interview_id")

                    if interview_id:

                        save_answer(
                            interview_id=interview_id,
                            question=current_question["question"],
                            answer=answer.strip(),
                            category=current_question.get(
                                "category",
                                "General",
                            ),
                            score=safe_score(
                                ai_result.get("overall_score", 0)
                            ),
                            relevance=safe_score(
                                ai_result.get("relevance", 0)
                            ),
                            correctness=safe_score(
                                ai_result.get("correctness", 0)
                            ),
                            completeness=safe_score(
                                ai_result.get("completeness", 0)
                            ),
                            clarity=safe_score(
                                ai_result.get("clarity", 0)
                            ),
                            feedback=ai_result.get(
                                "feedback",
                                "",
                            ),
                            strengths=ai_result.get(
                                "strengths",
                                [],
                            ),
                            weaknesses=ai_result.get(
                                "weaknesses",
                                [],
                            ),
                        )

                        # Update interview statistics.
                        saved_scores = [
                            safe_score(
                                item.get("ai_evaluation", {}).get(
                                    "overall_score",
                                    0,
                                )
                            )
                            for item in st.session_state.answers
                        ]

                        update_interview_summary(
                            interview_id,
                            saved_scores,
                        )


                    st.rerun()

                except Exception as error:
                    st.error(
                        "Evaluation could not be completed. "
                        "Please try again."
                    )
                    st.caption(f"Details: {error}")

    else:
        ai_result = saved_result.get("ai_evaluation", {})

        st.success("Answer evaluated successfully!")

        overall_score = safe_score(
            ai_result.get("overall_score", 0)
        )

        st.markdown("### 📊 Your Evaluation")

        main_score_col, score_col1, score_col2, score_col3, score_col4 = (
            st.columns(5)
        )

        with main_score_col:
            st.metric(
                "Overall Score",
                f"{overall_score:.1f}/10",
            )

        for column, label, key in [
            (score_col1, "Relevance", "relevance"),
            (score_col2, "Correctness", "correctness"),
            (score_col3, "Completeness", "completeness"),
            (score_col4, "Clarity", "clarity"),
        ]:
            with column:
                st.metric(
                    label,
                    f"{safe_score(ai_result.get(key, 0)):.1f}/10",
                )

        st.markdown("### 💬 Your Answer")
        st.write(saved_result["answer"])

        st.markdown("### ✅ Strengths")
        strengths = ai_result.get("strengths", [])

        if isinstance(strengths, list) and strengths:
            for strength in strengths:
                st.markdown(f"- {strength}")
        else:
            st.write("No strengths were returned.")

        st.markdown("### 🎯 Areas for Improvement")
        weaknesses = ai_result.get("weaknesses", [])

        if isinstance(weaknesses, list) and weaknesses:
            for weakness in weaknesses:
                st.markdown(f"- {weakness}")
        else:
            st.write("No improvement areas were returned.")

        st.markdown("### 💡 AI Feedback")
        st.info(
            ai_result.get(
                "feedback",
                "No additional feedback is available.",
            )
        )

        st.caption(
            f"Keyword score: {saved_result.get('score', 0)}/10 "
            f"· Concepts found: "
            f"{saved_result.get('concepts_found', 0)}/"
            f"{saved_result.get('total_concepts', 0)}"
        )

        st.divider()

        if question_number + 1 < len(questions):
            if st.button(
                "Next Question →",
                use_container_width=True,
            ):
                st.session_state.current_question += 1
                st.rerun()
        else:
            st.success(
                "🎉 You have completed all the interview questions!"
            )

            if st.button(
                "View Final Results →",
                use_container_width=True,
            ):
                go_to("results")

    st.divider()

    if st.button("End Interview and View Results"):
        go_to("results")


# ============================================================
# RESULTS DASHBOARD
# ============================================================

elif st.session_state.page == "results":

    st.markdown(
        """
        <div class="hero" style="padding: 32px 24px;">
            <div class="eyebrow">INTERVIEW SUMMARY</div>
            <div style="font-size: 38px; margin: 8px 0;">📊</div>
            <div class="hero-title" style="font-size: 34px;">
                Your Performance Dashboard
            </div>
            <p class="hero-subtitle">
                Review your performance, explore AI feedback,
                and identify opportunities to improve.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    answers = st.session_state.get("answers", [])
    total_questions = len(
        st.session_state.get("interview_questions", [])
    )
    total_answered = len(answers)

    # --------------------------------------------------------
    # CANDIDATE SUMMARY
    # --------------------------------------------------------

    st.markdown("## 👤 Candidate Profile")

    with st.container(border=True):
        profile_col1, profile_col2 = st.columns(2)

        with profile_col1:
            st.markdown(
                f"**Name:** {st.session_state.get('name', 'N/A')}"
            )
            st.markdown(
                f"**Education:** "
                f"{st.session_state.get('education', 'N/A')}"
            )
            st.markdown(
                f"**Target Role:** "
                f"{st.session_state.get('job_role', 'N/A')}"
            )

        with profile_col2:
            st.markdown(
                f"**Difficulty:** "
                f"{st.session_state.get('difficulty', 'N/A')}"
            )
            st.markdown(
                f"**Interview Type:** "
                f"{st.session_state.get('interview_type', 'N/A')}"
            )
            st.markdown(
                f"**Skills:** "
                f"{st.session_state.get('skills', 'N/A') or 'Not specified'}"
            )

    st.divider()

    # --------------------------------------------------------
    # SCORE CALCULATION
    # --------------------------------------------------------

    st.markdown("## 📈 Performance Overview")

    if answers:

        scores = [
            safe_score(
                item.get("ai_evaluation", {}).get(
                    "overall_score",
                    0,
                )
            )
            for item in answers
        ]

        average_score = sum(scores) / len(scores)
        highest_score = max(scores)
        lowest_score = min(scores)

        completion = (
            total_answered / total_questions * 100
            if total_questions
            else 0
        )

        metric1, metric2, metric3, metric4 = st.columns(4)

        with metric1:
            st.metric(
                "Questions Answered",
                f"{total_answered}/{total_questions}",
            )

        with metric2:
            st.metric(
                "Average Score",
                f"{average_score:.1f}/10",
            )

        with metric3:
            st.metric(
                "Highest Score",
                f"{highest_score:.1f}/10",
            )

        with metric4:
            st.metric(
                "Completion",
                f"{completion:.0f}%",
            )

        st.progress(
            min(completion / 100, 1.0),
            text=f"Interview completion: {completion:.0f}%",
        )

        st.caption(f"Lowest score recorded: {lowest_score:.1f}/10")

        # ----------------------------------------------------
        # PERFORMANCE INTERPRETATION
        # ----------------------------------------------------

        st.markdown("## 💡 Performance Insights")

        if average_score >= 8:
            st.success(
                "Your average score is high in this session. "
                "Continue practicing to maintain consistency "
                "and refine your explanations."
            )
        elif average_score >= 6:
            st.info(
                "Your results show a developing understanding. "
                "Review the feedback below and practice the "
                "concepts that need more clarity."
            )
        else:
            st.warning(
                "Use this session as a learning opportunity. "
                "Review the explanations, revisit the relevant "
                "concepts, and try another practice interview."
            )

        # ----------------------------------------------------
        # QUESTION-WISE PERFORMANCE CHART
        # ----------------------------------------------------

        st.divider()
        st.markdown("## 📊 Question-wise Performance")

        chart_data = pd.DataFrame(
            {
                "Question": [
                    f"Q{i + 1}"
                    for i in range(len(answers))
                ],
                "Score": scores,
            }
        )

        figure = px.bar(
            chart_data,
            x="Question",
            y="Score",
            text="Score",
            range_y=[0, 10],
            color="Score",
            color_continuous_scale=[
                "#c7d2fe",
                "#6366f1",
                "#312e81",
            ],
            labels={
                "Question": "Interview Question",
                "Score": "AI Score out of 10",
            },
            hover_data={
                "Score": ":.1f",
            },
        )

        figure.update_traces(
            texttemplate="%{text:.1f}",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=0,
        )

        figure.update_layout(
            height=360,
            margin=dict(l=15, r=15, t=25, b=15),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                family="Inter, Segoe UI, sans-serif",
                color="#172554",
            ),
            yaxis=dict(
                range=[0, 11],
                dtick=2,
                gridcolor="#e0e7ff",
                zeroline=False,
            ),
            xaxis=dict(
                showgrid=False,
            ),
            coloraxis_showscale=False,
        )

        st.plotly_chart(
            figure,
            use_container_width=True,
            key="question_performance_chart",
        )

        # ----------------------------------------------------
        # CATEGORY ANALYSIS
        # ----------------------------------------------------

        st.divider()
        st.markdown("## 🧩 Category Analysis")

        category_scores = {}

        for item in answers:
            category = item.get("category", "General")
            evaluation = item.get("ai_evaluation", {})

            category_score = safe_score(
                evaluation.get("overall_score", 0)
            )

            category_scores.setdefault(
                category,
                [],
            ).append(category_score)

        category_data = pd.DataFrame(
            [
                {
                    "Category": category,
                    "Average Score": sum(values) / len(values),
                    "Questions": len(values),
                }
                for category, values in category_scores.items()
            ]
        )

        if not category_data.empty:

            category_figure = px.bar(
                category_data,
                x="Category",
                y="Average Score",
                text="Average Score",
                range_y=[0, 10],
                color="Average Score",
                color_continuous_scale=[
                    "#c7d2fe",
                    "#4f46e5",
                ],
                hover_data=["Questions"],
                labels={
                    "Average Score": "Average AI Score out of 10",
                },
            )

            category_figure.update_traces(
                texttemplate="%{text:.1f}",
                textposition="outside",
                cliponaxis=False,
                marker_line_width=0,
            )

            category_figure.update_layout(
                height=340,
                margin=dict(l=15, r=15, t=25, b=15),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    family="Inter, Segoe UI, sans-serif",
                    color="#172554",
                ),
                yaxis=dict(
                    range=[0, 11],
                    dtick=2,
                    gridcolor="#e0e7ff",
                    zeroline=False,
                ),
                xaxis=dict(showgrid=False),
                coloraxis_showscale=False,
            )

            st.plotly_chart(
                category_figure,
                use_container_width=True,
                key="category_performance_chart",
            )

        # ----------------------------------------------------
        # DIMENSION-WISE AI SCORES
        # ----------------------------------------------------

        st.divider()
        st.markdown("## 🎯 Evaluation Dimensions")

        dimensions = [
            ("Relevance", "relevance"),
            ("Correctness", "correctness"),
            ("Completeness", "completeness"),
            ("Clarity", "clarity"),
        ]

        dimension_averages = {}

        for label, key in dimensions:
            dimension_values = [
                safe_score(
                    item.get("ai_evaluation", {}).get(
                        key,
                        0,
                    )
                )
                for item in answers
            ]

            dimension_averages[label] = (
                sum(dimension_values) / len(dimension_values)
            )

        dimension_columns = st.columns(4)

        for column, (label, key) in zip(
            dimension_columns,
            dimensions,
        ):
            with column:
                st.metric(
                    label,
                    f"{dimension_averages[label]:.1f}/10",
                )

                st.progress(
                    min(dimension_averages[label] / 10, 1.0)
                )

        # ----------------------------------------------------
        # AI ANSWER REVIEW
        # ----------------------------------------------------

        st.divider()
        st.markdown("## 🤖 AI Feedback & Answer Review")

        st.write(
            "Expand a question to review your answer, evaluation "
            "scores, strengths, and improvement suggestions."
        )

        for index, item in enumerate(answers, start=1):

            evaluation = item.get("ai_evaluation", {})
            question_text = item.get(
                "question",
                f"Question {index}",
            )

            question_score = safe_score(
                evaluation.get("overall_score", 0)
            )

            with st.expander(
                f"Q{index}. {question_text} — "
                f"{question_score:.1f}/10"
            ):

                st.markdown("### ❓ Interview Question")
                st.write(question_text)

                st.markdown("### 💬 Your Answer")
                st.write(
                    item.get(
                        "answer",
                        "No answer recorded.",
                    )
                )

                st.markdown("### 📋 Evaluation Breakdown")

                score_columns = st.columns(4)

                for column, (label, key) in zip(
                    score_columns,
                    dimensions,
                ):
                    with column:
                        dimension_score = safe_score(
                            evaluation.get(key, 0)
                        )

                        st.metric(
                            label,
                            f"{dimension_score:.1f}/10",
                        )

                st.markdown("### ✅ Strengths")

                strengths = evaluation.get("strengths", [])

                if isinstance(strengths, list) and strengths:
                    for strength in strengths:
                        st.markdown(f"- {strength}")
                elif isinstance(strengths, str) and strengths.strip():
                    st.write(strengths)
                else:
                    st.write("No strengths were provided.")

                st.markdown("### 🎯 Areas for Improvement")

                weaknesses = evaluation.get("weaknesses", [])

                if isinstance(weaknesses, list) and weaknesses:
                    for weakness in weaknesses:
                        st.markdown(f"- {weakness}")
                elif isinstance(weaknesses, str) and weaknesses.strip():
                    st.write(weaknesses)
                else:
                    st.write(
                        "No improvement suggestions were provided."
                    )

                st.markdown("### 💡 Personalized Feedback")

                feedback = evaluation.get(
                    "feedback",
                    "No additional feedback is available.",
                )

                st.info(feedback)

                st.caption(
                    f"Category: {item.get('category', 'General')} "
                    f"· Keyword score: {item.get('score', 0)}/10 "
                    f"· Concepts found: "
                    f"{item.get('concepts_found', 0)}/"
                    f"{item.get('total_concepts', 0)}"
                )

    else:
        st.info(
            "No answers have been evaluated yet. Complete at least "
            "one interview question to view your performance dashboard."
        )

    # --------------------------------------------------------
    # FOOTER ACTIONS
    # --------------------------------------------------------

    st.divider()

    st.markdown("## 🚀 What's Next?")
    st.write(
        "Continue practicing to build confidence and improve "
        "your interview performance."
    )

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button(
            "🔄 Start New Interview",
            use_container_width=True,
        ):
            reset_interview()
            go_to("profile")

    with action_col2:
        if st.button(
            "🏠 Return Home",
            use_container_width=True,
        ):
            reset_interview()
            go_to("home")