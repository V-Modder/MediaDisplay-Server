import json
from typing import List
from types import SimpleNamespace


class Network(object):
    up: str
    down: str

    def __init__(self, up: str = None, down: str = None):
        self.up = up
        self.down = down

class CPU(object):
    load: int
    temperature: float

    def __init__(self, load: int = None, temperature: float = None) -> None:
        self.load = load
        self.temperature = temperature

class GPU(object):
    load: int
    memory_load: int
    temperature: float

    def __init__(self, load: int = None, memory_load: int = None, temperature: float = None) -> None:
        self.load = load
        self.memory_load = memory_load
        self.temperature = temperature

class PlaybackInfo(object):
    title: str
    artist: str
    status: int
    is_status_only: bool
    image: str

    def __init__(self, title: str = None, artist: str = None, status: int = None, is_status_only: bool = None, image: str = None) -> None:
        self.title = title
        self.artist = artist
        self.status = status
        self.is_status_only = is_status_only
        self.image = image

class Metric(object):
    reset: bool
    cpus: List[CPU]
    gpu: GPU
    memory_load: int
    network: Network
    time: str
    playback_info: PlaybackInfo
    display_brightness: int

    def __init__(self, reset: bool = None, cpu: List[CPU] = None, gpu: GPU = None, memory_load: int = None, network: Network = None, time: str = None, playback_info: PlaybackInfo = None, display_brightness: int = None, send_display_brightness: bool = None) -> None:
        self.reset = reset
        self.cpus = cpu
        self.gpu = gpu
        self.memory_load = memory_load
        self.network = network
        self.time = time
        self.playback_info = playback_info
        self.display_brightness = display_brightness
        self.send_display_brightness = send_display_brightness

def parseMetric(jsonStr):
    simple_metric = json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))
    cpus = list()
    for simple_cpu in simple_metric.cpus:
        cpus.append(CPU(simple_cpu.load, simple_cpu.temperature))

    net = Network(simple_metric.network.up, simple_metric.network.down)
    gpu = GPU(simple_metric.gpu.load, simple_metric.gpu.memory_load, simple_metric.gpu.temperature)
    if simple_metric.playback_info is not None:
        playback = PlaybackInfo(simple_metric.playback_info.title, simple_metric.playback_info.artist, simple_metric.playback_info.status, simple_metric.playback_info.is_status_only, simple_metric.playback_info.image)
    else:
        playback = None

    return Metric(cpu = cpus, gpu = gpu, memory_load = simple_metric.memory_load, network = net, time = simple_metric.time, playback_info = playback, display_brightness = simple_metric.display_brightness, send_display_brightness = simple_metric.send_display_brightness)
