Для провекри запросов можно добавить текст в a.html
Текст в Massd[*]
Добавить кнопку 
<button onclick='document.getElementsByTagName("textarea")[0].value = Massd[*];'>Name_Command</button>

Для нового модуля:
Модуль это пакет питона например мой competitor_prices (директория внутри которой есть __init__.py)
В ней же дополнительные файлы, которые нужны для работы
Дополнительный файлы подключать так
from . import db_actions
from . import rc_client

Внутри модуля должно быть :
from module_loader import singleton, action, module_start, module_stop
###
@singleton
class CLASS_NAME:
    @classmethod
    @action("HTTP_ACTION")
    def function(cls, data):
      pass
    @classmethod
    @module_start
    def function(cls, data):
      pass
    @classmethod
    @module_stop
    def function(cls, data):
      pass
###
CLASS_NAME()

Можно добавить загрузку модуля в main:      ML.load_module("competitor_prices")


Для отправки сообщений в телеграмме, надо написать что-то такое(напрямую подключать нельзя, так как тогда не будет работтать обновление модуля, хотя может оно и не надо): 
import requests

def send(*message):
    r = requests.post("http://127.0.0.1:8019", json={'action':'TG_send','data':{'id': 0, 'message': "\n".join([str(mes) for mes in message]).replace("\\n", "\n").replace("\\\\", "\\")}})
    try:
        if r.status_code != requests.codes:
            return False
        if 'error' not in r.json():
            return True
    except:
        return False
###
send(data)

При отправке на сервер '{"action": "ModuleLoad", "data": {"module_name": "competitor_prices"}}'
обновляется не только модуль но и все  подмодули в пакете


