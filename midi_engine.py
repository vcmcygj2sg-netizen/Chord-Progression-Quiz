from __future__ import annotations

from io import BytesIO
import math
import wave
from typing import Iterable

from mido import Message, MetaMessage, MidiFile, MidiTrack, bpm2tempo


TICKS_PER_BEAT = 480

NOTE_OFFSETS = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

SCALES = {
    "Dur": [0, 2, 4, 5, 7, 9, 11],
    "Natuerlich Moll": [0, 2, 3, 5, 7, 8, 10],
    "Dorian": [0, 2, 3, 5, 7, 9, 10],
    "Phrygisch": [0, 1, 3, 5, 7, 8, 10],
    "Lydisch": [0, 2, 4, 6, 7, 9, 11],
    "Mixolydisch": [0, 2, 4, 5, 7, 9, 10],
}

ROMAN_DEGREES = {
    "I": 0,
    "II": 1,
    "III": 2,
    "IV": 3,
    "V": 4,
    "VI": 5,
    "VII": 6,
}


def normalize_roman(symbol: str) -> tuple[int, str, bool]:
    stripped = symbol.strip()
    is_minor = stripped.endswith("m") or stripped.endswith("min")
    without_quality = stripped.removesuffix("min").removesuffix("m")
    accidental = 0

    if without_quality.startswith("b"):
        accidental = -1
        without_quality = without_quality[1:]
    elif without_quality.startswith("#"):
        accidental = 1
        without_quality = without_quality[1:]

    return accidental, without_quality.upper(), is_minor


def scale_notes(root: str, scale_name: str, octave: int = 4) -> list[int]:
    root_midi = 12 * (octave + 1) + NOTE_OFFSETS[root]
    return [root_midi + step for step in SCALES[scale_name]]


def parse_progression(text: str) -> list[str]:
    cleaned = text.replace("-", " ").replace(",", " ")
    symbols = [part.strip() for part in cleaned.split() if part.strip()]
    valid = []
    for symbol in symbols:
        accidental, core, is_minor = normalize_roman(symbol)
        if core in ROMAN_DEGREES:
            prefix = "b" if accidental < 0 else "#" if accidental > 0 else ""
            valid.append(f"{prefix}{core}m" if is_minor else f"{prefix}{core}")
    return valid or ["I", "V", "VIm", "IV"]


def chord_from_degree(notes: list[int], roman: str) -> list[int]:
    accidental, core, is_minor = normalize_roman(roman)
    degree = ROMAN_DEGREES[core]
    root = notes[degree] + accidental

    if is_minor:
        return [root, root + 3, root + 7]

    return [root, root + 4, root + 7]


def add_note(track: MidiTrack, note: int, velocity: int, duration: int, delay: int = 0) -> None:
    track.append(Message("note_on", note=note, velocity=velocity, time=delay))
    track.append(Message("note_off", note=note, velocity=0, time=duration))


def add_block_chord(track: MidiTrack, notes: Iterable[int], velocity: int, duration: int) -> None:
    notes = list(notes)
    for index, note in enumerate(notes):
        track.append(Message("note_on", note=note, velocity=velocity, time=0 if index else 0))
    for index, note in enumerate(notes):
        track.append(Message("note_off", note=note, velocity=0, time=duration if index == 0 else 0))


def add_arpeggio(track: MidiTrack, notes: list[int], velocity: int, beat_ticks: int) -> None:
    pattern = [notes[0], notes[1], notes[2], notes[1]]
    for note in pattern:
        add_note(track, note, velocity, beat_ticks)


def progression_chords(root: str, scale_name: str, progression_text: str) -> list[list[int]]:
    notes = scale_notes(root, scale_name)
    return [chord_from_degree(notes, roman) for roman in parse_progression(progression_text)]


def is_tonic_symbol(roman: str) -> bool:
    accidental, core, _ = normalize_roman(roman)
    return accidental == 0 and core == "I"


def bass_candidates(note: int, base_shift: int = -24) -> list[int]:
    return sorted({note + base_shift + 12 * octave_shift for octave_shift in range(-5, 6)})


def bass_register_cost(note: int, low: int = 28, high: int = 52) -> float:
    if note < low:
        range_penalty = (low - note) * 8
    elif note > high:
        range_penalty = (note - high) * 8
    else:
        range_penalty = 0

    return range_penalty + abs(note - 42) * 0.08


# Searches a playable bass path that keeps all jumps within a fifth and can pin
# repeated tonic bass notes to the same register.
def choose_bass_path(
    chords: list[list[int]],
    romans: list[str] | None,
    tonic_anchor: int | None = None,
    max_jump: int = 7,
    base_shift: int = -24,
) -> tuple[list[int], float] | None:
    if not chords:
        return [], 0.0

    candidate_sets = []
    for index, chord in enumerate(chords):
        candidates = bass_candidates(chord[0], base_shift)
        if romans and tonic_anchor is not None and is_tonic_symbol(romans[index]):
            candidates = [tonic_anchor]
        candidate_sets.append(candidates)

    states: dict[int, tuple[float, list[int]]] = {
        candidate: (bass_register_cost(candidate), [candidate])
        for candidate in candidate_sets[0]
    }

    for candidates in candidate_sets[1:]:
        next_states: dict[int, tuple[float, list[int]]] = {}
        for candidate in candidates:
            best: tuple[float, list[int]] | None = None
            for previous, (cost, path) in states.items():
                jump = abs(candidate - previous)
                if jump > max_jump:
                    continue
                next_cost = cost + bass_register_cost(candidate) + jump * 0.05
                next_path = path + [candidate]
                if best is None or next_cost < best[0]:
                    best = (next_cost, next_path)
            if best is not None:
                next_states[candidate] = best

        if not next_states:
            return None
        states = next_states

    cost, path = min(states.values(), key=lambda item: item[0])
    return path, cost


def closest_octave(note: int, previous: int, low: int = 28, high: int = 52) -> int:
    candidates = bass_candidates(note, base_shift=0)
    within_fifth = [candidate for candidate in candidates if abs(candidate - previous) <= 7]
    if within_fifth:
        candidates = within_fifth
    in_range = [candidate for candidate in candidates if low <= candidate <= high]
    if in_range:
        candidates = in_range
    return min(candidates, key=lambda candidate: (abs(candidate - previous), abs(candidate - 42)))


def fit_bass_register(note: int, low: int = 28, high: int = 52) -> int:
    candidates = bass_candidates(note, base_shift=0)
    in_range = [candidate for candidate in candidates if low <= candidate <= high]
    if in_range:
        candidates = in_range
    return min(candidates, key=lambda candidate: abs(candidate - 42))


def smooth_bass_line(
    chords: list[list[int]],
    romans: list[str] | None = None,
    base_shift: int = -24,
) -> list[int]:
    if romans:
        tonic_indices = [
            index for index, roman in enumerate(romans)
            if is_tonic_symbol(roman)
        ]
    else:
        tonic_indices = []

    if len(tonic_indices) >= 2:
        first_tonic = tonic_indices[0]
        anchor_candidates = bass_candidates(chords[first_tonic][0], base_shift)
        paths = [
            choose_bass_path(chords, romans, tonic_anchor=anchor, base_shift=base_shift)
            for anchor in anchor_candidates
        ]
        valid_paths = [path for path in paths if path is not None]
        if valid_paths:
            return min(valid_paths, key=lambda item: item[1])[0]

    path = choose_bass_path(chords, romans, base_shift=base_shift)
    if path is not None:
        return path[0]

    bass_notes = []
    for chord in chords:
        bass_note = chord[0] + base_shift
        if bass_notes:
            bass_note = closest_octave(bass_note, bass_notes[-1])
        else:
            bass_note = fit_bass_register(bass_note)
        bass_notes.append(bass_note)

    return bass_notes


def create_midi(
    root: str,
    scale_name: str,
    progression_text: str,
    bpm: int,
    bars: int,
    pattern: str,
    program: int = 0,
) -> bytes:
    notes = scale_notes(root, scale_name)
    progression = parse_progression(progression_text)

    midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    midi.tracks.append(track)

    track.append(MetaMessage("track_name", name="Theory Sketch", time=0))
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
    track.append(Message("program_change", program=program, time=0))

    bar_ticks = TICKS_PER_BEAT * 4
    beat_ticks = TICKS_PER_BEAT

    bar_chords = [
        chord_from_degree(notes, progression[bar_index % len(progression)])
        for bar_index in range(bars)
    ]
    bar_romans = [
        progression[bar_index % len(progression)]
        for bar_index in range(bars)
    ]
    bass_line = smooth_bass_line(bar_chords, bar_romans)

    for bar_index in range(bars):
        progression_index = bar_index % len(progression)
        roman = progression[progression_index]
        chord = bar_chords[bar_index]
        bass_note = bass_line[bar_index]

        if pattern == "Akkorde":
            add_block_chord(track, [bass_note] + chord, velocity=72, duration=bar_ticks)
        elif pattern == "Arpeggio":
            add_arpeggio(track, chord, velocity=76, beat_ticks=beat_ticks)
        else:
            _, core, _ = normalize_roman(roman)
            melody = [chord[0], chord[1], chord[2], notes[(ROMAN_DEGREES[core] + 6) % 7] + 12]
            for note in melody:
                add_note(track, note, velocity=82, duration=beat_ticks)

    track.append(MetaMessage("end_of_track", time=0))

    output = BytesIO()
    midi.save(file=output)
    return output.getvalue()


def midi_note_to_frequency(note: int) -> float:
    return 440.0 * (2 ** ((note - 69) / 12))


def instrument_wave(frequency: float, t: float, instrument: str) -> float:
    if instrument == "E-Piano":
        shimmer = 1 + 0.04 * math.sin(2 * math.pi * 5.0 * t)
        return (
            math.sin(2 * math.pi * frequency * t)
            + 0.22 * math.sin(2 * math.pi * frequency * 2 * t)
            + 0.12 * math.sin(2 * math.pi * frequency * 4 * t)
        ) * shimmer / 1.34

    if instrument == "Synth":
        detune = 1.006
        return (
            math.sin(2 * math.pi * frequency * t)
            + 0.72 * math.sin(2 * math.pi * frequency * detune * t)
            + 0.18 * math.sin(2 * math.pi * frequency * 2 * t)
        ) / 1.9

    return (
        math.sin(2 * math.pi * frequency * t)
        + 0.18 * math.sin(2 * math.pi * frequency * 2 * t)
        + 0.08 * math.sin(2 * math.pi * frequency * 3 * t)
    ) / 1.26


def instrument_envelope(t: float, duration: float, instrument: str) -> float:
    if instrument == "E-Piano":
        return 0.28 + 0.72 * math.exp(-1.8 * t / duration)

    if instrument == "Synth":
        attack = min(1.0, t / 0.06)
        release_like_decay = 0.74 + 0.26 * math.exp(-0.8 * t / duration)
        return attack * release_like_decay

    return 1.0


def chord_tones_for_texture(chord: list[int], bass_note: int, texture: str) -> list[tuple[int, float]]:
    if texture == "bass":
        return [(bass_note, 1.0)]

    if texture == "bass_soprano":
        return [(bass_note + 36, 1.0)]

    if texture == "guided":
        return [(bass_note, 1.15)] + [(note - 12, 0.07) for note in chord]

    if texture == "bright":
        return [(note, 0.32) for note in chord]

    return [(bass_note, 0.22)] + [(note - 12, 0.28) for note in chord]


def create_wav(
    root: str,
    scale_name: str,
    progression_text: str,
    chord_seconds: float = 1.15,
    gap_seconds: float = 0.08,
    sample_rate: int = 44100,
    texture: str = "chords",
    instrument: str = "Orgel",
) -> bytes:
    progression = parse_progression(progression_text)
    notes = scale_notes(root, scale_name)
    chords = [chord_from_degree(notes, roman) for roman in progression]
    chord_samples = int(chord_seconds * sample_rate)
    gap_samples = int(gap_seconds * sample_rate)
    fade_samples = max(1, int(0.03 * sample_rate))
    frames = bytearray()
    bass_line = smooth_bass_line(chords, progression)

    for chord, bass_note in zip(chords, bass_line):
        tones = chord_tones_for_texture(chord, bass_note, texture)
        weight_total = sum(weight for _, weight in tones)
        frequencies = [
            (midi_note_to_frequency(note), weight / weight_total)
            for note, weight in tones
        ]
        for sample_index in range(chord_samples):
            t = sample_index / sample_rate
            duration = chord_samples / sample_rate
            value = sum(
                instrument_wave(frequency, t, instrument) * weight
                for frequency, weight in frequencies
            )
            value *= instrument_envelope(t, duration, instrument)

            fade_in = min(1.0, sample_index / fade_samples)
            fade_out = min(1.0, (chord_samples - sample_index) / fade_samples)
            envelope = min(fade_in, fade_out)
            scaled = int(max(-1.0, min(1.0, value * envelope * 0.32)) * 32767)
            frames.extend(scaled.to_bytes(2, byteorder="little", signed=True))

        frames.extend((0).to_bytes(2, byteorder="little", signed=True) * gap_samples)

    output = BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(bytes(frames))

    return output.getvalue()
