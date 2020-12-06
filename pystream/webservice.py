import socket
import logging
from threading import Thread
from zeroconf import IPVersion, ServiceInfo, Zeroconf
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from pystream.utils import macDeviceName, localIp

clients = []
receivers = []
deviceName = macDeviceName()
deviceIP = localIp()
wsPort = 8765

def mDNSinit(type, name):
    deviceType = '_' + type
    desc = {'deviceName': name}
    address = [socket.inet_aton(deviceIP)]

    logging.info("[Server] Register Zeroconf server at %s:%s"%(deviceIP, port))
    info = ServiceInfo(type_= deviceType + "._tcp.local.",
                       name = deviceType + "._tcp.local.",
                       addresses = address, 
                       port = wsPort,
                       properties = desc,
                       server = name + ".local.")

    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    zeroconf.register_service(info)


class HandleServer(WebSocket):
    def handleMessage(self):
        sendDataToReceivers(self.data)

    def handleConnected(self):
        clients.append(self)

    def handleClose(self):
        clients.remove(self)
        sendDataToReceivers(None)

    def sendDataToReceivers(self, data):
        for receiver in receivers:
            receiver.receive(data)


class WebSocketServer(Thread):
    def __init__(self, receiver = None):
        Thread.__init__(self)
        self.name = deviceIP
        self.port = wsPort
        self.server = SimpleWebSocketServer(self.name, self.port, HandleServer)
        self._isClosed = False
        self.setDaemon(True)
        if receiver is not None:
            receivers.append(receiver)

    def start(self, name = deviceName):
        mDNSinit('mediadisplay', name)
        logging.info("[Server] starting tcp socket server")
        super(WebSocketServer, self).start()

    def run(self):
        self.server.serveforever()

    def stop(self):
        self.server.close()
        self._isClosed = True

    def broadcast(self, msg):
        if isinstance(msg, str):
            msg = msg.encode('utf-8').decode("utf-8")
        for client in clients:
            client.sendMessage(msg)
            while client.sendq:
                opcode, payload = client.sendq.popleft()
                remaining = client._sendBuffer(payload)
                if remaining is not None:
                    client.sendq.appendleft((opcode, remaining))
                    break

if __name__ == "__main__":
   server = WebSocketServer()
   server.start()