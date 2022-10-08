import RPI.GPIO as GPIO

class PySense:
    INPUT_1 = 24
    INPUT_2 = 23

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.INPUT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.INPUT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def check_state(self, input_pin):
        return GPIO.input(input_pin) == 0
