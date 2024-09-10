import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot

import secret
from handlers.situation_getter   import get_situation
from handlers.map_maker          import painter
from handlers.stenography_handler import pictorial
from handlers.BanList_meneger    import BanTuple
from handlers.texts import PHOTO


bot = TeleBot(secret.TOKEN)
ban_tuple = BanTuple(r"data/ban_list.json")
data_last_photo = {
    "file_id" : str(),
    "version_time" : float()
}


def photo(message, security_level=3):
    global data_last_photo
    situation = get_situation(message.from_user.id)
    situation_mtime= Path(r'data/situation.json').lstat().st_mtime
    date= datetime.fromtimestamp(
        situation_mtime, tz=timezone('Europe/Kiev')
    ).strftime('%d.%m %H:%M')

    conclusion = str()
    alarm_list= [
        state["Name"]
        for state in situation
        if state["alarm"]
    ]

    if alarm_list:
        conclusion= "Тривога у:\n"
        for n, state in enumerate(alarm_list, start=1):
            conclusion+= f"{n}. {state}\n"
    else:
        conclusion= "Тривоги немає ✅\n"

    text= PHOTO.format(date=date, conclusion=conclusion)

    if 0 < message.chat.id:
        text+= "\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    if data_last_photo["version_time"] == situation_mtime and message.from_user.id not in ban_tuple and security_level<3:
        return bot.send_photo(message.chat.id, data_last_photo["file_id"], text, parse_mode='html')

    maket, pal_maket = pictorial(
        (0, 0, int(time.time()), message.from_user.id)[security_level]
    )

    image = painter(situation, maket, pal_maket)

    if security_level<=2:
        resalt= bot.send_photo(message.chat.id, image, text, parse_mode='html')
        data_last_photo = {
            "file_id" : resalt.photo[-2].file_id,
            "version_time" : situation_mtime
        }
        return resalt
    else:
        return bot.send_photo(message.chat.id, image, text, parse_mode='html')
