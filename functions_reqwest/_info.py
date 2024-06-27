import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot

import secret
from .handlers.situation_getter import get_situation
from .handlers.stenography_module import writing


bot = TeleBot(secret.TOKEN)

def timedelta(t):
    t = time.time()-t
    if t < 120:
        return " 1 хв"
    elif t < 3600:
        return f" {t//60:.0f} хв"
    elif t < 86400:
        return f" {t//3600:.0f} год"
    else:
        return f" {t//86400:.0f} д"

def info(message, security_level):
    date= datetime.fromtimestamp(
        Path(r'data/situation.json').lstat().st_mtime,
        tz=timezone('Europe/Kiev')
    )
    text= f"Станом на {date.strftime('%d.%m %H:%M')} за Києвом\n\nСитуація у: \n"
    is_alarm = bool()

    for i, state in enumerate(get_situation(message.from_user.id), start=1):
        if state["alarm"]:
            text+= f"\n{i}. <b>{state['Name']}</b> - 🚨"
            is_alarm= True
        else:
            text+= f"\n{i}. {state['Name']} - ✅"
        text+= timedelta(state['date'])

    if is_alarm:
        text+= f'\n\nНа {text.count("🚨")*4}% території України оголошено тривогу!'
    else:
        text+= "\n\n<b>Тривоги немає</b> ✅"

    if security_level:
        text= writing(text, message.from_user.id)

    if 0 < message.chat.id:
        text+= "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    bot.send_message(message.chat.id, text, parse_mode='html')
