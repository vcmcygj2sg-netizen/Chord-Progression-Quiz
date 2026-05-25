import base64
from io import BytesIO
import math
import random
import wave

import streamlit as st

from midi_engine import create_wav


APP_TITLE = "Auralingo"
ROOTS = ["C", "D", "E", "F", "G", "A", "Bb"]
INSTRUMENTS = ["Orgel", "E-Piano", "Synth"]
PRACTICE_MODES = {
    "cadences": "Kadenzmuster",
    "loops": "4-Chord-Loops",
}
TASK_TYPES = {
    "identify": "Hoeren und benennen",
    "choose_audio": "Passendes Audio waehlen",
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

LOOP_LEVELS = {
    "level_1": {
        "title": "Level 1: Dur",
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
        "title": "Level 2: Moll",
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

CADENCE_LEVELS = {
    "cadence_basic": {
        "title": "Grundkadenzen",
        "scale_name": "Dur",
        "items": [
            {"name": "Ganzschluss", "progression": "I - IV - V - I", "gesture": "subdominantischer Weg, Dominante, Rueckkehr"},
            {"name": "Halbschluss", "progression": "I - IV - I - V", "gesture": "Zuhause, Ausweichen, Zuhause, offener Dominantschluss"},
            {"name": "Trugschluss", "progression": "I - IV - V - VIm", "gesture": "Schlusszug, der nicht nach Hause aufloest"},
            {"name": "Plagalschluss", "progression": "I - V - IV - I", "gesture": "Dominante, Subdominante, weiche Rueckkehr"},
            {"name": "Ganzschluss", "progression": "VIm - IIm - V - I", "gesture": "fallende Quintbeziehungen bis zur Tonika"},
            {"name": "Plagalschluss", "progression": "I - IIm - IV - I", "gesture": "subdominantische Farbe ohne Dominantschluss"},
        ],
    },
    "cadence_minor": {
        "title": "Mollkadenzen",
        "scale_name": "Natuerlich Moll",
        "items": [
            {"name": "Ganzschluss", "progression": "Im - IVm - V - Im", "gesture": "Mollzentrum, Subdominante, Durdominante, Rueckkehr"},
            {"name": "Halbschluss", "progression": "Im - VI - IVm - V", "gesture": "dunkle Farbe, Subdominante, offener Dominantschluss"},
            {"name": "Trugschluss", "progression": "Im - IVm - V - VI", "gesture": "Dominantzug, der in die sechste Stufe ausweicht"},
            {"name": "Plagalschluss", "progression": "Im - Vm - IVm - Im", "gesture": "Molldominante, Subdominante, weiche Rueckkehr"},
            {"name": "Halbschluss", "progression": "Im - VII - VI - V", "gesture": "absteigende Mollfolge mit offenem Dominantschluss"},
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


def cadence_name_options(correct_name: str, pool_items: list[dict]) -> list[str]:
    return shuffled_options(correct_name, [item["name"] for item in pool_items])


def cadence_items() -> list[dict]:
    items = []
    for level in CADENCE_LEVELS.values():
        for item in level["items"]:
            items.append({**item, "scale_name": level["scale_name"]})
    return items


def reset_task_cycle() -> None:
    st.session_state.current_task_type = random.choice(list(TASK_TYPES.keys()))
    st.session_state.tasks_left_before_switch = random.randint(1, 3)


def next_task_type() -> str:
    if "current_task_type" not in st.session_state or "tasks_left_before_switch" not in st.session_state:
        reset_task_cycle()

    task_type = st.session_state.current_task_type
    st.session_state.tasks_left_before_switch -= 1

    if st.session_state.tasks_left_before_switch <= 0:
        st.session_state.current_task_type = "choose_audio" if task_type == "identify" else "identify"
        st.session_state.tasks_left_before_switch = random.randint(1, 3)

    return task_type


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


@st.cache_data(show_spinner=False)
def create_success_sound(sample_rate: int = 44100) -> bytes:
    frames = bytearray()
    notes = [(659.25, 0.10), (783.99, 0.12), (1046.50, 0.16)]

    for frequency, seconds in notes:
        samples = int(sample_rate * seconds)
        fade_samples = max(1, int(sample_rate * 0.018))
        for sample_index in range(samples):
            t = sample_index / sample_rate
            tone = (
                math.sin(2 * math.pi * frequency * t)
                + 0.35 * math.sin(2 * math.pi * frequency * 2 * t)
            ) / 1.35
            fade_in = min(1.0, sample_index / fade_samples)
            fade_out = min(1.0, (samples - sample_index) / fade_samples)
            envelope = min(fade_in, fade_out)
            scaled = int(max(-1.0, min(1.0, tone * envelope * 0.34)) * 32767)
            frames.extend(scaled.to_bytes(2, byteorder="little", signed=True))

    output = BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))

    return output.getvalue()


def render_success_sound() -> None:
    encoded = base64.b64encode(create_success_sound()).decode("ascii")
    st.markdown(
        f"""
        <audio class="success-sound" autoplay preload="auto">
            <source src="data:audio/wav;base64,{encoded}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True,
    )


def render_compact_audio(audio_bytes: bytes, audio_key: str) -> None:
    with st.container(key=f"compact_audio_{audio_key}"):
        st.audio(audio_bytes, format="audio/wav")


def make_audio_choices(correct_item: dict, distractor_item: dict) -> list[dict]:
    choices = [
        {
            "id": "audio_a",
            "label": "Soundfile A",
            "root": random.choice(ROOTS),
            "scale_name": correct_item["scale_name"],
            "progression": correct_item["progression"],
            "is_correct": True,
        },
        {
            "id": "audio_b",
            "label": "Soundfile B",
            "root": random.choice(ROOTS),
            "scale_name": distractor_item["scale_name"],
            "progression": distractor_item["progression"],
            "is_correct": False,
        },
    ]
    random.shuffle(choices)
    for index, choice in enumerate(choices):
        choice["id"] = f"audio_{index + 1}"
        choice["label"] = f"Soundfile {chr(65 + index)}"
    return choices


def make_loop_identify_exercise(level_id: str, task_type: str) -> dict:
    level = LOOP_LEVELS[level_id]
    item = random.choice(level["items"])
    root = random.choice(ROOTS)
    progression = item["progression"]
    bass = bass_label_from_progression(progression)
    return {
        "id": random.randint(100000, 999999),
        "mode": "loops",
        "mode_title": PRACTICE_MODES["loops"],
        "task_type": task_type,
        "task_title": TASK_TYPES[task_type],
        "level_id": level_id,
        "scale_name": level["scale_name"],
        "root": root,
        "progression": progression,
        "bass": bass,
        "question": "Welches Vier-Akkord-Muster hoerst du?",
        "correct": progression,
        "options": close_progression_options(progression, level["items"]),
        "answer_style": "progression",
        "explanation": f"{item['gesture']}. {item['tip']} Bass: {bass}.",
        "reveal": normalize_progression(progression),
    }


def make_loop_audio_choice_exercise(level_id: str, task_type: str) -> dict:
    level = LOOP_LEVELS[level_id]
    item = random.choice(level["items"])
    distractor = random.choice([
        candidate for candidate in level["items"]
        if candidate["progression"] != item["progression"]
    ])
    correct_item = {**item, "scale_name": level["scale_name"]}
    distractor_item = {**distractor, "scale_name": level["scale_name"]}
    choices = make_audio_choices(correct_item, distractor_item)
    correct_choice = next(choice for choice in choices if choice["is_correct"])
    progression = item["progression"]
    bass = bass_label_from_progression(progression)

    return {
        "id": random.randint(100000, 999999),
        "mode": "loops",
        "mode_title": PRACTICE_MODES["loops"],
        "task_type": task_type,
        "task_title": TASK_TYPES[task_type],
        "level_id": level_id,
        "scale_name": correct_choice["scale_name"],
        "root": correct_choice["root"],
        "progression": progression,
        "bass": bass,
        "question": "Welches Soundfile spielt dieses Vier-Akkord-Muster?",
        "target_label": normalize_progression(progression),
        "correct": correct_choice["id"],
        "audio_choices": choices,
        "answer_style": "audio",
        "explanation": f"{normalize_progression(progression)}. Bass: {bass}.",
        "reveal": normalize_progression(progression),
    }


def make_loop_exercise(level_id: str, task_type: str) -> dict:
    if task_type == "choose_audio":
        return make_loop_audio_choice_exercise(level_id, task_type)
    return make_loop_identify_exercise(level_id, task_type)


def make_cadence_identify_exercise(task_type: str) -> dict:
    items = cadence_items()
    item = random.choice(items)
    root = random.choice(ROOTS)
    progression = item["progression"]
    bass = bass_label_from_progression(progression)
    return {
        "id": random.randint(100000, 999999),
        "mode": "cadences",
        "mode_title": PRACTICE_MODES["cadences"],
        "task_type": task_type,
        "task_title": TASK_TYPES[task_type],
        "level_id": "cadences",
        "scale_name": item["scale_name"],
        "root": root,
        "progression": progression,
        "bass": bass,
        "question": "Welcher Kadenzverlauf ist zu hoeren?",
        "correct": item["name"],
        "options": cadence_name_options(item["name"], items),
        "answer_style": "name",
        "explanation": f"{item['name']}: {item['gesture']}. Bass: {bass}.",
        "reveal": item["name"],
    }


def make_cadence_audio_choice_exercise(task_type: str) -> dict:
    items = cadence_items()
    item = random.choice(items)
    distractor = random.choice([
        candidate for candidate in items
        if candidate["name"] != item["name"]
    ])
    choices = make_audio_choices(item, distractor)
    correct_choice = next(choice for choice in choices if choice["is_correct"])
    progression = item["progression"]
    bass = bass_label_from_progression(progression)

    return {
        "id": random.randint(100000, 999999),
        "mode": "cadences",
        "mode_title": PRACTICE_MODES["cadences"],
        "task_type": task_type,
        "task_title": TASK_TYPES[task_type],
        "level_id": "cadences",
        "scale_name": correct_choice["scale_name"],
        "root": correct_choice["root"],
        "progression": progression,
        "bass": bass,
        "question": "Welches Soundfile passt zu diesem Kadenzverlauf?",
        "target_label": item["name"],
        "correct": correct_choice["id"],
        "audio_choices": choices,
        "answer_style": "audio",
        "explanation": f"{item['name']}: {item['gesture']}. Bass: {bass}.",
        "reveal": item["name"],
    }


def make_cadence_exercise(task_type: str) -> dict:
    if task_type == "choose_audio":
        return make_cadence_audio_choice_exercise(task_type)
    return make_cadence_identify_exercise(task_type)


def make_exercise() -> dict:
    task_type = next_task_type()
    if st.session_state.active_mode == "cadences":
        return make_cadence_exercise(task_type)
    return make_loop_exercise(st.session_state.active_loop_level, task_type)


def new_exercise() -> None:
    exercise = make_exercise()
    exercise["instrument"] = random.choice(INSTRUMENTS)
    st.session_state.exercise = exercise
    st.session_state.answered = False
    st.session_state.feedback = None
    st.session_state.last_answer = None
    st.session_state.tried_answers = []
    st.session_state.show_soprano_bass = False
    st.session_state.play_success_sound = False


def submit_answer(answer: str) -> None:
    if st.session_state.answered or answer in st.session_state.tried_answers:
        return

    exercise = st.session_state.exercise
    st.session_state.last_answer = answer

    if answer == exercise["correct"]:
        st.session_state.answered = True
        st.session_state.score = st.session_state.get("score", 0) + 1
        st.session_state.feedback = {
            "kind": "success",
            "title": "Richtig.",
        }
        st.session_state.play_success_sound = True
        return

    st.session_state.tried_answers.append(answer)
    st.session_state.wrong_count = st.session_state.get("wrong_count", 0) + 1
    st.session_state.feedback = {
        "kind": "warning",
        "title": "Noch einmal versuchen.",
    }
    st.session_state.play_success_sound = False


def option_label(option: str, exercise: dict) -> str:
    if exercise["answer_style"] == "progression":
        return normalize_progression(option)
    return option


def render_audio_controls(exercise: dict, instrument: str) -> None:
    st.markdown("### Höre zuerst das ganze Pattern")
    st.markdown(
        "<div class='skill-note'>Versuche, den Gesamtverlauf zu erfassen. Wenn du unsicher bist, nutze darunter die Bass-Hilfen.</div>",
        unsafe_allow_html=True,
    )
    st.audio(
        create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "chords", instrument),
        format="audio/wav",
    )

    st.markdown("<div class='helper-title'>Bass hervorgehoben</div>", unsafe_allow_html=True)
    render_compact_audio(
        create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "guided", instrument),
        f"guided_{exercise['id']}",
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
        st.markdown("<div class='helper-title'>Bass in Sopranlage</div>", unsafe_allow_html=True)
        render_compact_audio(
            create_audio(exercise["root"], exercise["scale_name"], exercise["progression"], "bass_soprano", instrument),
            f"soprano_{exercise['id']}",
        )


def render_feedback() -> None:
    feedback = st.session_state.feedback
    if feedback:
        if feedback["kind"] == "success":
            st.success(feedback["title"])
            if st.session_state.get("play_success_sound"):
                render_success_sound()
                st.session_state.play_success_sound = False
        else:
            st.warning(feedback["title"])


def render_text_answers(exercise: dict) -> None:
    st.subheader(exercise["question"])

    for option in exercise["options"]:
        label = option_label(option, exercise)
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

    render_feedback()


def render_audio_choice_answers(exercise: dict, instrument: str) -> None:
    st.subheader(exercise["question"])
    st.markdown(f"<div class='target-pattern'>{exercise['target_label']}</div>", unsafe_allow_html=True)

    for choice in exercise["audio_choices"]:
        st.markdown(f"### {choice['label']}")
        st.audio(
            create_audio(choice["root"], choice["scale_name"], choice["progression"], "chords", instrument),
            format="audio/wav",
        )

        label = f"{choice['label']} waehlen"
        if choice["id"] in st.session_state.tried_answers:
            label = f"{label}  (schon versucht)"
        if st.session_state.last_answer == choice["id"] and st.session_state.answered:
            label = f"{label}  (deine Antwort)"

        st.button(
            label,
            key=f"{exercise['id']}_{choice['id']}",
            disabled=st.session_state.answered or choice["id"] in st.session_state.tried_answers,
            use_container_width=True,
            on_click=submit_answer,
            args=(choice["id"],),
        )

    render_feedback()


def correct_percentage() -> int:
    correct = st.session_state.get("score", 0)
    wrong = st.session_state.get("wrong_count", 0)
    total = correct + wrong
    if total == 0:
        return 0
    return round(correct / total * 100)


def render_scoreboard() -> None:
    correct = st.session_state.get("score", 0)
    wrong = st.session_state.get("wrong_count", 0)
    percentage = correct_percentage()
    st.markdown(
        f"""
        <div class="scoreboard">
            <div><span>Richtig</span><strong>{correct}</strong></div>
            <div><span>Falsch</span><strong>{wrong}</strong></div>
            <div><span>Trefferquote</span><strong>{percentage}%</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    .helper-title {
        color: #4a5562;
        font-size: 0.92rem;
        font-weight: 700;
        margin: 0.95rem 0 0.2rem 0;
    }
    div[class*="st-key-compact_audio"] {
        max-width: 420px;
        margin-bottom: 0.65rem;
    }
    div[class*="st-key-compact_audio"] audio {
        min-height: 32px;
    }
    .target-pattern {
        border-left: 4px solid #1f7a6d;
        color: #182026;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 0.35rem 0 1rem 0;
        padding: 0.35rem 0 0.35rem 0.75rem;
    }
    .scoreboard {
        border-top: 1px solid #d8dee5;
        display: grid;
        gap: 0.5rem;
        grid-template-columns: repeat(3, 1fr);
        margin-top: 1rem;
        padding-top: 0.8rem;
    }
    .scoreboard div {
        background: #f6f7f9;
        border-radius: 8px;
        padding: 0.55rem 0.65rem;
    }
    .scoreboard span {
        color: #64717f;
        display: block;
        font-size: 0.8rem;
        margin-bottom: 0.15rem;
    }
    .scoreboard strong {
        color: #1f7a6d;
        display: block;
        font-size: 1.15rem;
        line-height: 1.2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_mode" not in st.session_state:
    st.session_state.active_mode = "loops"
if "active_loop_level" not in st.session_state:
    st.session_state.active_loop_level = "level_1"
if "exercise" not in st.session_state:
    new_exercise()
elif (
    "mode" not in st.session_state.exercise
    or st.session_state.exercise["mode"] != st.session_state.active_mode
    or "scale_name" not in st.session_state.exercise
    or "task_type" not in st.session_state.exercise
    or "instrument" not in st.session_state.exercise
):
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
if "play_success_sound" not in st.session_state:
    st.session_state.play_success_sound = False
if "score" not in st.session_state:
    st.session_state.score = 0
if "wrong_count" not in st.session_state:
    st.session_state.wrong_count = 0

st.title(APP_TITLE)

mode_ids = list(PRACTICE_MODES.keys())
selected_mode = st.radio(
    "Auswahl der Übung",
    mode_ids,
    index=mode_ids.index(st.session_state.active_mode),
    format_func=lambda mode_id: PRACTICE_MODES[mode_id],
    horizontal=True,
)

if selected_mode != st.session_state.active_mode:
    st.session_state.active_mode = selected_mode
    new_exercise()
    st.rerun()

if st.session_state.active_mode == "loops":
    level_ids = list(LOOP_LEVELS.keys())
    selected_level = st.radio(
        "Level",
        level_ids,
        index=level_ids.index(st.session_state.active_loop_level),
        format_func=lambda level_id: LOOP_LEVELS[level_id]["title"],
        horizontal=True,
    )
    if selected_level != st.session_state.active_loop_level:
        st.session_state.active_loop_level = selected_level
        new_exercise()
        st.rerun()

exercise = st.session_state.exercise
instrument = exercise["instrument"]

if exercise["task_type"] == "choose_audio":
    render_audio_choice_answers(exercise, instrument)
else:
    render_audio_controls(exercise, instrument)
    render_text_answers(exercise)

if st.button("Nächste Aufgabe", type="primary", use_container_width=True):
    new_exercise()
    st.rerun()

render_scoreboard()
