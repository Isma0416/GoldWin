
from gpiozero import AngularServo
from threading import Thread
from time import sleep

gpio_moteur= 23   #le gpio du moteur

def lancer_moteur():
    servo = AngularServo(
        gpio_moteur,
        min_angle=0,
        max_angle=180,
        min_pulse_width=0.0005,
        max_pulse_width=0.0025
    )

    def mouvement():
        try:
            servo.angle = 10
            sleep(1)
            servo.angle = 90
            sleep(0.5)
            servo.angle = 10
            sleep(0.5)
            servo.angle = 90
            sleep(0.5)
            servo.angle = 10
            sleep(1)
            servo.angle = 90
            sleep(0.5)
            servo.angle = 180
            sleep(1)
        finally:
            servo.detach()
            servo.close()

    thread = Thread(target=mouvement)
    thread.start()
    return thread

#lancer_moteur()
