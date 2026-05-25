import random

import streamlit as st

from midi_engine import create_midi, create_wav


APP_TITLE = "Auralingo"
ROOTS = ["C", "D", "E", "F", "G", "A", "Bb"]
INSTRUMENTS = ["Orgel", "E-Piano", "Synth"]
MIDI_PROGRAMS = {
    "Orgel": 16,
    "E-Piano": 4,
    "Synth": 88,
}
ROMAN_NUMBERS = {
    "I": "1",
    "II": "2",
    "III": "3",
    "IV": "4",
    "V": "5",
    "VI": "6",
    "VII": "7",
}

LEVELS = {
    "level_1": {
        "title": "Level 1: Dur & Kadenzen",
        "scale_name": "Dur",
        "items": [
            {"progression": "I - V - VIm - IV", "gesture": "stabil -> dominantisch -> Mollfarbe -> Rueckung", "tip": "Achte auf den grossen Sprung von 1 nach 5 und den Schritt 5-6."},
            {"progression": "VIm - IV - I - V", "gesture": "Mollstart -> Rueckung -> Zuhause -> offen", "tip": "Der Anfang klingt dunkler, weil die Folge auf 6 startet."},
            {"progression": "I - VIm - IV - V", "gesture": "stabil -> Mollfarbe -> Rueckung -> Zug", "tip": "Nach dem Start faellt der Bass erst nach 6 und dann nach 4."},
            {"progression": "I - IV - V - I", "gesture": "Zuhause -> Weg -> Spannung -> Ankunft", "tip": "Hoere auf die klare Schlussbewegung 5-1."},
            {"progression": "I - V - IV - V", "gesture": "stabil -> Spannung -> Rueckung -> offen", "tip": "Der Schluss bleibt auf 5 stehen und will weiter."},
            {"progression": "IIm - V - I - VIm", "gesture": "Vorspannung -> Spannung -> Ankunft -> Farbe", "tip": "Die ersten drei Stationen bilden eine starke 2-5-1-Richtung."},
            {"progression": "I - IIIm - VIm - IV", "gesture": "stabil -> zart -> Mollfarbe -> Rueckung", "tip": "Die Mitte klingt weniger zielgerichtet als bei 1-5-6-4."},
            {"progression": "IV - V - IIIm - VIm", "gesture": "Rueckung -> Spannung -> zart -> Mollfarbe", "tip": "Die Folge startet nicht zu Hause, sondern auf 4."},
            {"progression": "I - IV - VIm - V", "gesture": "Zuhause -> Rueckung -> Mollfarbe -> Zug", "tip": "Der Schluss geht von 6 nach 5 und bleibt gespannt."},
            {"progression": "I - VIm - IIm - V", "gesture": "Zuhause -> Mollfarbe -> Vorspannung -> Spannung", "tip": "Die zweite Haelfte fuehrt klar auf 5 hin."},
            {"progression": "IV - I - V - VIm", "gesture": "Rueckung -> Zuhause -> Spannung -> Mollfarbe", "tip": "Achte darauf, dass die Folge nicht auf 1 beginnt."},
            {"progression": "VIm - V - IV - V", "gesture": "Mollfarbe -> Spannung -> Rueckung -> offen", "tip": "Der Bass geht 6-5-4-5."},
            {"progression": "I - IV - I - V", "gesture": "Zuhause -> Rueckung -> Zuhause -> offen", "tip": "Die Rueckkehr nach 1 kommt vor dem offenen Schluss auf 5."},
            {"progression": "I - IIIm - IV - V", "gesture": "Zuhause -> zart -> Rueckung -> Spannung", "tip": "Der Bass steigt nicht schrittweise, sondern springt von 1 nach 3."},
            {"progression": "I - IIm - V - I", "gesture": "Zuhause -> Vorspannung -> Spannung -> Ankunft", "tip": "Die zweite Haelfte klingt wie eine klassische 2-5-1-Bewegung."},
            {"progression": "I - IV - V - VIm", "gesture": "Zuhause -> Rueckung -> Spannung -> Mollfarbe", "tip": "Nach 5 erwartest du 1, bekommst aber 6."},
        ],
    },
    "level_2": {
        "title": "Level 2: Mollkontexte",
        "scale_name": "Natuerlich Moll",
        "items": [
            {"progression": "Im - VII - VI - VII", "gesture": "Mollzentrum -> Rueckung -> tiefere Farbe -> Rueckung", "tip": "Der Bass pendelt zwischen 1, 7 und 6."},
            {"progression": "Im - VI - III - VII", "gesture": "Mollzentrum -> Farbe -> Durweite -> Rueckung", "tip": "Nach 1 faellt der Bass nach 6 und springt dann nach 3."},
            {"progression": "Im - IVm - VII - III", "gesture": "Mollzentrum -> Mollsubdominante -> Rueckung -> Durweite", "tip": "Die erste Haelfte bleibt dunkel, die zweite oeffnet sich."},
            {"progression": "Im - IVm - Vm - Im", "gesture": "Mollzentrum -> Mollsubdominante -> Molldominante -> Rueckkehr", "tip": "Die Schlussbewegung 5-1 ist weniger scharf als im Dur-Kontext."},
            {"progression": "Im - IVm - V - Im", "gesture": "Mollzentrum -> Mollsubdominante -> Durdominante -> Rueckkehr", "tip": "Der Dur-V erzeugt im Mollkontext eine staerkere Schlusswirkung als Vm."},
            {"progression": "Im - VII - VI - V", "gesture": "Mollzentrum -> Rueckung -> Farbe -> Spannung", "tip": "Der Dur-V am Schluss zieht staerker als Vm."},
            {"progression": "Im - III - VII - VI", "gesture": "Mollzentrum -> Durweite -> Rueckung -> Farbe", "tip": "Achte auf den grossen Sprung von 1 nach 3."},
            {"progression": "Im - VI - VII - Im", "gesture": "Mollzentrum -> Farbe -> Rueckung -> Rueckkehr", "tip": "Die Folge kommt am Ende wieder nach 1 zurueck."},
        ],
    },
    "level_3": {
        "title": "Level 3: Borrowed Chords",
        "scale_name": "Dur",
        "items": [
            {"progression": "I - bVII - IV - I", "gesture": "Zuhause -> tiefe Rueckung -> Rueckung -> Zuhause", "tip": "Die Stufe bVII liegt einen Halbton tiefer als VII und klingt modal."},
            {"progression": "I - bVI - bVII - I", "gesture": "Zuhause -> dunkle Farbe -> Rueckung -> Zuhause", "tip": "Hoere die chromatische Farbe von bVI und bVII."},
            {"progression": "I - IVm - I - V", "gesture": "Zuhause -> Mollfaerbung -> Zuhause -> Spannung", "tip": "Die IV wird hier zur Mollstufe."},
            {"progression": "I - bIII - IV - I", "gesture": "Zuhause -> fremde Durfarbe -> Rueckung -> Zuhause", "tip": "bIII hebt sich deutlich vom diatonischen IIIm ab."},
            {"progression": "I - bVII - bVI - V", "gesture": "Zuhause -> Rueckung -> dunkle Farbe -> Spannung", "tip": "Der Bass faellt von b7 nach b6 und geht dann nach 5."},
            {"progression": "I - IV - IVm - I", "gesture": "Zuhause -> Rueckung -> Mollfaerbung -> Zuhause", "tip": "Vergleiche IV und IVm direkt miteinander."},
            {"progression": "I - bVI - IV - V", "gesture": "Zuhause -> dunkle Farbe -> Rueckung -> Spannung", "tip": "bVI ist der auffaellige Farbakzent."},
            {"progression": "bVII - IV - I - V", "gesture": "modale Rueckung -> Rueckung -> Zuhause -> Spannung", "tip": "Die Folge startet bewusst nicht auf 1."},
        ],
    },
}


def normalize_progression(text: str) -> str:
    return " - ".join(part.strip() for part in text.split("-"))


def bass_label_from_progression(text: str) -> str:
    labels = []
    for part in text.split("-"):
        symbol = part.strip()
        accidental = ""
        if symbol.startswith("b"):
            accidental = "b"
            symbol = symbol[1:]
        elif symbol.startswith("#"):
            accidental = "#"
            symbol = symbol[1:]
        core = symbol.removesuffix("min").removesuffix("m").upper()
        labels.append(f"{accidental}{ROMAN_NUMBERS.get(core, core)}")
    return " - ".join(labels)


def shuffled_options(correct: str, pool: list[str], count: int = 4) -> list[str]:
    unique_pool = [item for item in dict.fromkeys(pool) if item != correct]
    options = random.sample(unique_pool, min(count - 1, len(unique_pool))) + [correct]
    random.shuffle(options)
    return options


def close_progression_options(correct: str, pool_items: list[dict]) -> list[str]:
    correct_parts = [part.strip() for part in correct.split("-")]
    candidates = [item["progression"] for item in pool_items if item["progression"] != correct]
    close = [
        item
        for item in candidates
        if item.split("-")[0].strip() == correct_parts[0]
        or item.split("-")[-1].strip() == correct_parts[-1]
    ]
    pool = close + [item for item in candidates if item not in close]
    return shuffled_options(correct, pool)


@st.cache_data(show_spinner=False)
def create_audio(root: str, scale_name: str, progression: str, texture: str, instrument: str) -> bytes:
    return create_wav(
        root=root,
        scale_name=scale_name,
        progression_text=progression,
        chord_seconds=1.0,
        gap_seconds=0.07,
        texture=texture,
        instrument=instrument,
    )


def make_exercise(level_id: str) -> dict:
    level = LEVELS[level_id]
    item = random.choice(level["items"])
    root = random.choice(ROOTS)
    progression = item["progression"]
    bass = bass_label_from_progression(progression)
    return {
        "id": random.randint(100000, 999999),
        "level_id": level_id,
        "scale_name": level["scale_name"],
        "root": root,
        "progression": progression,
        "bass": bass,
        "question": "Welches Vier-Akkord-Muster hoerst du?",
        "correct": progression,
        "options": close_progression_options(progression, level["items"]),
        "explanation": f"{item['gesture']}. {item['tip']} Bass: {bass}.",
        "reveal": normalize_progression(progression),
    }


def new_exercise() -> None:
    st.session_state.exercise = make_exercise(st.session_state.active_level)
    st.session_state.answered = False
    st.session_state.feedback = None
    st.session_state.last_answer = None
    st.session_state.tried_answers = []
    st.session_state.show_soprano_bass = False


def submit_answer(answer: str) -> None:
    if st.session_state.answered or answer in st.session_state.tried_answers:
        return

    exercise = st.session_state.exercise
    st.session_state.last_answer = answer

    if answer == exercise["correct"]:
        st.session_state.answered = True
        st.session_state.feedback = {
            "kind": "success",
            "title": "Richtig.",
        }
        return

    st.session_state.tried_answers.append(answer)
    st.session_state.feedback = {
        "kind": "warning",
        "title": "Noch einmal versuchen.",
    }


st.set_page_config(
    page_title=APP_TITLE,
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": f"{APP_TITLE}: kurze Hoer-Missionen fuer den LMS-Kurs.",
    },
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 780px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        font-size: 2rem;
        margin-bottom: 0.15rem;
    }
    h2, h3 {
        letter-spacing: 0;
    }
    div[data-testid="stButton"] > button {
        min-height: 2.35rem;
        border-radius: 8px;
        font-size: 0.95rem;
        padding: 0.25rem 0.7rem;
        text-align: left;
    }
    div[data-testid="stDownloadButton"] > button {
        border-radius: 8px;
    }
    .skill-note {
        color: #4a5562;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }
    .small-note {
        color: #64717f;
        font-size: 0.86rem;
        margin-top: -0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_level" not in st.session_state:
    st.session_state.active_level = "level_1"
if "exercise" not in st.session_state:
    new_exercise()
elif "scale_name" not in st.session_state.exercise:
    new_exercise()
if "answered" not in st.session_state:
    st.session_state.answered = False
if "feedback" not in st.session_state:
    st.session_state.feedback = None
if "last_answer" not in st.session_state:
    st.session_state.last_answer = None
if "tried_answers" not in st.session_state:
    st.session_state.tried_answers = []
if "show_soprano_bass" not in st.session_state:
    st.session_state.show_soprano_bass = False

exercise = st.session_state.exercise

st.title(APP_TITLE)
st.caption("Vier-Akkord-Muster hoeren. Bass als jederzeit verfuegbare Strategie nutzen.")

level_ids = list(LEVELS.keys())
selected_level = st.radio(
    "Level",
    level_ids,
    index=level_ids.index(st.session_state.active_level),
    format_func=lambda level_id: LEVELS[level_id]["title"],
    horizontal=True,
)

if selected_level != st.session_state.active_level:
    st.session_state.active_level = selected_level
    new_exercise()
    st.rerun()

instrument = st.radio(
    "Instrument",
    INSTRUMENTS,
    index=INSTRUMENTS.index("Orgel"),
    horizontal=True,
)

st.markdown("### Höre zuerst das ganze Pattern")
st.markdown(
    "<div class='skill-note'>Versuche, den Gesamtverlauf zu erfassen. Wenn du unsicher bist, nutze darunter die Bass-Hilfen.</div>",
    unsafe_allow_html=True,
)
st.audio(
    create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "chords", instrument),
    format="audio/wav",
)

st.markdown("### Bass hervorgehoben")
st.audio(
    create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "guided", instrument),
    format="audio/wav",
)

if not st.session_state.show_soprano_bass:
    if st.button("Bass in hoher Lage abspielen", help="Optionale Hoerhilfe", use_container_width=False):
        st.session_state.show_soprano_bass = True
        st.rerun()
    st.markdown(
        "<div class='small-note'>Optionale Hilfe: gleicher Bassverlauf in Sopranlage.</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown("### Bass in Sopranlage")
    st.audio(
        create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "bass_soprano", instrument),
        format="audio/wav",
    )

st.subheader(exercise["question"])

for option in exercise["options"]:
    label = normalize_progression(option)
    if option in st.session_state.tried_answers:
        label = f"{label}  (schon versucht)"
    if st.session_state.last_answer == option and st.session_state.answered:
        label = f"{label}  (deine Antwort)"

    st.button(
        label,
        key=f"{exercise['id']}_{option}",
        disabled=st.session_state.answered or option in st.session_state.tried_answers,
        use_container_width=True,
        on_click=submit_answer,
        args=(option,),
    )

feedback = st.session_state.feedback
if feedback:
    if feedback["kind"] == "success":
        st.success(feedback["title"])
    else:
        st.warning(feedback["title"])

actions_left, actions_right = st.columns([1, 1])
with actions_left:
    if st.button("Naechste Mission", type="primary", use_container_width=True):
        new_exercise()
        st.rerun()
with actions_right:
    st.download_button(
        "MIDI",
        data=create_midi(
            root=exercise["root"],
            scale_name=exercise["scale_name"],
            progression_text=exercise["progression"],
            bpm=86,
            bars=4,
            pattern="Akkorde",
            program=MIDI_PROGRAMS[instrument],
        ),
        file_name="auralingo_mission.mid",
        mime="audio/midi",
        use_container_width=True,
    )
