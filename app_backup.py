import streamlit as st
import json
import random

from modules.scorer import score_answer
from modules.evaluator import evaluate_answer


st.set_page_config(
    page_title="INTERVISION",
    page_icon="🎤",
    layout="centered"
)


if "page" not in st.session_state:
    st.session_state.page = "home"


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

if st.session_state.page == "home":

    st.title("🎤 INTERVISION")
    st.subheader("An Intelligent Virtual Interview Simulator")

    st.write(
        "Practice interviews anytime, anywhere. INTERVISION helps "
        "you prepare with realistic questions and useful AI-powered "
        "feedback."
    )

    st.divider()

    st.markdown("### Features")

    with st.container(border=True):
        st.markdown("#### 🧠 Smart Questions")
        st.write(
            "Get interview questions based on your selected job role "
            "and difficulty."
        )

    with st.container(border=True):
        st.markdown("#### 🤖 AI Evaluation")
        st.write(
            "Gemini evaluates your answers for relevance, correctness, "
            "completeness and clarity."
        )

    with st.container(border=True):
        st.markdown("#### 📈 Interview Feedback")
        st.write(
            "Understand your strengths, weaknesses and areas for improvement."
        )

    st.divider()

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):
        st.session_state.page = "profile"
        st.rerun()


# --------------------------------------------------
# CANDIDATE PROFILE PAGE
# --------------------------------------------------

elif st.session_state.page == "profile":

    st.title("👤 Candidate Profile")

    st.write(
        "Enter your basic information before starting the interview."
    )

    name = st.text_input(
        "Full Name",
        placeholder="Enter your name"
    )

    education = st.text_input(
        "Education",
        placeholder="Example: B.E. Artificial Intelligence and Machine Learning"
    )

    skills = st.text_input(
        "Skills",
        placeholder="Example: Python, Machine Learning, SQL"
    )

    experience = st.text_area(
        "Experience",
        placeholder="Describe your projects, internships or experience."
    )

    job_role = st.selectbox(
        "Target Job Role",
        [
            "AI/ML Intern",
            "Python Developer",
            "Data Analyst",
            "Software Developer"
        ]
    )

    st.divider()

    if st.button(
        "Continue →",
        use_container_width=True
    ):

        if name.strip() == "":
            st.warning("Please enter your name.")

        elif education.strip() == "":
            st.warning("Please enter your education.")

        else:
            st.session_state.name = name
            st.session_state.education = education
            st.session_state.skills = skills
            st.session_state.experience = experience
            st.session_state.job_role = job_role
            st.session_state.page = "setup"
            st.rerun()


# --------------------------------------------------
# INTERVIEW SETUP PAGE
# --------------------------------------------------

elif st.session_state.page == "setup":

    st.title("⚙️ Interview Setup")

    st.write("Customize your interview.")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    interview_type = st.selectbox(
        "Interview Type",
        ["HR", "Technical", "Mixed"]
    )

    number_of_questions = st.selectbox(
        "Number of Questions",
        [5, 10]
    )

    st.divider()

    if st.button(
        "🎤 Start Interview",
        use_container_width=True
    ):

        st.session_state.difficulty = difficulty
        st.session_state.interview_type = interview_type
        st.session_state.number_of_questions = number_of_questions

        if "interview_questions" in st.session_state:
            del st.session_state.interview_questions

        if "answers" in st.session_state:
            del st.session_state.answers

        if "current_question" in st.session_state:
            del st.session_state.current_question

        st.session_state.page = "interview"
        st.rerun()


# --------------------------------------------------
# INTERVIEW PAGE
# --------------------------------------------------

elif st.session_state.page == "interview":

    with open("data/questions.json", "r") as file:
        question_bank = json.load(file)

    role = st.session_state.job_role
    difficulty = st.session_state.difficulty

    available_questions = question_bank[role][difficulty]

    if "interview_questions" not in st.session_state:

        number_of_questions = st.session_state.number_of_questions

        st.session_state.interview_questions = random.sample(
            available_questions,
            min(
                number_of_questions,
                len(available_questions)
            )
        )

    if "current_question" not in st.session_state:
        st.session_state.current_question = 0

    if "answers" not in st.session_state:
        st.session_state.answers = []

    question_number = st.session_state.current_question

    current_question = st.session_state.interview_questions[
        question_number
    ]

    st.write(
        f"### Question {question_number + 1} "
        f"of {len(st.session_state.interview_questions)}"
    )

    st.divider()

    st.markdown(
        f"### {current_question['question']}"
    )

    st.caption(
        f"Category: {current_question['category']}"
    )

    answer = st.text_area(
        "Your Answer",
        placeholder="Type your answer here...",
        height=180,
        key=f"answer_{question_number}"
    )

    st.divider()

    if st.button(
        "Submit Answer →",
        use_container_width=True
    ):

        if answer.strip() == "":
            st.warning(
                "Please enter your answer before continuing."
            )

        else:

            basic_result = score_answer(
                answer,
                current_question["expected_concepts"]
            )

            try:

                with st.spinner(
                    "🤖 Gemini is evaluating your answer..."
                ):

                    ai_result = evaluate_answer(
                        current_question["question"],
                        answer,
                        current_question["expected_concepts"]
                    )

                st.subheader("🤖 AI Evaluation")

                st.metric(
                    "Overall Score",
                    f"{ai_result['overall_score']}/10"
                )

                st.write(
                    f"**Relevance:** "
                    f"{ai_result['relevance']}/10"
                )

                st.write(
                    f"**Correctness:** "
                    f"{ai_result['correctness']}/10"
                )

                st.write(
                    f"**Completeness:** "
                    f"{ai_result['completeness']}/10"
                )

                st.write(
                    f"**Clarity:** "
                    f"{ai_result['clarity']}/10"
                )

                st.write("### ✅ Strengths")

                for strength in ai_result["strengths"]:
                    st.write(f"- {strength}")

                st.write("### ⚠️ Areas to Improve")

                for weakness in ai_result["weaknesses"]:
                    st.write(f"- {weakness}")

                st.write("### 💡 Feedback")

                st.info(
                    ai_result["feedback"]
                )

            except Exception as error:

                st.error(
                    "Gemini evaluation could not be completed."
                )

                st.write(
                    f"Error: {error}"
                )

                ai_result = {
                    "overall_score": 0,
                    "relevance": 0,
                    "correctness": 0,
                    "completeness": 0,
                    "clarity": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "feedback": "AI evaluation was unavailable."
                }

            st.session_state.answers.append(
                {
                    "question": current_question["question"],
                    "answer": answer,
                    "category": current_question["category"],
                    "expected_concepts": current_question[
                        "expected_concepts"
                    ],
                    "score": basic_result["score"],
                    "concepts_found": basic_result["concepts_found"],
                    "total_concepts": basic_result["total_concepts"],
                    "ai_evaluation": ai_result
                }
            )

            st.success(
                "Answer evaluated successfully! ✅"
            )

        if (
            question_number + 1
            < len(st.session_state.interview_questions)
        ):

            if st.button(
                "Next Question →",
                use_container_width=True
            ):

                st.session_state.current_question += 1
                st.rerun()

            else:

                st.success(
                    "🎉 Interview completed!"
                )

                if st.button(
                    "View Final Results →",
                    use_container_width=True
                ):

                    st.session_state.page = "results"
                    st.rerun()


# --------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------

elif st.session_state.page == "results":

    st.title("📊 Interview Results")

    st.success(
        "Your INTERVISION interview is complete!"
    )

    st.divider()

    st.subheader("👤 Candidate")

    st.write(
        f"**Name:** {st.session_state.name}"
    )

    st.write(
        f"**Education:** {st.session_state.education}"
    )

    st.write(
        f"**Target Role:** {st.session_state.job_role}"
    )

    st.write(
        f"**Difficulty:** {st.session_state.difficulty}"
    )

    st.divider()

    for index, item in enumerate(
        st.session_state.answers
    ):

        st.subheader(
            f"Question {index + 1}"
        )

        st.write(
            f"**Question:** {item['question']}"
        )

        st.write(
            f"**Your Answer:** {item['answer']}"
        )

        st.write(
            f"**Basic Score:** {item['score']}/10"
        )

        st.write(
            f"**Concepts identified:** "
            f"{item['concepts_found']} / "
            f"{item['total_concepts']}"
        )

        ai_result = item.get(
            "ai_evaluation"
        )

        if ai_result:

            st.markdown(
                "#### 🤖 AI Evaluation"
            )

            st.write(
                f"**Overall:** "
                f"{ai_result['overall_score']}/10"
            )

            st.write(
                f"**Relevance:** "
                f"{ai_result['relevance']}/10"
            )

            st.write(
                f"**Correctness:** "
                f"{ai_result['correctness']}/10"
            )

            st.write(
                f"**Completeness:** "
                f"{ai_result['completeness']}/10"
            )

            st.write(
                f"**Clarity:** "
                f"{ai_result['clarity']}/10"
            )

            st.write(
                "**Strengths:**"
            )

            for strength in ai_result["strengths"]:
                st.write(
                    f"- {strength}"
                )

            st.write(
                "**Areas to Improve:**"
            )

            for weakness in ai_result["weaknesses"]:
                st.write(
                    f"- {weakness}"
                )

            st.write(
                "**Feedback:**"
            )

            st.info(
                ai_result["feedback"]
            )

        st.divider()

    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        st.session_state.page = "profile"

        if "interview_questions" in st.session_state:
            del st.session_state.interview_questions

        if "answers" in st.session_state:
            del st.session_state.answers

        if "current_question" in st.session_state:
            del st.session_state.current_question

        st.rerun()

