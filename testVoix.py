import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr

DUREE = 10
FS = 48000
FICHIER = "enregistrement.wav"
GAIN = 8
LANGUE = "fr-FR"   # "en-US" pour l'anglais

IN_DEV = "googlevoicehat"
OUT_DEV = "Headphones"

# --- Enregistrement ---
print("Enregistrement... parle maintenant !")
audio = sd.rec(int(DUREE * FS), samplerate=FS, channels=2, dtype="int32", device=IN_DEV)
sd.wait()
print("Terminé.")

gauche = audio[:, 0].astype(np.float64) / 2**31
mono16 = np.clip(gauche * GAIN, -1, 1)
mono16 = (mono16 * 32767).astype(np.int16)

with wave.open(FICHIER, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(FS)
    w.writeframes(mono16.tobytes())
print(f"Sauvegardé dans {FICHIER}")

# --- Lecture ---
print("Lecture...")
sd.play(np.column_stack((mono16, mono16)), FS, device=OUT_DEV)
sd.wait()

# --- Transcription ---
print("Transcription...")
r = sr.Recognizer()
with sr.AudioFile(FICHIER) as source:
    donnees = r.record(source)

try:
    texte = r.recognize_google(donnees, language=LANGUE)
    print("Texte reconnu :", texte)
except sr.UnknownValueError:
    print("Je n'ai rien compris (parle plus fort ou plus près du micro).")
except sr.RequestError as e:
    print("Erreur de connexion au service :", e)