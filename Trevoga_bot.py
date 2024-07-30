import json
import threading
import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot, apihelper, util, ExceptionHandler

import secret
import update_situation
from handlers.error_handler import *
from handlers.Audience_meneger import Audience
from handlers.BanList_meneger import BanList
from handlers.stenography_handler import decoder
from functions_reqwest import _info, _photo, form_controller


def information(message):
    if security_level == 0:
        return

    text_tg = f"""
🔵 {datetime.fromtimestamp(message.date).strftime('%d/%m/%Y %H:%M:%S')}

Name: <pre>{message.from_user.first_name}</pre>
Username: <pre>{message.from_user.username}</pre>
LastName:<pre>{message.from_user.last_name}</pre>
UserId: <pre>{message.from_user.id}</pre>
MessageId: {message.message_id}
ChatType: {message.chat.type}
Chat_id: <pre>{message.chat.id}</pre>
Command: {message.text}
"""
    bot.send_message(secret.ADMIN_ID, text_tg, parse_mode='html')

class ExceptionHandler(ExceptionHandler):
    def handle(self, exc_value):
        if exc_value.__class__ == ZeroDivisionError:
            return False
        else:
            my_excepthook(exc_value.__class__, exc_value, exc_value.__traceback__)
            return True


bot= TeleBot(secret.TOKEN, exception_handler=ExceptionHandler())
ban_list= BanList(r"data/ban_list.json")
security_level= 1
dict_function= {
    "info" : _info.info,
    "map" : _photo.photo,
    "form" : form_controller.form
}

make_warning(20, f"<{datetime.now().strftime('%x %X')}> Trevoga_bot.py started")
threading.Thread(target=update_situation.main, daemon=True).start()
freeze_updater= 0

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
        security_level+=1
        bot.send_message(message.chat.id, f"security_level: <b>{security_level}</b>", parse_mode='html')

@bot.message_handler(commands=['sd']) #security_level down
def sd(message):
    if message.from_user.id==secret.ADMIN_ID:
        global security_level
        if security_level:
            security_level-=1
        bot.send_message(message.chat.id, f"security_level: <b>{security_level}</b>", parse_mode='html')

@bot.message_handler(commands=['as']) #all SubId
def all_sub(message):
    if message.from_user.id==secret.ADMIN_ID:
        audience = Audience(r"data/audience.json")
        all_SubId = audience.all_SubId()
        bot.send_message(secret.ADMIN_ID, f"<pre>len: {len(all_SubId)}</pre>\n\n{all_SubId}", parse_mode='html')
        with open(r'data/audience.json','rb') as f:
            bot.send_document(secret.ADMIN_ID, f)

@bot.message_handler(commands=['ban', 'b'])
def ban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = util.extract_arguments(message.text)
        try:
            id = int(id)
        except ValueError:
            bot.send_message(message.chat.id, "id is not correct\n"+id)

        ban_list.append(id)

        ban_list.save()
        bot.send_message(message.chat.id, f"user banned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['unban', 'ub'])
def unban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = util.extract_arguments(message.text)
        if id.isalpha():
            bot.send_message(message.chat.id, "id is not correct\n"+id)
            return

        if id in ban_list:
            ban_list.remove(id)
        else:
            bot.send_message(message.chat.id, "id not found\n"+str(id))
            return

        ban_list.save()
        bot.send_message(message.chat.id, f"user unbanned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['sbl']) #send ban_list
def sbl(message):
    if message.from_user.id==secret.ADMIN_ID:
        bot.send_message(message.chat.id, f"<pre>len: {len(ban_list)}</pre>\n\n{ban_list}", parse_mode='html')

        with open(ban_list.path, 'rb') as f:
            bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['glog']) #get Log.log
def glog(message):
    if message.from_user.id==secret.ADMIN_ID:
        with open("Log.log", 'rb') as f:
            bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['clog']) #cleen Log.log
def clog(message):
    if message.from_user.id==secret.ADMIN_ID:
        open("Log.log", 'w').close()
        bot.send_message(message.chat.id, "\'Log.log\' cleaned")

@bot.message_handler(commands=['decoder', 'dc'])
def dc(message):
    if message.from_user.id==secret.ADMIN_ID:
        bin, id = decoder(
            util.extract_arguments(message.text)
        )
        bot.send_message(message.chat.id, f"bin: <pre>{bin}</pre>\nid: <pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['test','t','ping','p'])
def ping(message):
    text=f"""
{'tost' if "t" in message.text else 'pong'}
затримка: {round(time.time()-message.date,2)} сек
freeze_updater: {freeze_updater} times
ваш статус: {bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id).status}
версія: 4.8.0+"""
    bot.send_message(message.chat.id, text)
    information(message)

@bot.message_handler(commands=['stiker', 's'])
def stiker(message):
    with open(r'static/map.png' , "rb") as f:
        bot.send_sticker(message.chat.id , f)
    information(message)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    help_text = """
/info - Надсилаю перелік з інформацію про стан у регіонах Україні
/map - Надсилаю мапу тривог України
/form - Налаштування надсилання повідомлень про початок або відбій тривоги
<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>

<b><a href='https://t.me/+FeZvEeXW5lIzMjYy'>Support Тривога Бот</a></b>
"""

    bot.send_message(message.chat.id, help_text,
        parse_mode='html', disable_web_page_preview= True)
    information(message)

@bot.message_handler(commands=list(dict_function))
def multipurpose(message):
    if Path(r'data/situation.json').lstat().st_mtime+120 < time.time():
        global freeze_updater
        freeze_updater+=1
        threading.Thread(target=update_situation.main, daemon=True).start()
        make_warning(30, f"Updater freezed {freeze_updater}. Started one more thread.")
        time.sleep(10)
    command= util.extract_command(message.text)
    dict_function[command](message, security_level)
    information(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    form_controller.callback_form(call)

bot.polling(none_stop=True, interval = 1)
