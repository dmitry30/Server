import http.server
import json
from threading import Thread

class HttpServer(http.server.HTTPServer):

    class HttpHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        def do_POST(self):
            data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            print(data)

            res = self.server.ActionsProcessing(data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(res).encode('utf-8'))

    def __init__(self, server_address):
        self.server_address = server_address
        self.actions = {}
        self.Thd = None
        super().__init__(self.server_address, self.HttpHandler)

    def AddAction(self, name, func):
        self.actions[name] = func

    def RemoveAction(self, name):
        del self.actions[name]

    def ActionsProcessing(self, jsn):
        if jsn['action'] in self.actions:
            try:
                return self.actions[jsn['action']](jsn['data'])
            except Exception as e:
                print(jsn['action'] + " : " + str(e))
                return {"error": "Error in " + jsn['action']}
        return {"error": "Action not found"}

    def StartServer(self):
        if self.Thd is None:
            self.Thd = Thread(target=self.serve_forever)
            self.Thd.start()

    def StopServer(self):
        if self.Thd is not None:
            self.server_close()
            self.Thd = None