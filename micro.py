
import subprocess
import speech_recognition as sr

FICHIER_AUDIO = "/tmp/enregistrement.wav"
DUREE = 5

def enregistrer_audio():
    print("Je t'écoute pendant 5 secondes...")

    commande = [
        "arecord",
        "-D", "plughw:3,0",
        "-f", "S16_LE",
        "-r", "16000",
        "-c", "1",
        "-d", str(DUREE),
        FICHIER_AUDIO
    ]

    subprocess.run(commande, check=True)
    print("Enregistrement terminé !")

def convertir_en_texte():
    recognizer = sr.Recognizer()

    with sr.AudioFile(FICHIER_AUDIO) as source:
        audio = recognizer.record(source)

    try:
        texte = recognizer.recognize_google(
            audio,
            language="fr-FR"
        )
        print("Tu as dit :", texte)

    except sr.UnknownValueError:
        print("Je n'ai pas compris ce que tu as dit.")

    except sr.RequestError as erreur:
        print("Erreur du service de reconnaissance :", erreur)

if __name__ == "__main__":
    try:
        enregistrer_audio()
        convertir_en_texte()

    except subprocess.CalledProcessError:
        print("Erreur pendant l'enregistrement.")
        print("Vérifie la configuration du microphone I2S.")
