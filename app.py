import random

import streamlit as st

from midi_engine import create_midi, create_wav


APP_TITLE = "Akkordfolgen-Training"

PROGRESSIONS = [
    "I - V - vi - IV",
    "I - vi - IV - V",
    "vi - IV - I - V",
    "I - IV - V - I",
    "ii - V - I - vi",
    "I - V - IV - V",
    "I - IV - vi - V",
    "vi - V - IV - V",
    "I - iii - vi - IV",
    "IV - V - iii - vi",
]

ROOTS = ["C", "D", "E", "F", "G", "A", "Bb"]


def normalize_progression(text: str) -> str:
    return " - ".join(part.strip() for part in text.split("-"))


def make_exercise() -> dict:
    correct = random.choice(PROGRESSIONS)
    distractors = random.sample([item for item in PROGRESSIONS if item != correct], 3)
    options = distractors + [correct]
    random.shuffle(options)
    root = random.choice(ROOTS)

    return {
        "id": random.randint(100000, 999999),
        "root": root,
        "correct": correct,
        "options": options,
        "audio": create_wav(root=root, scale_name="Dur", progression_text=correct),
        "midi": create_midi(
            root=root,
            scale_name="Dur",
            progression_text=correct,
            bpm=86,
            bars=4,
            pattern="Akkorde",
        ),
    }


def new_exercise() -> None:
    st.session_state.exercise = make_exercise()
    st.session_state.feedback = None
    st.session_state.answered = False


def reset_score() -> None:
    st.session_state.correct_count = 0
    st.session_state.total_count = 0
    st.session_state.feedback = None


def submit_answer(answer: str) -> None:
    if st.session_state.answered:
        return

    st.session_state.answered = True
    st.session_state.total_count += 1

    correct = st.session_state.exercise["correct"]
    if answer == correct:
        st.session_state.correct_count += 1
        st.session_state.feedback = "Richtig."
    else:
        st.session_state.feedback = f"Noch nicht. Richtig war: {normalize_progression(correct)}"


st.set_page_config(
    page_title=APP_TITLE,
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": f"{APP_TITLE}: ein kleines Uebetool fuer den LMS-Kurs.",
    },
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 760px;
        padding-top: 1.1rem;
        padding-bottom: 1.1rem;
    }
    div[data-testid="stMetric"] {
        background: #f6f7f9;
        border: 1px solid #e3e7ee;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
    }
    div[data-testid="stButton"] > button {
        min-height: 3rem;
        font-size: 1rem;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "exercise" not in st.session_state:
    new_exercise()
if "correct_count" not in st.session_state:
    reset_score()
if "total_count" not in st.session_state:
    st.session_state.total_count = 0
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "answered" not in st.session_state:
    st.session_state.answered = False

exercise = st.session_state.exercise
answered = st.session_state.answered
total_count = st.session_state.total_count
correct_count = st.session_state.correct_count
accuracy = 0 if total_count == 0 else round((correct_count / total_count) * 100)

st.title(APP_TITLE)

score_left, score_mid, score_right = st.columns(3)
score_left.metric("Richtig", correct_count)
score_mid.metric("Versuche", total_count)
score_right.metric("Quote", f"{accuracy}%")

st.audio(exercise["audio"], format="audio/wav")

st.subheader("Welche Akkordfolge hoerst du?")

for option in exercise["options"]:
    st.button(
        normalize_progression(option),
        key=f"{exercise['id']}_{option}",
        disabled=answered,
        use_container_width=True,
        on_click=submit_answer,
        args=(option,),
    )

if st.session_state.feedback:
    if st.session_state.feedback == "Richtig.":
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)

actions_left, actions_right = st.columns([1, 1])
with actions_left:
    if st.button("Naechste Aufgabe", type="primary", use_container_width=True):
        new_exercise()
        st.rerun()
with actions_right:
    st.download_button(
        "MIDI herunterladen",
        data=exercise["midi"],
        file_name="akkordfolge.mid",
        mime="audio/midi",
        use_container_width=True,
    )

if st.button("Fortschritt zuruecksetzen", use_container_width=True):
    reset_score()
    new_exercise()
    st.rerun()
