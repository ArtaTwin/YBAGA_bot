import threading
import time
import logging
import sys
from datetime  import datetime

from telebot   import TeleBot, apihelper, ExceptionHandler

import secret

#__all__ = ['report_error', 'repr_traceback']

file_log = logging.FileHandler('Log.log')
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out),
                    format='[%(asctime)s | %(levelname)s] %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)

def SendTextByTelegram(text):
    try:
        TeleBot(secret.TOKEN).send_message(secret.ADMIN_ID, text)
    except apihelper.ApiTelegramException as e:
        logging.log(30, "Telegram-API not working <- "+repr(e))
    except Exception as e:
        logging.log(40, "SendTextByTelegram don`n work <- "+repr(e))
    finally:
        time.sleep(5)


def repr_traceback(traceback):
    text='\n'

    k = 0
    while traceback != None:
        k += 1

        text+= f">{k}| \'{traceback.tb_frame.f_code.co_filename}\' line {traceback.tb_lineno}, in \'{traceback.tb_frame.f_code.co_name}\' \n"
        traceback = traceback.tb_next
    return text

def make_warning(level: int, msg: str, *args, **kwargs):
    date= datetime.now().strftime('%x %X')
    level_str= str()

    if level%10 or level>60:
        level_str= f"Level {level}"
    else:
        level_str= ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")[level//10]

    logging.log(level, msg, *args, exc_info=True, **kwargs)
    SendTextByTelegram(f"⚠ {level_str} | {date}\n message: {msg}")


def my_excepthook(exc_type, exc_value, traceback):
    date = datetime.now().strftime('%x %X')
    resalt_repr_traceback = repr_traceback(traceback)
    repr_exc_value= repr(exc_value)

    logging.critical(repr_exc_value+resalt_repr_traceback) #add agrs
    SendTextByTelegram(f"❗️ CRITICAL: {repr_exc_value} | {date}\n" +resalt_repr_traceback)
    time.sleep(5)

def report_except(exc_type, exc_value, traceback):
    my_excepthook(exc_type, exc_value, traceback)

sys.excepthook = my_excepthook
threading.excepthook = lambda ExceptHookArgs: my_excepthook(ExceptHookArgs.exc_type,
    ExceptHookArgs.exc_value, ExceptHookArgs.exc_traceback)
