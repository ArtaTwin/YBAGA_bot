import time
from datetime  import datetime
from pathlib   import Path

from pytz      import timezone
from telebot   import TeleBot

import secret
from handlers.situation_getter import get_situation
from handlers.stenography_handler import writing
from handlers.texts import INFO


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


def info(message, security_level=3):
    date= datetime.fromtimestamp(
        Path(r'data/situation.json').lstat().st_mtime,
        tz=timezone('Europe/Kiev')
    ).strftime('%d.%m %H:%M')

    summary= str()
    alarm_count = 0

    for i, state in enumerate(get_situation(message.from_user.id), start=1):
        if state["alarm"]:
            summary+= f"{i}. <b>{state['Name']}</b> - 🚨"
            alarm_count+= 4
        else:
            summary+= f"{i}. {state['Name']} - ✅"
        summary+= timedelta(state['date'])+ "\n"

    if alarm_count > 0:
        conclusion= f'На {alarm_count}% території України оголошено тривогу!'
    else:
        conclusion= "<b>Тривоги немає</b> ✅"

    text= INFO.format(date=date, summary=summary, conclusion=conclusion)

    if security_level:
        text= writing(text, message.from_user.id)

    if 0 < message.chat.id:
        text+= "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    return bot.send_message(message.chat.id, text, parse_mode='html')
