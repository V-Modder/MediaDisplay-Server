import uuid
from netifaces import interfaces, ifaddresses, AF_INET

def local_ips():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface).get(AF_INET, ()):
            if link['addr'] != '127.0.0.1':
                ip_list.append(link['addr'])

    return ip_list

def localIp():
    ip_list = []
    for interface in interfaces():
        for link in ifaddresses(interface).get(AF_INET, ()):
            if link['addr'] != '127.0.0.1':
                ip_list.append(link['addr'])

    return ip_list[0]

def macDeviceName():
    return (''.join(['{:02X}'.format((uuid.getnode() >> ele) & 0xff)
        for ele in range(0,8*6,8)][::-1]))