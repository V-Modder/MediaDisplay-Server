import threading
from . import pystream, webservice

def start_webserver():
	webservice.main()

if __name__ == '__main__':
	y = threading.Thread(target=start_webserver)
	y.start()
	pystream.main()