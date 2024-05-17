import asyncio
import time

import websocket
import ssl
import threading
import json
import traceback

class RC_Client():
    __thread = None
    __host = None
    __port = None

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.actions = {}

        self.ws = websocket.WebSocketApp("wss://"+self.__host+":"+self.__port,
                                         on_open=lambda ws: self.__on_open(ws),
                                         on_message=lambda ws, message: self.__on_message(ws, message),
                                         on_close=self.__on_close,
                                         on_error=self.__on_error)


    def __on_open(self, ws):
        print("Connection opened")
        ws.send("Тут должен быть текст для проверки пользователя")

    def __on_message(self, ws, message):
        jsn = json.loads(message)
        if jsn['action'] in self.actions:
            try:
                threading.Thread(target=self.actions[jsn['action']], args=(jsn['data'],)).start()
            except Exception as e:
                traceback.print_exc()
                pass
        else:
            print("Action not found: " + jsn['action'])

    def __on_close(self, ws, close_code, close_msg):
        print("Connection closed", close_code, close_msg)

    def __on_error(self, ws, error):
        print(error)


    def __server_start(self):
        self.ws.run_forever(None, {"cert_reqs": ssl.CERT_NONE}, reconnect=True)


    def start(self):
        if self.__thread is None:
            self.__thread = threading.Thread(target=self.__server_start)
            self.__thread.start()
    def stop(self):
        if self.__thread is not None:
            self.ws.close()
    def AddAction(self, name, func):
        self.actions[name] = func

    def RemoveAction(self, name):
        del self.actions[name]

    def send(self, struct):
        if self.ws.sock.connected:
            self.ws.send(json.dumps(struct))
            return True
        else:
            return False


if __name__ == '__main__':
    RC_C = RC_Client("192.168.1.12", "8765")
    RC_C.start()