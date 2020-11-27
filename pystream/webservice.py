import asyncio
import json
import websockets

import pystream


class Webservice:
    __CONNECTIONS = set()


    def __add_connection(self, websocket):
        __CONNECTIONS.add(websocket)

    async def new_connection(self, websocket, path):
        try:
            add_connection(websocket)
            async for message in websocket:
                if message != "Stop":
                    pystream.pystream.window.update_gui(message)
        except:
            print("connection closed")
        finally:
            __CONNECTIONS.remove(websocket)
            if len(__CONNECTIONS) == 0:
                pystream.pystream.window.restore_gui()

    def send_message(message):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send(message)) 
    
    async def send(message):
        for connection in __CONNECTIONS:
            await connection.send(json.dumps(message))

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(new_connection, "localhost", 8765)

    loop.run_until_complete(start_server)
    loop.run_forever()