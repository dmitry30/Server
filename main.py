import module_loader
import http_server
import time

if __name__ == '__main__':
    ML = module_loader.ModuleLoader()
    ML.setServer(http_server.HttpServer(('', 8019)))
    #ML.load_module("competitor_prices")
    ML.hServ.StartServer()
    while True:
        time.sleep(10000)
