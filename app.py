import streamlit as st

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

    st.title("🎤 Interview")

    st.success("Interview module is ready for the next step.")

    st.write(
        f"**Role:** {st.session_state.job_role}"
    )

    st.write(
        f"**Difficulty:** {st.session_state.difficulty}"
    )

    st.write(
        f"**Interview Type:** {st.session_state.interview_type}"
    )

    st.write(
        f"**Questions:** {st.session_state.number_of_questions}"
    )

    st.divider()

    st.info(
        "Question Engine will be added next."
    )
