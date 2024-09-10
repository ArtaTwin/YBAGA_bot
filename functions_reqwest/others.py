from telebot   import TeleBot, util

import secret
from handlers.Audience_meneger import Audience
from handlers.stenography_handler import decoder

bot = TeleBot(secret.TOKEN)

def get_all_SubId(message):
    audience = Audience(r"data/audience.json")
    resalt = audience.all_SubId()
    bot.send_message(secret.ADMIN_ID, f"<pre>len: {len(resalt)}</pre>\n\n{resalt}", parse_mode='html')
    with open(r'data/audience.json','rb') as f:
        return_message= bot.send_document(secret.ADMIN_ID, f)

    return return_message


def get_log(message):
    with open("Log.log", 'rb') as f:
        return_message= bot.send_document(message.chat.id, f)
    return return_message

def cleen_log(message):
    with open("Log.log", 'w') as f:
        pass
    return bot.send_message(message.chat.id, "\'Log.log\' cleaned")


def dc(message): #decoder
    bin, id = decoder(
        util.extract_arguments(message.text)
    )
    return bot.send_message(message.chat.id, f"bin: <pre>{bin}</pre>\nid: <pre>{id}</pre>", parse_mode='html')
