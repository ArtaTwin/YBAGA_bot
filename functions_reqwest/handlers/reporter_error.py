import time
import sys
import threading
import logging
from datetime  import datetime

from telebot   import TeleBot, apihelper, ExceptionHandler

import secret

__all__ = ['report_error', 'repr_traceback']


bot = TeleBot(secret.TOKEN)
"""logging.basicConfig(level=logging.INFO, filename=f"{__name__}.log",
                    format="%(asctime)s | %(levelname)s | %(message)s", filemode="w")
"""
#class ListOfEr
list_error=[]

def try_send_message(text):
    try:
        bot.send_message(secret.ADMIN_ID, text)
    except apihelper.ApiTelegramException:
        print("Telegram-API not working")
        time.sleep(5)

def get_disassembly_traceback(traceback):
    disassembly_traceback_list = list()

    while traceback != None:
        n_traceback = (traceback.tb_frame.f_code.co_filename,
            traceback.tb_lineno,
            traceback.tb_frame.f_code.co_name)

        disassembly_traceback_list.append(n_traceback)

        traceback = traceback.tb_next

    return disassembly_traceback_list


def repr_traceback(traceback):
    text="\n"

    k = 0
    while traceback != None:
        k += 1

        text+= f"{k}|| \'{traceback.tb_frame.f_code.co_filename}\' line {traceback.tb_lineno}, in \'{traceback.tb_frame.f_code.co_name}\' \n"
        traceback = traceback.tb_next
    return text
"""
def f(exc_type, exc_value, traceback):
    exc_value = repr(exc_value)
    traceback = get_disassembly_traceback(traceback)


    data = datetime.now().strftime('%x %X')


"""


def report_error(exc_type, exc_value, traceback):
    if (exc_type, exc_value, traceback) in list_error:
        print("pass")
        time.sleep(5)
        return
    else:
        list_error.append(traceback)

    def try_send_message(text):
        try:
            bot.send_message(secret.ADMIN_ID, text)
        except apihelper.ApiTelegramException:
            print("Telegram-API not working")
            time.sleep(5)

    date = datetime.now().strftime('%x %X')

    resalt_repr_traceback = repr_traceback(traceback)
    print(f"\n!!! !!! ERROR: {repr(exc_value)} | {date}" +resalt_repr_traceback)
    try_send_message(f"❗️ ERROR: {repr(exc_value)} | {date}" +resalt_repr_traceback)

    time.sleep(1)

sys.excepthook = report_error
threading.excepthook = lambda ExceptHookArgs: report_error(ExceptHookArgs.exc_type,
    ExceptHookArgs.exc_value, ExceptHookArgs.exc_traceback)
