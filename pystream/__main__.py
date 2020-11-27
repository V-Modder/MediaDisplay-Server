import threading
from . import pystream, webservice, gitupdater

def start_webserver():
	webservice.main()

def main():
	gitupdater.update()
	y = threading.Thread(target=start_webserver)
	y.start()
	pystream.main()