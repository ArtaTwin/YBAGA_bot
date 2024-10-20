import json
import threading
import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot, util, ExceptionHandler

import secret
import update_situation
import functions_reqwest
from handlers.error_handler import *
from handlers.texts import WELCOME, INFORMANT, PING

def information(message):
    if security_level == 0:
        return

    information_text= INFORMANT.format(
        date= datetime.fromtimestamp(message.date).strftime('%d/%m/%Y %H:%M:%S'),
        name= message.from_user.first_name,
        username= message.from_user.username,
        last_name= message.from_user.last_name,
        id= message.from_user.id,
        chat_type= message.chat.type,
        chat_id= message.chat.id,
        text= message.text
    )
    bot.send_message(secret.ADMIN_ID, information_text, parse_mode='html')

class ExceptionHandler(ExceptionHandler):
    def handle(self, exc_value):
        if exc_value.__class__ == ZeroDivisionError:
            return False
        else:
            my_excepthook(exc_value.__class__, exc_value, exc_value.__traceback__)
            return True


bot= TeleBot(secret.TOKEN, exception_handler=ExceptionHandler())
security_level= 1

make_warning(20, f"<{datetime.now().strftime('%x %X')}> Trevoga_bot.py started")
threading.Thread(target=update_situation.main, daemon=False).start()
time.sleep(10)

@bot.message_handler(commands=['test', 't', 'ping', 'p'])
def ping(message):
    answer= 'tost' if 't' in util.extract_command(message.text) else 'pong'
    ping_time= round(time.time()-message.date,2)
    resalt_testing= [
        [func, None]
        for func in functions_reqwest.list_my_tg_funcs
    ]

    def repr_resalt_test_func(item_func):
        one = item_func[0].__name__
        two = str()

        if item_func[-1] == None:
            two= '🔘'
        elif item_func[-1]:
            two= '✔️'
        else:
            two= '✖️'

        return f"{one} >> {two}"

    text= PING.format(
        answer= answer,
        ping_time= ping_time,
        resalt_testing= "\n".join(
            map(repr_resalt_test_func, resalt_testing)
        )
    )
    bot_message= bot.send_message(message.chat.id, text)

    for n, item_func in enumerate(resalt_testing):
        try:
            test_message = item_func[0](message)
        except:
            resalt_testing[n][-1] = False
        else:
            time.sleep(3)
            bot.delete_message(test_message.chat.id, test_message.message_id)
            resalt_testing[n][-1] = True

        text= PING.format(
            answer= answer,
            ping_time= ping_time,
            resalt_testing= "\n".join(
                map(repr_resalt_test_func, resalt_testing)
            )
        )

        bot.edit_message_text(chat_id=bot_message.chat.id,
            message_id=bot_message.message_id, text=text,
        )


@bot.message_handler(commands=['restart', 'r'])
def restart(message):
    if message.from_user.id==secret.ADMIN_ID:
        bot.send_message(
            message.chat.id,
            f"{datetime.fromtimestamp(message.date).strftime('%x %X')}\n Bot start to restart"
        )

        #This forces telebot to crash exit. It will be restarted by service script. We tried exit(1), KeyboardInterrup, but they don't work as good as 1/0
        1/0

@bot.message_handler(commands=['su']) #security_level up
def su(message):
    if message.from_user.id==secret.ADMIN_ID:
        global security_level
        if security_level < 3:
            security_level+=1
        bot.send_message(message.chat.id, f"security_level: <b>{security_level}</b>", parse_mode='html')

@bot.message_handler(commands=['sd']) #security_level down
def sd(message):
    if message.from_user.id==secret.ADMIN_ID:
        global security_level
        if security_level > 0:
            security_level-=1
        bot.send_message(message.chat.id, f"security_level: <b>{security_level}</b>", parse_mode='html')

#bot.message_handler(functions_reqwest.ping, commands=["test"])

@bot.message_handler(commands=['stiker', 's'])
def stiker(message):
    with open(r'static/map.png' , "rb") as f:
        bot.send_sticker(message.chat.id , f)
    information(message)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, WELCOME,
        parse_mode='html', disable_web_page_preview= True)
    information(message)

@bot.message_handler(commands=functions_reqwest.list_admin_function)
def A(message):
    if message.from_user.id==secret.ADMIN_ID:
        command= util.extract_command(message.text)
        functions_reqwest.dict_admin_function[command](message)

@bot.message_handler(commands=functions_reqwest.list_function)
def B(message):
    if Path(r'data/situation.json').lstat().st_mtime+120 < time.time():
        make_warning(50, f"Updater freezed 🤬🤬🤬")
    command= util.extract_command(message.text)
    functions_reqwest.dict_function[command](message, security_level= security_level)
    information(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    functions_reqwest.form_controller.callback_form(call)

bot.polling(none_stop=True, interval = 5)
