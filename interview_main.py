from time import sleep
import streamlit as st
from services.interview_api_openai import generate_question, grade_answer
import json

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(page_title="Interview Practice App", layout="centered")

# -----------------------------
# Session state (UI state only)
# -----------------------------
if "level" not in st.session_state:
    st.session_state.level = "Medium"

if "question_text" not in st.session_state:
    st.session_state.question_text = ""

if "answer_text" not in st.session_state:
    st.session_state.answer_text = ""

if "feedback_text" not in st.session_state:
    st.session_state.feedback_text = ""

if "tts_audio_bytes" not in st.session_state:
    st.session_state.tts_audio_bytes = None

if "show_recorder" not in st.session_state:
    st.session_state.show_recorder = False

if "recorded_audio_bytes" not in st.session_state:
    st.session_state.recorded_audio_bytes = None
# global question object to hold rubric etc.
if "full_question_json" not in st.session_state:
    st.session_state.full_question_json = None

if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = []

def reset_to_initial():
    """Clears boxes and returns UI to initial stage (called on Next question)."""
    st.session_state.question_text = ""
    st.session_state.answer_text = ""
    st.session_state.feedback_text = ""
    st.session_state.tts_audio_bytes = None
    st.session_state.show_recorder = False
    st.session_state.recorded_audio_bytes = None


# -----------------------------
# Header + instructions
# -----------------------------
st.header("Interview Practice App")

st.info(
    "1) Select the interview level.\n"
    "2) Click **Next question** to get a new question.\n"
    "3) Answer by typing (or record), then click **Finish** for feedback."
)

# -----------------------------
# Level selector
# -----------------------------
st.session_state.level = st.radio(
    "Select interview level",
    options=["Easy", "Medium", "Hard"],
    horizontal=True,
    index=["Easy", "Medium", "Hard"].index(st.session_state.level),
)

st.divider()

# Handy flags used to disable/enable UI elements
question_empty = (st.session_state.question_text.strip() == "")
answer_empty = (st.session_state.answer_text.strip() == "")

# -----------------------------
# Interviewer box
# -----------------------------
st.subheader("Interviewer")

st.text_area(
    label="Question",
    value=st.session_state.question_text,
    height=120,
    disabled=True,
    placeholder="Click “Next question” to display a question here...",
)

col_q1, col_q2 = st.columns([1, 1])

with col_q1:
    if st.button("Next question", use_container_width=True):
        # Reset everything to initial stage first
        reset_to_initial()

        # TODO: Call your question generation function here and assign result to st.session_state.question_text

        # Placeholder question so you can see the UI behavior:
        st.session_state.question_text = "Generating..."
        
        with st.spinner("Generating next question..."):
            # sleep(5)

            # print on console for debugging the parameters for generate_question
            print("Generating question with parameters:")
            print(f"  position: Software Engineer")
            print(f"  subject: iOS - Swift programming")
            print(f"  difficulty: {st.session_state.level}")
            print(f"  persona: friendly")
            print(f"  num_followups: 2")
            print(f"  clarification_allowance: 1")
            print(f"  avoid_questions: {st.session_state.asked_questions}")
            print(f"  level: {st.session_state.level}")

            question = generate_question(
                position="Software Engineer",
                subject="iOS - Swift programming",
                difficulty=st.session_state.level,
                persona="friendly",
                num_followups=2,
                clarification_allowance=1,
                avoid_questions=st.session_state.asked_questions,
        )  
            # Store full question object for grading later
            st.session_state.full_question_json = question 
            # Append to asked questions to avoid repeats
            st.session_state.asked_questions.append(question["question"])
            st.session_state.question_text = (
                f"{question['question']} followups: {question['followups']}"
            )
        st.rerun()

with col_q2:
    # ✅ Not allow to press Listen if question is empty
    if st.button("Listen", use_container_width=True, disabled=question_empty):
        # TODO: Call OpenAI TTS here using the question text, then store bytes in st.session_state.tts_audio_bytes
        # Example (DO NOT call now):
        #   st.session_state.tts_audio_bytes = tts_bytes
        st.session_state.tts_audio_bytes = None  # placeholder

# If you generate real audio bytes, show the player:
if st.session_state.tts_audio_bytes:
    st.audio(st.session_state.tts_audio_bytes, format="audio/mp3")

st.divider()

# Recompute flags (Streamlit reruns top-to-bottom after button clicks)
question_empty = (st.session_state.question_text.strip() == "")
answer_empty = (st.session_state.answer_text.strip() == "")

# -----------------------------
# Answer box
# -----------------------------
st.subheader("Answer")

# ✅ Not allow to type answer if "Next question" not pressed (i.e., question is empty)
st.session_state.answer_text = st.text_area(
    label="Your answer",
    value=st.session_state.answer_text,
    height=160,
    placeholder="Type your answer here...",
    disabled=question_empty,
)

# Recompute answer_empty after text area renders
answer_empty = (st.session_state.answer_text.strip() == "")

col_a1, col_a2 = st.columns([1, 1])

with col_a1:
    # ✅ Not allow to press Finish if answer is empty OR question is empty
    if st.button("Finish", use_container_width=True, disabled=(question_empty or answer_empty)):
        # TODO: Call your grading/evaluation function here using:
        #   - st.session_state.question_text (and rubric if stored)
        #   - st.session_state.answer_text OR transcribed recorded audio
        # Example (DO NOT call now):
        #   report = grade_answer(q_obj, st.session_state.answer_text)
        #   st.session_state.feedback_text = format_report(report)

        feedback = grade_answer(
            st.session_state.full_question_json,
            st.session_state.answer_text,
        )
        st.session_state.feedback_text = (json.dumps(feedback, indent=2))
    
        # # Placeholder feedback:
        # st.session_state.feedback_text = (
        #     "Overall: 3/5\n"
        #     "- Swift fundamentals: 3/5 (OK explanation, missing closure capture list detail)\n"
        #     "- Memory management: 3/5 (mention weak/unowned and a concrete example)\n\n"
        #     "Tip: Add a short code snippet showing [weak self] in a closure."
        # )
        st.rerun()

with col_a2:
    # ✅ Not allow to press Recording if question is empty
    if st.button("Recording", use_container_width=True, disabled=question_empty):
        st.session_state.show_recorder = not st.session_state.show_recorder

# Optional recording UI (shown when Recording toggled on)
if st.session_state.show_recorder:
    st.caption("Record your answer (optional).")

    # Streamlit versions differ. If `st.audio_input` exists, use it.
    # Otherwise, fall back to uploading an audio file.
    if hasattr(st, "audio_input"):
        audio = st.audio_input("Record audio")
        if audio is not None:
            st.session_state.recorded_audio_bytes = audio.read()
            st.audio(st.session_state.recorded_audio_bytes)
            # TODO: Send recorded bytes to transcription, then use text for grading
    else:
        uploaded = st.file_uploader("Upload an audio file instead", type=["mp3", "wav", "m4a"])
        if uploaded is not None:
            st.session_state.recorded_audio_bytes = uploaded.read()
            st.audio(st.session_state.recorded_audio_bytes)
            # TODO: Send uploaded bytes to transcription, then use text for grading

st.divider()

# -----------------------------
# Feedback box
# -----------------------------
st.subheader("FeedBack")

st.text_area(
    label="Feedback",
    value=st.session_state.feedback_text,
    height=180,
    disabled=True,
    placeholder="Feedback will appear here after you click Finish.",
)
