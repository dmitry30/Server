from module_loader import singleton, action, module_start, module_stop
import Competitor_prices.db_actions as db_actions
import Competitor_prices.rc_cient as rc_cient

import threading
import time


@singleton
class CompetitorPrices:
    DB = None


    @classmethod
    @action("CompetitorPrices_GetPrices")
    # {} -> [{"GUID":ProductGUID,"medium_cost":100.00}, ...]
    def get_prices(cls, data):
        #table = cls.DB.get_all_prices()
        #return [{"GUID": row[0], "cost": row[1]} for row in table]
        return {"function": "CompetitorPrices_SetProducts"}

    @classmethod
    @action("CompetitorPrices_SetProducts")
    # [{"GUID":PartnerGUID,"products":[{"GUID":ProductGUID, "url":"URL"}, ...]}, ...] -> {}
    def set_products(cls, data):
        return {"function": "CompetitorPrices_SetProducts"}

    @classmethod
    @module_start
    def start(cls, OldData = None):
        #cls.DB = db_actions.DbActions()

    @classmethod
    @module_stop
    def stop(cls):
        return None #OldData


# Initiallization module
CompetitorPrices()