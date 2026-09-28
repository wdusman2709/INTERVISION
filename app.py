import streamlit as st

# 1. Page setup
st.set_page_config(page_title="INTERVISION", page_icon="🎤", layout="centered")

# 2. Title and subtitle
st.title("🎤 INTERVISION")
st.subheader("An Intelligent Virtual Interview Simulator")

# 3. Short description
st.write(
    "Practice interviews anytime, anywhere. INTERVISION helps you prepare "
    "with realistic questions and useful feedback, so you can walk into "
    "your next interview with confidence."
)

st.divider()

# 4. Feature cards
st.markdown("### Features")

with st.container(border=True):
    st.markdown("#### 🧠 Smart Questions")
    st.write("Get interview questions based on your chosen role.")

with st.container(border=True):
    st.markdown("#### 💬 Instant Feedback")
    st.write("Learn what you did well and what to improve.")

with st.container(border=True):
    st.markdown("#### 📈 Track Progress")
    st.write("See how your skills grow with every practice session.")

st.divider()

# 5. Start Interview button
if st.button("🚀 Start Interview", use_container_width=True):
    st.success("Interview module coming soon!")
