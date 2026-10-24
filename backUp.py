import json
import random
import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

import pyttsx3
import speech_recognition as sr


QUESTIONS_FILE = Path(__file__).resolve().parent / "data" / "questions.json"
MICROPHONE_DEVICE = "plughw:3,0"
RECORDING_DURATION = 5


def load_questions() -> list[dict[str, Any]]:
    with QUESTIONS_FILE.open(encoding="utf-8") as file:
        questions = json.load(file)

    if not isinstance(questions, list) or not questions:
        raise ValueError(f"Aucune question valide dans {QUESTIONS_FILE}")

    for index, question in enumerate(questions, start=1):
        if (
            not isinstance(question, dict)
            or not isinstance(question.get("english"), str)
            or not question["english"].strip()
            or not isinstance(question.get("french"), str)
            or not question["french"].strip()
        ):
            raise ValueError(f"Question invalide à la position {index}")

    return questions


def find_voice(engine: Any, language: str) -> str | None:
    if language == "fr":
        patterns = (re.compile(r"\bfrench\b", re.IGNORECASE), re.compile(r"(^|[^a-z])fr([_-]|$)", re.IGNORECASE))
    else:
        patterns = (re.compile(r"\benglish\b", re.IGNORECASE), re.compile(r"(^|[^a-z])en([_-]|$)", re.IGNORECASE))

    for voice in engine.getProperty("voices"):
        details = f"{voice.id} {voice.name}"
        if any(pattern.search(details) for pattern in patterns):
            return voice.id

    print(f"Avertissement : aucune voix {language} trouvée, la voix par défaut sera utilisée.")
    return None


def speak(text: str, language: str, engine: Any) -> None:
    voice_id = find_voice(engine, language)
    if voice_id is not None:
        engine.setProperty("voice", voice_id)
    engine.say(text)
    engine.runAndWait()


def record_answer(file_path: Path, language: str) -> str:
    print(f"Je t'écoute pendant {RECORDING_DURATION} secondes...")
    subprocess.run(
        [
            "arecord",
            "-D",
            MICROPHONE_DEVICE,
            "-f",
            "S16_LE",
            "-r",
            "16000",
            "-c",
            "1",
            "-d",
            str(RECORDING_DURATION),
            str(file_path),
        ],
        check=True,
    )

    recognizer = sr.Recognizer()
    with sr.AudioFile(str(file_path)) as source:
        audio = recognizer.record(source)

    return recognizer.recognize_google(audio, language=language)


def normalize_answer(text: str) -> str:
    normalized = unicodedata.normalize("NFC", text).casefold()
    normalized = "".join(
        character for character in normalized
        if not unicodedata.category(character).startswith("P")
    )
    return " ".join(normalized.split())


def main() -> None:
    question = random.choice(load_questions())
    ask_in_english = random.choice((True, False))

    if ask_in_english:
        prompt = question["english"]
        expected_answer = question["french"]
        prompt_language = "en"
        recognizer_language = "fr-FR"
    else:
        prompt = question["french"]
        expected_answer = question["english"]
        prompt_language = "fr"
        recognizer_language = "en-US"

    engine = pyttsx3.init()
    engine.setProperty("rate", 80)
    engine.setProperty("volume", 0.4)

    print(f"Traduis cette phrase ({'anglais' if prompt_language == 'en' else 'français'}) :")
    speak(prompt, prompt_language, engine)

    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_path = Path(temporary_directory)
        speak("Ding !", prompt_language, engine)

        try:
            answer = record_answer(temporary_path / "reponse.wav", recognizer_language)
        except sr.UnknownValueError:
            print("Je n'ai pas compris la réponse.")
            print("mauvais")
            print("Réponse attendue :", expected_answer)
            return
        except sr.RequestError as error:
            print("Erreur du service de reconnaissance vocale :", error)
            return

    print("Tu as dit :", answer)
    if normalize_answer(answer) == normalize_answer(expected_answer):
        print("ok")
    else:
        print("mauvais")
        print("Réponse attendue :", expected_answer)


if __name__ == "__main__":
    main()