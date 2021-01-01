
class Action:
    Click = 1
    Brightness = 2

class Command:
    Next = "key_next"
    PlayPause = "key_play_pause"
    Previous = "key_previous"
    Stop = "key_stop"
    VolumeDown = "key_volume_down"
    VolumeUp = "key_volume_up"

class EventMessage:
    action: int
    command: str

    def __init__(self, action: int, command: str):
        self.action = action
        self.command = command