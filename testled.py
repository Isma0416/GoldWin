from gpiozero import RGBLED
from time import sleep
import pyttsx3
import random

led1 = RGBLED(red=16, green=21, blue=20)
led2 = RGBLED(red=14, green=18, blue=15)

# ---------- Voix ----------
moteur = pyttsx3.init()
moteur.setProperty("rate", 100)
moteur.setProperty("volume", 0.7)

for voix in moteur.getProperty("voices"):
    if "fr" in voix.id.lower() or "french" in voix.name.lower():
        moteur.setProperty("voice", voix.id)
        break

def dire(texte):
    moteur.say(texte)
    moteur.runAndWait()

# ---------- Couleurs ----------
def led_verte():
    led1.color = (0, 1, 0)
    led2.color = (0, 1, 0)

def led_rouge():
    led1.color = (1, 0, 0)
    led2.color = (1, 0, 0)

# ---------- Les phrases ----------
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

# ---------- Réactions ----------
def bonne_reponse():
    led_verte()
    dire(random.choice(phrases_correctes))

def mauvaise_reponse():
    led_rouge()
    dire(random.choice(phrases_incorrectes))


