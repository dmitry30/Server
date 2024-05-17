from module_loader import singleton, action, module_start, module_stop
from . import db_actions
from . import rc_client

import threading
import time
import requests
from schedule import Scheduler

def send(*message):
    r = requests.post("http://127.0.0.1:8019", json={'action':'TG_send','data':{'id': 0, 'message': "\n".join([str(mes) for mes in message]).replace("\\n", "\n").replace("\\\\", "\\")}})
    try:
        if r.status_code != requests.codes:
            return False
        if 'error' not in r.json():
            return True
    except:
        return False


@singleton
class CompetitorPrices:
    DB: db_actions.DbActions = None
    RCC: rc_client.RC_Client = None
    thr_sch = None

    @classmethod
    @action("CompetitorPrices_GetPrices")
    # {} -> [{"GUID":ProductGUID,"medium_cost":100.00}, ...]
    def get_prices(cls, data):
        table = cls.DB.get_all_prices()
        return [{"GUID": row[0], "cost": row[1]} for row in table]

    @classmethod
    @action("CompetitorPrices_SetProducts")
    # [{"GUID":PartnerGUID,"products":[{"GUID":ProductGUID, "URL":"URL"}, ...]}, ...] -> {}
    def set_products(cls, data):
        dict1, dict2, dict3 = cls.DB.set_products(data)
        dataW = {}

        for paID in dict3:
            wID = dict1[paID][2]
            if wID is None:
                print("No worker for partner " + str(paID))
                continue
            if wID not in dataW:
                dataW[wID] = {'name': dict1[paID][3].strip(), 'data': {}}
            city = dict1[paID][4].strip()
            if city not in dataW[wID]['data']:
                dataW[wID]['data'][city] = []
            for prID in dict3[paID]:

                dataW[wID]['data'][city].append({'id': prID, 'url': dict3[paID][prID]['URL']})

        for wID in dataW:
            cls.RCC.send({"action": "CP_"+dataW[wID]['name']+"_NewItem", "data": dataW[wID]['data']})

        return {"function": "CompetitorPrices_SetProducts"}

    @classmethod
    @action("CompetitorPrices_RC_Redirect")
    # {"action":Action, "data":Data}
    def set_products(cls, data):
        cls.RCC.send(data)
        return {"function": "CompetitorPrices_RC_Redirect"}

    @classmethod
    @module_start
    def start(cls, OldData = None):
        self: CompetitorPrices = CompetitorPrices()
        cls.DB = db_actions.DbActions()
        cls.RCC = rc_client.RC_Client("192.168.1.12", "8765")
        cls.RCC.start()
        cls.RCC.AddAction("CP_Error", self.error)
        cls.RCC.AddAction("CP_NewPrices", self.newPrices)
        cls.RCC.AddAction("CP_NewParam", self.newParam)
        cls.RCC.AddAction("CP_SendProducts", self.sendProducts)
        cls.thr_sch = threading.Thread(target=cls.__TimeTable, args=(cls,))
        cls.thr_sch.start()
        time.sleep(5)
        wNames = cls.DB.get_workers_name()
        for wName in wNames:
            self.sendProducts({'competitor': wName})

    @classmethod
    @module_stop
    def stop(cls):
        cls.RCC.RemoveAction("CP_Error")
        cls.RCC.RemoveAction("CP_NewPrices")
        cls.RCC.RemoveAction("CP_NewParam")
        cls.RCC.RemoveAction("CP_SendProducts")
        cls.RCC.stop()
        thr = cls.thr_sch
        cls.thr_sch = None
        thr.join()
        return None

    def __TimeTable(self):
        sch = Scheduler()
        sch.every().day.at("04:30").do(self.__GetPrices)
        sch.every().day.at("09:30").do(self.__GetPrices)

        while self.thr_sch is not None:
            sch.run_pending()
            time.sleep(60)

    def __GetPrices(self):
        wNames = self.DB.get_workers_name()
        for wName in wNames:
            self.RCC.send({"action": "CP_" + wName +"_GetPrices", "data": ""})

    def error(self, data):
        if not send(data):
            print(data)

    def newPrices(self, data):
        paIDs = self.DB.get_partnersID_by_worker_request(data['competitor'], list(data['data'].keys()))


        for city in data['data']:
            if city not in paIDs or len(data['data'][city]) == 0:
                continue
            self.DB.set_prices(data['data'][city], paIDs[city])

    def newParam(self, data):
        if len(data['data']) == 0:
            return
        paIDs = self.DB.get_partnersID_by_worker_request(data['competitor'], list(data['data'].keys()))
        for city in data['data']:
            if city not in paIDs or len(data['data'][city]) == 0:
                continue
            self.DB.set_param(data['data'][city], paIDs[city])

    def sendProducts(self, data):
        tab1 = self.DB.get_products(data['competitor'])
        dataW = {}
        for row in tab1:
            cShortName = row[0].strip()
            if cShortName not in dataW:
                dataW[cShortName] = []
            if row[3] is not None:
                dataW[cShortName].append({'id': row[1], 'url': row[2], 'param': row[3]})
            else:
                dataW[cShortName].append({'id': row[1], 'url': row[2]})

        if len(dataW) == 0:
            return
        self.RCC.send({"action": "CP_" + data['competitor'] +"_NewItem", "data": dataW})




# Initiallization module
CompetitorPrices()
