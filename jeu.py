#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GoldWin - jeu complet (NOUVEAU fichier : ne modifie aucun de vos codes)
# Reutilise votre moteur.py et vos broches.

import os, json, random, subprocess, unicodedata
from difflib import SequenceMatcher
from threading import Thread, Event
from time import sleep
from signal import pause

from gpiozero import RGBLED, MotionSensor, Button
import pyttsx3
import speech_recognition as sr

from moteur import lancer_moteur   # <-- on reutilise votre moteur.py (servo GPIO 23)

# ==================== REGLAGES (a modifier facilement) ====================
NB_QUESTIONS = 5            # questions par partie : 5 pour les tests, 10 pour le final
SEUIL        = 0.6          # tolerance de la reponse : 0.5 = souple, 0.8 = strict
MICRO        = "plughw:3,0" # carte du micro (verifier avec : arecord -l)
DUREE_ECOUTE = 5            # secondes d'ecoute par reponse
PIN_START    = 17           # bouton Demarrer
PIN_STOP     = 22           # bouton Stop
# ==========================================================================

# ---------- Broches (vos pins) ----------
led1 = RGBLED(red=16, green=21, blue=20)   # oeil 1
led2 = RGBLED(red=14, green=18, blue=15)   # oeil 2
pir  = MotionSensor(27)                    # capteur de presence
bouton_start = Button(PIN_START, bounce_time=0.1)
bouton_stop  = Button(PIN_STOP,  bounce_time=0.1)

# ---------- Fichiers ----------
DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_QUESTIONS = os.path.join(DOSSIER, "data", "questions.json")
FICHIER_AUDIO = "/tmp/reponse.wav"

# ---------- Voix (francais + anglais) ----------
moteur_voix = pyttsx3.init()
moteur_voix.setProperty("rate", 150)
moteur_voix.setProperty("volume", 1.0)

def parler(texte, langue="fr"):
    # langue = "fr" ou "en"
    moteur_voix.setProperty("voice", langue)
    print(f"[{langue}] {texte}")
    moteur_voix.say(texte)
    moteur_voix.runAndWait()

def dire(texte):
    parler(texte, "fr")

# ---------- Yeux ----------
def yeux_bleu():
    led1.color = (0, 0, 1); led2.color = (0, 0, 1)
def yeux_vert():
    led1.color = (0, 1, 0); led2.color = (0, 1, 0)
def yeux_rouge():
    led1.color = (1, 0, 0); led2.color = (1, 0, 0)

# ---------- Phrases ----------
phrases_correctes = [
    "Bravo, finalement t'es pas une si grosse merde que ça.",
    "Correct ! Comme quoi, les miracles existent.",
    "Bien joué, pour une fois.",
    "Exact ! Tu me surprends, là.",
    "Parfait, continue comme ça, petit génie.",
    "Oui ! Alors t'as quand même un cerveau.",
    "Excellent, je retire ce que j'ai dit.",
    "Bonne réponse, respect.",
    "Nickel, t'assures finalement.",
    "C'est ça ! Tu montes dans mon estime.",
]
phrases_incorrectes = [
    "Mais t'es sérieux là ? C'est une catastrophe.",
    "Alors ça, c'est d'une nullité rare.",
    "Non mais quelle grosse merde, recommence.",
    "Faux, et pas qu'un peu, espèce de bouffon.",
    "Va te faire foutre avec des réponses pareilles.",
    "Même un hamster aurait trouvé, bravo le génie.",
    "T'es vraiment pas doué, faut réviser.",
    "Encore faux ? T'as un cerveau ou pas ?",
    "C'est une honte, j'ai mal pour toi.",
    "Lamentable. Vraiment lamentable.",
]

def bonne_reponse():
    yeux_vert()
    parler(random.choice(phrases_correctes), "fr")

def mauvaise_reponse():
    yeux_rouge()
    parler(random.choice(phrases_incorrectes), "fr")

# ---------- Micro -> texte ----------
def ecouter(langue="fr-FR"):
    try:
        subprocess.run(
            ["arecord", "-D", MICRO, "-f", "S16_LE", "-r", "16000",
             "-c", "1", "-d", str(DUREE_ECOUTE), FICHIER_AUDIO],
            check=True)
    except subprocess.CalledProcessError:
        print("Erreur micro (verifie la carte avec : arecord -l)")
        return ""
    r = sr.Recognizer()
    with sr.AudioFile(FICHIER_AUDIO) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language=langue)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Erreur du service de reconnaissance :", e)
        return ""

# ---------- Comparaison des reponses ----------
def normaliser(t):
    t = unicodedata.normalize("NFD", t.strip().lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    for p in "?.!,;:":
        t = t.replace(p, " ")
    return " ".join(t.split())

def reponse_correcte(entendu, attendue):
    e = normaliser(entendu)
    a = normaliser(attendue)
    if not e:
        return False
    if a in e or e in a:
        return True
    return SequenceMatcher(None, e, a).ratio() >= SEUIL

def charger_questions():
    with open(FICHIER_QUESTIONS, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("questions", data) if isinstance(data, dict) else data

# ---------- Etat du jeu ----------
jeu_actif = False
arret = Event()
pir_occupe = False

# ---------- Capteur PIR (seulement HORS jeu) ----------
def presence_detectee():
    global pir_occupe
    if jeu_actif or pir_occupe:
        return
    pir_occupe = True
    th = lancer_moteur()   # votre moteur.py fait bouger la tete (dans un thread)
    parler("C'est l'heure de faire ta leçon, espèce de gros con.", "fr")
    th.join()
    pir_occupe = False

pir.when_motion = presence_detectee

# ---------- Le jeu (tourne dans un thread, le bouton Stop peut l'arreter) ----------
def jouer():
    global jeu_actif
    toutes = charger_questions()
    n = min(NB_QUESTIONS, len(toutes))
    questions = random.sample(toutes, n)   # n questions tirees au hasard, sans doublon

    yeux_vert()
    dire("Le jeu commence. Écoute bien.")

    for q in questions:
        if arret.is_set():
            break
        yeux_vert()

        if random.choice([True, False]):
            # Il parle ANGLAIS -> tu reponds en FRANCAIS
            parler("Traduis en français.", "fr")
            parler(q["english"], "en")
            entendu = ecouter("fr-FR")
            attendue = q["french"]
        else:
            # Il parle FRANCAIS -> tu reponds en ANGLAIS
            parler("Translate into English.", "en")
            parler(q["french"], "fr")
            entendu = ecouter("en-US")
            attendue = q["english"]

        if arret.is_set():
            break

        print("Tu as dit :", entendu, "| attendu :", attendue)
        if reponse_correcte(entendu, attendue):
            bonne_reponse()
        else:
            mauvaise_reponse()
        sleep(1)

    if not arret.is_set():
        dire("C'est terminé. À la prochaine.")
    jeu_actif = False
    yeux_bleu()

# ---------- Boutons ----------
def demarrer():
    global jeu_actif
    if jeu_actif:
        return
    jeu_actif = True
    arret.clear()
    Thread(target=jouer, daemon=True).start()

def arreter():
    global jeu_actif
    if not jeu_actif:
        return
    arret.set()
    jeu_actif = False
    yeux_bleu()
    dire("Jeu arrêté.")

bouton_start.when_pressed = demarrer
bouton_stop.when_pressed  = arreter

# ---------- Demarrage ----------
if __name__ == "__main__":
    yeux_bleu()
    print("GoldWin prêt. Bouton Start = démarrer, bouton Stop = arrêter.")
    pause()   # garde le programme en vie, en attente des evenements
