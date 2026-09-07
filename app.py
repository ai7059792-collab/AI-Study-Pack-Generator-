import streamlit as st
from ai_workflow import run_study_pack_workflow

st.set_page_config(
    page_title="Personalized AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Personalized AI Study Pack Generator")
st.caption("Staged AI workflow: Planning → Content Generation → Quality Review → Repair → Final Verification")

with st.sidebar:
    st.header("Learner Profile")
    name = st.text_input("Learner name", "Student")
    subject = st.text_input("Subject", "Computer Science")
    topic = st.text_input("Topic", "Artificial Intelligence")
    level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced"])
    learning_goal = st.text_area(
        "Learning goal",
        "Understand the topic clearly and prepare for an assessment."
    )
    study_time = st.slider("Available study time (minutes)", 15, 180, 60, 15)
    difficulty = st.select_slider(
        "Preferred difficulty",
        options=["Easy", "Balanced", "Challenging"],
        value="Balanced",
    )
    pack_length = st.selectbox("Pack length", ["Short", "Standard", "Detailed"])
    question_count = st.slider("Practice questions", 3, 20, 8)

st.divider()

st.subheader("Generate your study pack")
extra_notes = st.text_area(
    "Optional instructions",
    placeholder="Example: Focus on exam-style questions, include analogies, or emphasize weak areas."
)

if st.button("🚀 Generate Study Pack", type="primary", use_container_width=True):
    profile = {
        "name": name,
        "subject": subject,
        "topic": topic,
        "level": level,
        "learning_goal": learning_goal,
        "study_time": study_time,
        "difficulty": difficulty,
        "pack_length": pack_length,
        "question_count": question_count,
        "extra_notes": extra_notes,
    }

    try:
        with st.status("Running staged AI workflow...", expanded=True) as status:
            st.write("1. Planning personalized learning path...")
            result = run_study_pack_workflow(profile)

            st.write("2. Generating study content...")
            st.write("3. Reviewing quality and consistency...")
            if result.get("repaired"):
                st.write("4. Repairing detected issues...")
            st.write("5. Running final deterministic verification...")
            status.update(label="Study pack generated successfully.", state="complete")

        st.success(f"Final quality score: {result['quality_score']}/100")

        cols = st.columns(4)
        cols[0].metric("Plan", "Complete")
        cols[1].metric("Content", "Complete")
        cols[2].metric("Review", result["review_status"])
        cols[3].metric("Verification", result["verification_status"])

        with st.expander("View workflow diagnostics"):
            st.json({
                "quality_score": result["quality_score"],
                "repaired": result["repaired"],
                "review": result["review"],
                "verification": result["verification"],
            })

        st.subheader("Your Personalized Study Pack")
        st.markdown(result["final_pack"])

        st.download_button(
            "⬇️ Download Study Pack",
            data=result["final_pack"],
            file_name=f"{topic.replace(' ', '_').lower()}_study_pack.md",
            mime="text/markdown",
            use_container_width=True,
        )

    except Exception as exc:
        st.error("The workflow could not complete.")
        st.exception(exc)

st.divider()
st.caption("API keys should be stored in Streamlit Secrets, not inside source code.")
