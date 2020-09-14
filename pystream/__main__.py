import threading
from . import pystream, webservice

def start_webserver():
	webservice.main()

def main():
	y = threading.Thread(target=start_webserver)
	y.start()
	pystream.main()