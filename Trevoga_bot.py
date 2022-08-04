from telebot   import TeleBot, types
from json      import load, dump
from datetime  import datetime
from threading import Thread
from time      import time
5

bot = TeleBot('5126680353:AAEBPAGPSNfb-_g-yxBdEd7Ku3vtdP0mbBM')
flag = True

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
        return f" {t//172800} д"

def information(message):
    None
    if flag:
        bot.send_message(965712322, f"📎🔵\n{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} :\n \nИмя:<pre>{message.from_user.first_name}</pre>\nПсевдоним:<pre>{message.from_user.username}</pre>\nUser_id=<pre>{message.from_user.id}</pre>\nmessage_id={message.message_id}\nlast_name:<pre>{message.from_user.last_name}</pre>\nТип чата:{message.chat.type}\nmess: {message.text}",parse_mode='html')
    #print(f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} /: \nИмя:{message.from_user.first_name} |Псевдоним:{message.from_user.username} |User_id={message.from_user.id} |message_id={message.message_id} |last_name:{message.from_user.last_name} |Тип чата:{message.chat.type} |mess: {message.text}\n")

@bot.message_handler(commands=['if'])
def InfoFile(message):
    if message.chat.id==965712322:
        s = set()
        for x in load(open('Info.json','rb')).values():
            for i in x:
                s.add(i)
        bot.send_message(965712322, int(len(s)))
        del s
        bot.send_document(965712322, open('Info.json','rb'))

@bot.message_handler(commands=['start','help'])
def start(message):
    information(message)
    bot.send_message(message.chat.id, "/info - Надсилаю список з інформацію\n/map - Надсилаю мапу України\n/form - Надсилаю форму\n\n не працюю у группах",parse_mode='html')

@bot.message_handler(commands=['f'])
def f(message):
    if message.chat.id==965712322:
        global flag
        flag = flag == False
        bot.send_message(965712322,str(flag))

@bot.message_handler(commands=['info'])
def info(message):

    information(message)
    text = "Ситуація по Україні : \n"
    statistic = 0
    k = 0
    loaded = load(open('new_situation.json' , "rb"))
    for x in loaded["situation"]:
        k += 1
        if x["alarm"]:
            statistic+=100
            text += f" {k}. <b>{x['stateName']}</b> - 🚨"
        else:
            text += f" {k}. {x['stateName']} - ✅"
        text += timedelta(x['data'])+"\n"
    if statistic==0:
        text += "\n<b>Тривоги немає ✅</b>"
    else:
        text += f"\nНа {statistic//25}% території України оголошено тривогу!"
    bot.send_message(message.chat.id, loaded["data"]+text,parse_mode='html')

@bot.message_handler(commands=['map'])
def map(message):

    information(message)
    text="Тривога у:\n"
    k = 0
    loaded = load(open('new_situation.json' , "rb"))
    for x in loaded["situation"]:
        if not x["alarm"]:
            continue
        k += 1
        text += f" {k}. {x['stateName']}\n"
    if k==0:
        text = "Тривоги немає ✅"

    bot.send_photo(message.chat.id, open("N.png", 'rb'),loaded["data"]+text)

@bot.message_handler(commands=['form'])
def k(message):
    global Info
    Info = load(open('Info.json' , "rb"))
    markup = types.InlineKeyboardMarkup()

    for stat in Info:
        if findl(Info[stat],message.from_user.id):
            markup.add(types.InlineKeyboardButton(stat+" ✅",callback_data="x"+stat))
        else:
            markup.add(types.InlineKeyboardButton(stat,callback_data=stat))

    markup.add(types.InlineKeyboardButton(" ЗАКРИТИ ПЕРЕЛІК ",callback_data="stop"))
    bot.send_message(message.chat.id, 'Надсилати повідомлення, коли тривога буде у:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            global Info
            if call.data == 'stop':
                with open('Info.json', 'w') as f:
                    dump(Info, f)
                t = "Повідомлення будуть надходити, коли змінюватиметься ситуація у: "
                for i in Info:
                    if findl(Info[i],call.from_user.id) :
                        t += "\n"+i
                if len(t) == 64:
                    t = "Повідомлення не будуть надходити"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t, reply_markup=None)
                return
            elif call.data[0] == "x":
                Info[call.data[1::]].remove(call.from_user.id)
            else:
                Info[call.data].append(call.from_user.id)

            # remove inline buttons
            markup = types.InlineKeyboardMarkup()
            for stat in Info:
                if findl(Info[stat],call.from_user.id):
                    markup.add(types.InlineKeyboardButton(stat+" ✅",callback_data="x"+stat))
                else:
                    markup.add(types.InlineKeyboardButton(stat,callback_data=stat))

            markup.add(types.InlineKeyboardButton(" ЗАКРИТИ ПЕРЕЛІК ",callback_data="stop"))
            #call.message.from_user.id
            #call.message.chat.id

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=markup)


    except Exception as e:

        print("\n", datetime.now().strftime("%x %X"), ">>> Maybe program was restarted. Error`s name is :\n", repr(e))
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Відбувся збій")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Відбувся збій.\nПовторіть спробу, будь ласка, знов')

bot.polling(none_stop=True, interval = 1)
