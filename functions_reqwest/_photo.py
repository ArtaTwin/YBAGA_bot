import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot

import secret
from .handlers.situation_getter   import get_situation
from .handlers.map_maker          import painter
from .handlers.stenography_module import pictorial
from .handlers.ban_list_module    import Ban_list


bot = TeleBot(secret.TOKEN)
ban_list = Ban_list(r"data/ban_list.json")
data_map = {
    "file_id" : str(),
    "version_time" : float()
}

def photo(message, security_level):
    global data_map
    situation = get_situation(message.from_user.id)
    situation_mtime= Path(r'data/situation.json').lstat().st_mtime

    text= f"Станом на {datetime.fromtimestamp(situation_mtime, tz=timezone('Europe/Kiev')).strftime('%d.%m %H:%M')} за Києвом\n\n"


    difference = int()
    str_list_of_alarm = str()
    for k, state in enumerate(situation, start=1):
        if not state["alarm"]:
            difference += 1
            continue
        str_list_of_alarm += f"{k-difference}. {state['Name']}\n"

    if difference:
        text += "Тривога у:\n"+ str_list_of_alarm
    else:
        text += "Тривоги немає ✅\n"

    if 0 < message.chat.id:
        text+= "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    if data_map["version_time"] == situation_mtime and message.from_user.id not in ban_list and security_level<3:
        bot.send_photo(message.chat.id, data_map["file_id"], text, parse_mode='html')
        return

    if security_level < 2:  # [0, 0, int(time.time()), message.from_user.id]
        maket, stenography_pal = pictorial(0)
    elif security_level == 2:
        maket, stenography_pal = pictorial( int(time.time()) )
    else:
        maket, stenography_pal = pictorial(message.from_user.id)

    image = painter(situation, maket, stenography_pal)

    if security_level<3:
        data_map = {
            "file_id" : bot.send_photo(message.chat.id, image, text, parse_mode='html').photo[-2].file_id,
            "version_time" : situation_mtime
        }
    else:
        bot.send_photo(message.chat.id, image, text, parse_mode='html')
