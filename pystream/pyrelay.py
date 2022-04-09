import RPi.GPIO as GPIO

class PyRelay:
    SMALL_1 = 19
    SMALL_2 = 26
    BIG_1 = 6
    BIG_2 = 13

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SMALL_1, GPIO.OUT)
        GPIO.setup(self.SMALL_2, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.BIG_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.BIG_2, GPIO.OUT, initial=GPIO.LOW)

    def activate_relay(self, relay_number):
         if self.__validate_input(relay_number):
            state = GPIO.HIGH
            if relay_number in [self.SMALL_1, self.SMALL_2]:
                state = GPIO.LOW
            GPIO.output(relay_number, state)

    def deactivate_relay(self, relay_number):
        if self.__validate_input(relay_number):
            state = GPIO.LOW
            if relay_number in [self.SMALL_1, self.SMALL_2]:
                state = GPIO.HIGH
            GPIO.output(relay_number, state)
    
    def toggle_relay(self, relay_number):
        if not self.__validate_input(relay_number):
            return

        GPIO.output(relay_number, not GPIO.input(relay_number))

    def __validate_input(self, input):
        return input in [self.SMALL_1, self.SMALL_2, self.BIG_1, self.BIG_2]
