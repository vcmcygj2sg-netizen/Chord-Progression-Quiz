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


def scale_notes(root: str, scale_name: str, octave: int = 4) -> list[int]:
    root_midi = 12 * (octave + 1) + NOTE_OFFSETS[root]
    return [root_midi + step for step in SCALES[scale_name]]


def parse_progression(text: str) -> list[str]:
    cleaned = text.replace("-", " ").replace(",", " ")
    symbols = [part.strip().upper() for part in cleaned.split() if part.strip()]
    valid = []
    for symbol in symbols:
        core = symbol.removesuffix("M").removesuffix("MIN")
        if core in ROMAN_DEGREES:
            valid.append(symbol)
    return valid or ["I", "V", "VI", "IV"]


def chord_from_degree(notes: list[int], roman: str) -> list[int]:
    core = roman.removesuffix("M").removesuffix("MIN")
    degree = ROMAN_DEGREES[core]
    triad_degrees = [degree, degree + 2, degree + 4]

    chord = []
    for item in triad_degrees:
        octave_shift = item // len(notes)
        note_index = item % len(notes)
        chord.append(notes[note_index] + 12 * octave_shift)

    if "M" in roman and "MIN" not in roman:
        chord[1] = chord[0] + 4
    elif "MIN" in roman:
        chord[1] = chord[0] + 3

    return chord


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


def create_midi(
    root: str,
    scale_name: str,
    progression_text: str,
    bpm: int,
    bars: int,
    pattern: str,
) -> bytes:
    notes = scale_notes(root, scale_name)
    progression = parse_progression(progression_text)

    midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    midi.tracks.append(track)

    track.append(MetaMessage("track_name", name="Theory Sketch", time=0))
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))
    track.append(Message("program_change", program=0, time=0))

    bar_ticks = TICKS_PER_BEAT * 4
    beat_ticks = TICKS_PER_BEAT

    for bar_index in range(bars):
        roman = progression[bar_index % len(progression)]
        chord = chord_from_degree(notes, roman)

        if pattern == "Akkorde":
            add_block_chord(track, chord, velocity=72, duration=bar_ticks)
        elif pattern == "Arpeggio":
            add_arpeggio(track, chord, velocity=76, beat_ticks=beat_ticks)
        else:
            melody = [chord[0], chord[1], chord[2], notes[(ROMAN_DEGREES[roman.removesuffix("M").removesuffix("MIN")] + 6) % 7] + 12]
            for note in melody:
                add_note(track, note, velocity=82, duration=beat_ticks)

    track.append(MetaMessage("end_of_track", time=0))

    output = BytesIO()
    midi.save(file=output)
    return output.getvalue()


def midi_note_to_frequency(note: int) -> float:
    return 440.0 * (2 ** ((note - 69) / 12))


def create_wav(
    root: str,
    scale_name: str,
    progression_text: str,
    chord_seconds: float = 1.15,
    gap_seconds: float = 0.08,
    sample_rate: int = 44100,
) -> bytes:
    chords = progression_chords(root, scale_name, progression_text)
    chord_samples = int(chord_seconds * sample_rate)
    gap_samples = int(gap_seconds * sample_rate)
    fade_samples = max(1, int(0.03 * sample_rate))
    frames = bytearray()

    for chord in chords:
        frequencies = [midi_note_to_frequency(note - 12) for note in chord]
        for sample_index in range(chord_samples):
            t = sample_index / sample_rate
            value = sum(math.sin(2 * math.pi * frequency * t) for frequency in frequencies)
            value = value / len(frequencies)

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
