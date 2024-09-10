from telebot   import TeleBot, util

import secret
from handlers.BanList_meneger import BanList

bot = TeleBot(secret.TOKEN)
ban_list = BanList(r"data/ban_list.json")

def ban_user(message):
    id = util.extract_arguments(message.text)
    try:
        id = int(id)
    except ValueError:
        return bot.send_message(message.chat.id, "id is not correct\n"+id)
    else:
        ban_list.append(id)
        ban_list.save()

        return bot.send_message(message.chat.id, f"user banned\n<pre>{id}</pre>", parse_mode='html')

def unban_user(message):
    id = util.extract_arguments(message.text)
    try:
        id = int(id)
    except ValueError:
        return bot.send_message(message.chat.id, "id is not correct\n"+id)

    ban_list = BanList(r"data/ban_list.json")
    if id in ban_list:
        ban_list.remove(id)
    else:
        return bot.send_message(message.chat.id, "id not found\n"+str(id))

    ban_list.save()
    bot.send_message(message.chat.id, f"user unbanned\n<pre>{id}</pre>", parse_mode='html')

def get_ban_list(message):
    ban_list = BanList(r"data/ban_list.json")
    bot.send_message(message.chat.id, f"<pre>len: {len(ban_list)}</pre>\n\n{ban_list}", parse_mode='html')

    with open(ban_list.path, 'rb') as f:
        return_message= bot.send_document(message.chat.id, f)

    return return_message
