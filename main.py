import module_loader
from Server import http_server
import time


if __name__ == '__main__':
    ML = module_loader.ModuleLoader()
    ML.setServer(http_server.HttpServer(('', 8019)))
    ML.hServ.StartServer()
    ML.load_module("telegram")
    ML.load_module("competitor_prices")
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        ML.hServ.StopServer()
        modules = [_ for _ in ML.modules]
        for md in modules:
            ML.action_delete_module({"module_name": md})
