import asyncio
import websocket
import ssl
import threading

class RC_Client():
    __thread = None
    __host = None
    __port = None

    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.ws = websocket.WebSocketApp("wss://"+host+":"+port,
                                         on_open=lambda ws: self.__on_open(ws),
                                         on_message=lambda ws, message: self.__on_message(ws, message),
                                         on_close=lambda ws: self.__on_close(ws))


    def __on_open(self, ws):
        print("Connection opened")
        ws.send("Тут должен быть текст для проверки пользователя")

    def __on_message(self, ws, message):
        print(f"Received message: {message}")

    def __on_close(self, ws):
        print("Connection closed")

    def start(self):
        self.__thread = threading.Thread(target=self.ws.run_forever, args=(None, {"cert_reqs": ssl.CERT_NONE}))
        self.__thread.start()

    def AddAction(self, name, func):
        self.actions[name] = func

    def RemoveAction(self, name):
        del self.actions[name]

RC_C = RC_Client("192.168.1.12", "8765")
RC_C.start()