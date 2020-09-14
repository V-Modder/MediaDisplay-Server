
class InputBuffer:
    def __init__(self):
        self.__action = {}

    def set_action(self, action, x, y):
        self.__action = {"action": action, "x": x, "y": y}
    
    def has_action(self):
        return self.__action

    def pop_action(self):
        action = self.__action
        self.__action = {}
        return action
