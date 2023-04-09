from telebot   import TeleBot, types
from json      import load, dump
from datetime  import datetime
from threading import Thread
from time      import time, sleep
import secret
print("Trevoga_bot.py started")

bot = TeleBot(secret.TOKEN)
flag = True
Info = load(open("JSONs/Info.json", "rb"))

def updater():
    import update_situation
Thread(target=updater, args=(), daemon=True).start()
del Thread, updater

def findl(list,element):
    return bool(list.count(element))

def timedelta(t):
    t = int(time())-t
    if t < 60:
        return " 1 хв"
    if t < 3601:
        return f" {t//60} хв"
    if t < 86400:
        return f" {t//3600} год"
    if t > 86399:
        return f" {t//86400} д"

def status_user(user_id, chat_id): #message.from_user.id, message.chat.id
    return bot.get_chat_member(chat_id=chat_id, user_id=user_id).status

def information(message):
    if flag:
        if message.from_user.id == 1087968824:
            bot.send_message(965712322, str(message))
            for i in message.entities:
                bot.send_message(965712322, str(i))
        bot.send_message(965712322, f"📎🔵\n{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} :\n \nИмя:<pre>{message.from_user.first_name}</pre>\nПсевдоним:<pre>{message.from_user.username}</pre>\nUser_id=<pre>{message.from_user.id}</pre>\nmessage_id={message.message_id}\nlast_name:<pre>{message.from_user.last_name}</pre>\nТип чата:{message.chat.type}\nChat_id = <pre>{message.chat.id}</pre>\nmess: {message.text}",parse_mode='html')
    #print(f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} /: \nИмя:{message.from_user.first_name} |Псевдоним:{message.from_user.username} |User_id={message.from_user.id} |message_id={message.message_id} |last_name:{message.from_user.last_name} |Тип чата:{message.chat.type} |mess: {message.text}\n")

@bot.message_handler(commands=['restart', 'r'])
def restart(message):
    if message.from_user.id==965712322 or message.chat.id==552733968:
        bot.send_message(message.chat.id,f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')}\n Bot start to restart")
        #This forces telebot to crash exit. It will be restarted by service script. We tried exit(1), KeyboardInterrup, but they don't work as good as 1/0
        1/0

@bot.message_handler(commands=['f'])
def f(message):
    if message.chat.id==965712322:
        global flag
        bot.send_message(965712322,str(flag := flag == False))

@bot.message_handler(commands=['if'])
def InfoFile(message):
    if message.chat.id==965712322:
        s = set()
        for x in Info.values():
            for i in x:
                s.add(i)
        bot.send_message(965712322, f"<pre>len: {len(s)}</pre>\n\n{s}",parse_mode='html')
        del s
        bot.send_document(965712322, open('JSONs/Info.json','rb'))

#testing
@bot.message_handler(commands=['test','t','ping','p'])
def testing(message):
    now = time()
    bot.send_message(message.chat.id, f"{'pong' if message.text.find('t') == -1 else 'tost'}\nзатримка: {round(now-message.date,2)} сек\nваш статус: {bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id).status}\n версія: 4.5.8 C")
    information(message)

#stiker
@bot.message_handler(commands=['s'])
def stiker(message):
    bot.send_sticker(message.chat.id , open("PICTURES/N.png", 'rb'))
    information(message)

@bot.message_handler(commands=['start','help'])
def start(message):
    bot.send_message(message.chat.id, "/info - Надсилаю перелік з інформацію про стан у регіонах Україні\n/map - Надсилаю мапу тривог України\n/form - Налаштування надсилання повідомлень про початок або відбій тривоги\n\n<b><a href='https://t.me/+FeZvEeXW5lIzMjYy'>Support Тривога Бот</a>\n<a href='https://t.me/+GCh0rwIVS-tkNmIy'>Пропозиції та звіти помилок</a></b>",parse_mode='html')
    information(message)

@bot.message_handler(commands=['info'])
def info(message):
    #loaded_situation
    loaded = load(open('JSONs/new_situation.json' , "rb"))
    text = f"Станом на {loaded['data']} за Києвом\n\nСитуація у: \n"
    statistic = 0

    for k, x in enumerate(loaded["situation"], start=1):
        if x["alarm"]:
            statistic+=4
            text += f"{k}. <b>{x['stateName']}</b> - 🚨"
        else:
            text += f"{k}. {x['stateName']} - ✅"
        text += timedelta(x['data'])+"\n"
    if statistic:
        text += f"\nНа {statistic}% території України оголошено тривогу!"
    else:
        text += "\n<b>Тривоги немає</b> ✅"

    bot.send_message(message.chat.id, text+"\n\n@YBAGA_bot",parse_mode='html')
    information(message)

@bot.message_handler(commands=['map'])
def map(message):
    bot.send_message(message.chat.id, "Тимчасово не працює.\nАльтернатива - /info")
    return
    #loaded_situation
    loaded = load(open('JSONs/new_situation.json' , "rb"))
    text=f"Станом на {loaded['data']} за Києвом\n\nТривога у:\n"
    k = 0

    for x in loaded["situation"]:
        if not x["alarm"]:
            continue
        k += 1
        text += f"{k}. {x['stateName']}\n"
    if k==0:
        text.replace("Тривога у:","Тривоги немає ✅")

    bot.send_photo(message.chat.id, open("PICTURES/N.png", 'rb'),text+"\n\n@YBAGA_bot",parse_mode='html')
    information(message)

@bot.message_handler(commands=['form'])
def form(message):
    if message.chat.type != "private" and not (status_user(message.from_user.id, message.chat.id) == "creator" or status_user(message.from_user.id, message.chat.id) == "administrator" or status_user(message.from_user.id, message.chat.id) == "left"):
            bot.send_message(message.chat.id, 'Налаштувати надсилання повідомлень у групу про початок або відбій тривоги може тільки <b>автор групи</b> або <b>адмінітратор</b>',parse_mode='html')
            return
    markup = types.InlineKeyboardMarkup()
    for stat in Info:
        if findl(Info[stat],message.chat.id):
            markup.add(types.InlineKeyboardButton(stat+" ✅",callback_data="x"+stat))
        else:
            markup.add(types.InlineKeyboardButton(stat,callback_data=stat))

    markup.add(types.InlineKeyboardButton("Згорнути перелік",callback_data="close"))
    bot.send_message(message.chat.id, 'Надсилати повідомлення, коли тривога буде у:', reply_markup=markup)
    information(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.message.chat.type != "private" and not (status_user(call.from_user.id, call.message.chat.id) == "creator" or status_user(call.from_user.id, call.message.chat.id) == "administrator" or status_user(call.from_user.id, call.message.chat.id) == "left"):
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Взаємодіяти з цим таблом може тільки автор групи або адмінітратор")
                return
            global Info
            if call.message.chat.type != "private" :
                sleep(0.5)
            if call.data == 'close':
                dump(Info, open('JSONs/Info.json', 'w'))
                t = "Повідомлення будуть надходити, коли змінюватиметься ситуація у: "
                k = 1
                for i in Info:
                    if findl(Info[i],call.message.chat.id) :
                        t += f"\n {k}. "+i
                        k += 1
                if k == 1:
                    t = "Повідомлення не будуть надходити"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t, reply_markup=None)
                return
            elif call.data[0] == "x":
                Info[call.data[1::]].remove(call.message.chat.id)
            else:
                Info[call.data].append(call.message.chat.id)

            # remove inline buttons
            markup = types.InlineKeyboardMarkup()
            for stat in Info:
                if findl(Info[stat],call.message.chat.id):
                    markup.add(types.InlineKeyboardButton(stat+" ✅",callback_data="x"+stat))
                else:
                    markup.add(types.InlineKeyboardButton(stat,callback_data=stat))

            markup.add(types.InlineKeyboardButton("Зберегти налаштування ⚙️",callback_data="close"))
            #call.message.from_user.id
            #call.message.chat.id

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=markup)


    except Exception as e1:
        try:
            bot.send_message(965712322, str(e1))
        except Exception as e2:
            print("Bad connection, Telegram API does not work")
            print(e2)
            print()
            print(str(e1))
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Відбувся збій")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Відбувся збій.\nПовторіть спробу, будь ласка')

bot.polling(none_stop=True, interval = 1)
