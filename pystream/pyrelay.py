import relay_ft245r

class PyRelay:
    RELAY_LAPTOP_PSU = 1
    RELAY_DESK_LAMP = 2
    RELAY_SWITCH_KVM = 3

    def __init__(self):
        self.__relay_board = relay_ft245r.FT245R()
        self.__connect()

    def __connect(self):
        dev_list = self.__relay_board.list_dev()

        if len(dev_list) == 0:
            print('No FT245R devices found')
            return

        self.__relay_board.connect(dev_list[0])
        self.__relay_board.switchoff(1)
        self.__relay_board.switchoff(2)
        self.__relay_board.switchoff(3)
        self.__relay_board.switchoff(4)
    
    def activate_relay(self, relay_number):
        if not self.__validate_input(relay_number):
            return
        
        if not self.__relay_board.is_connected:
            self.__connect()
        
        self.__relay_board.switchon(relay_number)

    def deactivate_relay(self, relay_number):
        if not self.__validate_input(relay_number):
            return

        if not self.__relay_board.is_connected:
            self.__connect()
        
        self.__relay_board.switchoff(relay_number)

    def __validate_input(self, input):
        return input >= 1 and input <= 4

if __name__ == "__main__":
   relay = PyRelay()
   relay.activate_relay(PyRelay.RELAY_LAPTOP_PSU)
