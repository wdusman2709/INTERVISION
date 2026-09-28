import streamlit as st
import json
import random

from modules.scorer import score_answer
# --------------------------------------------------
# 1. Page setup
# --------------------------------------------------

st.set_page_config(
    page_title="INTERVISION",
    page_icon="🎤",
    layout="centered"
)


# --------------------------------------------------
# 2. Create session state
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "home"


# --------------------------------------------------
# 3. HOME PAGE
# --------------------------------------------------

if st.session_state.page == "home":

    st.title("🎤 INTERVISION")
    st.subheader("An Intelligent Virtual Interview Simulator")

    st.write(
        "Practice interviews anytime, anywhere. INTERVISION helps you "
        "prepare with realistic questions and useful feedback, so you "
        "can walk into your next interview with confidence."
    )

    st.divider()

    st.markdown("### Features")

    with st.container(border=True):
        st.markdown("#### 🧠 Smart Questions")
        st.write(
            "Get interview questions based on your chosen role."
        )

    with st.container(border=True):
        st.markdown("#### 💬 Instant Feedback")
        st.write(
            "Learn what you did well and what to improve."
        )

    with st.container(border=True):
        st.markdown("#### 📈 Track Progress")
        st.write(
            "See how your skills grow with every practice session."
        )

    st.divider()

    if st.button("🚀 Start Interview", use_container_width=True):

        st.session_state.page = "profile"

        st.rerun()


# --------------------------------------------------
# 4. CANDIDATE PROFILE PAGE
# --------------------------------------------------

elif st.session_state.page == "profile":

    st.title("👤 Candidate Profile")

    st.write(
        "Tell us a little about yourself so INTERVISION can "
        "personalize your interview."
    )

    st.divider()

    # Candidate profile form

    with st.form("candidate_profile_form"):

        name = st.text_input(
            "Full Name",
            placeholder="Enter your full name"
        )

        education = st.text_input(
            "Education",
            placeholder="Example: B.E. Artificial Intelligence & Machine Learning"
        )

        skills = st.text_input(
            "Skills",
            placeholder="Example: Python, SQL, Machine Learning"
        )

        experience = st.text_area(
            "Experience",
            placeholder="Example: Fresher / Internship / Project experience"
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

        submitted = st.form_submit_button(
            "Continue to Interview Setup →",
            use_container_width=True
        )

    # Save candidate information

    if submitted:

        if name.strip() == "":
            st.error("Please enter your name.")

        elif education.strip() == "":
            st.error("Please enter your education.")

        elif skills.strip() == "":
            st.error("Please enter at least one skill.")

        else:

            st.session_state.name = name
            st.session_state.education = education
            st.session_state.skills = skills
            st.session_state.experience = experience
            st.session_state.job_role = job_role

            st.success("Profile saved successfully! ✅")

            st.session_state.page = "setup"

            st.rerun()


# --------------------------------------------------
# 5. INTERVIEW SETUP PAGE
# --------------------------------------------------

elif st.session_state.page == "setup":

    st.title("⚙️ Interview Setup")

    st.write(
        "Configure your interview before starting."
    )

    st.divider()

    # Show candidate information

    st.write(
        f"**Candidate:** {st.session_state.name}"
    )

    st.write(
        f"**Target Role:** {st.session_state.job_role}"
    )

    st.divider()

    # Interview configuration

    difficulty = st.selectbox(
        "🎯 Difficulty Level",
        [
            "Easy",
            "Medium",
            "Hard"
        ]
    )

    interview_type = st.selectbox(
        "🧠 Interview Type",
        [
            "HR",
            "Technical",
            "Mixed"
        ]
    )

    number_of_questions = st.selectbox(
        "❓ Number of Questions",
        [
            5,
            10
        ]
    )

    st.divider()

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        # Save interview settings

        st.session_state.difficulty = difficulty
        st.session_state.interview_type = interview_type
        st.session_state.number_of_questions = number_of_questions

        st.session_state.page = "interview"

        st.rerun()

    if st.button(
        "⬅️ Back to Profile",
        use_container_width=True
    ):

        st.session_state.page = "profile"

        st.rerun()


# --------------------------------------------------
# 6. INTERVIEW PAGE
# --------------------------------------------------

elif st.session_state.page == "interview":

    st.title("🎤 INTERVISION Interview")

    # Load question bank
    with open("data/questions.json", "r") as file:
        question_bank = json.load(file)

    # Get selected role and difficulty
    role = st.session_state.job_role
    difficulty = st.session_state.difficulty

    # Get available questions
    available_questions = question_bank[role][difficulty]

    # Create the interview questions only once
    if "interview_questions" not in st.session_state:

        number_of_questions = st.session_state.number_of_questions

        st.session_state.interview_questions = random.sample(
            available_questions,
            min(number_of_questions, len(available_questions))
        )

        st.session_state.current_question = 0

    # Create answer storage only once
    if "answers" not in st.session_state:
        st.session_state.answers = []

    # Current question number
    question_number = st.session_state.current_question

    # Get current question
    current_question = st.session_state.interview_questions[
        question_number
    ]

    # Display question number
    st.write(
        f"**Question {question_number + 1} "
        f"of {len(st.session_state.interview_questions)}**"
    )

    st.divider()

    # Display question
    st.markdown(
        f"### {current_question['question']}"
    )

    st.caption(
        f"Category: {current_question['category']}"
    )

    # Answer box
    answer = st.text_area(
        "Your Answer",
        placeholder="Type your answer here...",
        height=180,
        key=f"answer_{question_number}"
    )

    # Submit answer
    if st.button(
        "Submit Answer →",
        use_container_width=True
    ):

        if answer.strip() == "":
            st.warning(
                "Please enter your answer before continuing."
            )

        else:

            # Save the answer
            st.session_state.answers.append({
                "question": current_question["question"],
                "answer": answer,
                "category": current_question["category"],
                "expected_concepts": current_question[
                    "expected_concepts"
                ]
            })

            st.success(
                "Answer saved successfully! ✅"
            )

            # Check if more questions remain
            if (
                question_number + 1
                < len(st.session_state.interview_questions)
            ):

                st.session_state.current_question += 1

                st.rerun()

            else:

                # Interview completed
                st.session_state.page = "results"

                st.rerun()


# --------------------------------------------------
# 7. RESULTS PAGE
# --------------------------------------------------

elif st.session_state.page == "results":

    st.title("📊 Interview Results")

    st.success(
        "🎉 Interview completed successfully!"
    )

    st.write(
        f"**Candidate:** {st.session_state.name}"
    )

    st.write(
        f"**Role:** {st.session_state.job_role}"
    )

    st.write(
        f"**Difficulty:** {st.session_state.difficulty}"
    )

    st.divider()

    st.subheader("📝 Your Answers")

    for index, item in enumerate(
        st.session_state.answers
    ):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            item["question"]
        )

        st.markdown("**Your Answer:**")

        st.info(
            item["answer"]
        )

        st.caption(
            f"Category: {item['category']}"
        )

        st.divider()
