import pyttsx3

# Initialisation du moteur vocal
moteur = pyttsx3.init()

# Paramètres de la voix
moteur.setProperty("rate", 80)    # Vitesse de parole
moteur.setProperty("volume", 0.4)  # Volume maximal

# Choisir une voix française si elle est disponible
for voix in moteur.getProperty("voices"):
    if "de" in voix.id.lower() or "german" in voix.name.lower():
        moteur.setProperty("voice", voix.id)
        break

# Faire parler le hibou
moteur.say("Bonjour")
moteur.say("Ich ben der fürher")
moteur.runAndWait()