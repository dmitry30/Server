from module_loader import singleton, action, module_start, module_stop
import time
import telebot
import threading

@singleton
class Telegram:
    BOT_TOKEN = "6450880386:AAHXWFQDzcBOnKtIRvKA8-bUXc5pyYu2UHc"
    BOT : telebot.TeleBot = None

    users = {0: 215189899, 1: 215189899}

    @classmethod
    @action("TG_send")
    # {id:, message: } -> {}
    def send_message(cls, data):
        cls.BOT.send_message(cls.users[data['id']], data['message'])

    @classmethod
    @module_start
    def start(cls, OldData = None):
        cls.BOT = telebot.TeleBot(cls.BOT_TOKEN)
        threading.Thread(target=cls.BOT.polling, args=(True, False, 60))

    @classmethod
    @module_stop
    def stop(cls):
        pass


# Initiallization module
Telegram()
