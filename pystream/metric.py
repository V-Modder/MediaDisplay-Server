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

class Metric(object):
    cpus: List[CPU]
    gpu: GPU
    memory_load: int
    network: Network
    time: str
    room_temperature: float

    def __init__(self, cpu: List[CPU] = None, gpu: GPU = None, memory_load: int = None, network: Network = None, time: str = None, room_temperature: float = None) -> None:
        self.cpus = cpu
        self.gpu = gpu
        self.memory_load = memory_load
        self.network = network
        self.time = time
        self.room_temperature = room_temperature

def parseMetric(jsonStr):
    simple_metric = json.loads(jsonStr, object_hook=lambda d: SimpleNamespace(**d))
    cpus = list()
    for simple_cpu in simple_metric.cpus:
        cpus.append(CPU(simple_cpu.load, simple_cpu.temperature))

    net = Network(simple_metric.network.up, simple_metric.network.down)
    gpu = GPU(simple_metric.gpu.load, simple_metric.gpu.memory_load, simple_metric.gpu.temperature)

    return Metric(cpus, gpu, simple_metric.memory_load, net, simple_metric.time, simple_metric.room_temperature)
