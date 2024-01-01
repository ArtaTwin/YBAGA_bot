from telebot   import TeleBot, types
from json      import load, dump
from PIL       import Image
from datetime  import datetime
from pytz      import timezone
from threading import Thread
from time      import time, sleep
from os        import path
from random    import randint
import secret

bot = TeleBot(secret.TOKEN)
bot.send_message(secret.ADMIN_ID, "Trevoga_bot.py started")
try:
    from migrations import migration_3_renaming, migration_4_situation_edit, migration_5_banlist_creat
except Exception as e:
    bot.send_message(secret.ADMIN_ID, f"{e}\n\n{repr(e)}")

print("Trevoga_bot.py started")
#bot = TeleBot(secret.TOKEN)
security_level = 1
file_id = (str(),float())
try:
    subscribers = load(open("data/users.json", "rb"))
    ban_list = load(open("data/ban_list.json", "rb"))
except Exception as e:
    bot.send_message(secret.ADMIN_ID, str(e1))

def updater():
    import update_situation
Thread(target=updater, args=(), daemon=True).start()
del Thread, updater

def timedelta(t):
    t = time()-t
    if t < 60:
        return " 1 хв"
    if t < 3601:
        return f" {t//60:.0f} хв"
    if t < 86400:
        return f" {t//3600:.0f} год"
    if t > 86399:
        return f" {t//86400:.0f} д"

def color(t,alarm):
    score = (time()-t)/7200 #one score is two hours

    if alarm:
        if score >= 2:
            return (50,0,0)
        elif score >= 1:
            return (100,0,0)
        else:
            return (150,0,0)
    else:
        if score >= 2:
            return (0,120,100)
        elif score >= 1:
            return (0,120,50)
        else:
            return (0,120,0)

def stenography_img(num):
    pal=[255 if s=="1" else 20 for s in f"{int(num):b}"]

    if len(pal)%3:
        for i in range(3-len(pal)%3):
            pal.append(20)

    print(len(pal))
    print(pal)
    maket = Image.new("P", (5 * len(pal)//3,2)) #color=(255,100,255)
    maket.putpalette(pal)
    pixlist = maket.load()

    for i in range(len(pal)//3):
        for a in range(5):
            pixlist[i*5+a,0] = i+36 #tuple(b_list[i*3:(i+1)*3])
            pixlist[i*5+a,1] = i+36
    return (maket, pal)

def stenography(text, num):
    b_list = [s == "1" for s in f"{abs(num):b}"]
    #changes = "12345678"
    changes = "apceoixy"
    targets = "арсеоіху"
    d = dict(zip(targets,changes))
    text = list(text)
    i = int()

    while b_list:
        a = text[i]
        if a in targets and b_list.pop():
            text[i] = d[a]
        i+=1

    return "".join(text)

def decoder(text):
    eng = "apceoixy"
    ukr = "арсеоіху"

    b = str()
    for s in text:
        if s in eng or s in ukr:
            if s in eng:
                b += "1"
            else:
                b += "0"

    return (b, int(b[::-1],2) )

def customizer_chek(chat_id, user_id): #message.chat.id, message.from_user.id
    return bot.get_chat_member(chat_id=chat_id, user_id=user_id).status in ["creator", "administrator", "left"]

def information(message): #for statistics
    if security_level:
        bot.send_message(secret.ADMIN_ID, f"📎🔵\n{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} :\n \nІм я:<pre>{message.from_user.first_name}</pre>\nПсевдонім:<pre>{message.from_user.username}</pre>\nUser_id=<pre>{message.from_user.id}</pre>\nmessage_id={message.message_id}\nlast_name:<pre>{message.from_user.last_name}</pre>\nВид чату:{message.chat.type}\nChat_id = <pre>{message.chat.id}</pre>\nmess: {message.text}",parse_mode='html')
    #print(f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')} /: \nИмя:{message.from_user.first_name} |Псевдоним:{message.from_user.username} |User_id={message.from_user.id} |message_id={message.message_id} |last_name:{message.from_user.last_name} |Тип чата:{message.chat.type} |mess: {message.text}\n")

@bot.message_handler(commands=['restart', 'r'])
def restart(message):
    if message.from_user.id==secret.ADMIN_ID or message.chat.id==552733968:
        bot.send_message(message.chat.id,f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')}\n Bot start to restart")
        #This forces telebot to crash exit. It will be restarted by service script. We tried exit(1), KeyboardInterrup, but they don't work as good as 1/0
        1/0

@bot.message_handler(commands=['su']) #security_level up
def su(message):
    if message.from_user.id==secret.ADMIN_ID:
        global security_level
        security_level+=1
        bot.send_message(message.chat.id, f"safer\nsecurity_level: <pre>{security_level}</pre>", parse_mode='html')

@bot.message_handler(commands=['sd']) #security_level down
def sd(message):
    if message.from_user.id==secret.ADMIN_ID:
        global security_level
        if security_level:
            security_level-=1
        bot.send_message(message.chat.id, f"less safe\nsecurity_level: <pre>{security_level}</pre>", parse_mode='html')

@bot.message_handler(commands=['iu']) #info of users
def inactive_users(message):
    if message.from_user.id==secret.ADMIN_ID:
        s = set()
        for x in subscribers.values():
            for i in x:
                s.add(i)
        bot.send_message(secret.ADMIN_ID, f"<pre>len: {len(s)}</pre>\n\n{s}", parse_mode='html')
        del s
        bot.send_document(secret.ADMIN_ID, open('data/users.json','rb'))

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = message.text[5:]
        try:
            id = int(id)
        except ValueError:
            bot.send_message(message.chat.id, "id is not correct\n"+id)
        if not id in ban_list:
            ban_list.append(id)
            dump(ban_list, open('data/ban_list.json', 'w'))
        bot.send_message(message.chat.id, f"user banned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = message.text[7:]
        try:
            id = int(id)
        except ValueError:
            bot.send_message(message.chat.id, "id is not correct\n"+id)
        try:
            ban_list.remove(id)
        except ValueError:
            bot.send_message(message.chat.id, "id not found\n"+str(id))
            return
        dump(ban_list, open('data/ban_list.json', 'w'))
        bot.send_message(message.chat.id, f"user unbanned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['sbl']) #send ban_list
def sbl(message):
    if message.from_user.id==secret.ADMIN_ID:
        bot.send_message(message.chat.id, f"<pre>len: {len(ban_list)}</pre>\n\n{ban_list}", parse_mode='html')
        bot.send_document(message.chat.id, open('data/ban_list.json','rb'))

@bot.message_handler(commands=['dc']) #decoder
def dc(message):
    if message.from_user.id==secret.ADMIN_ID:
        b, id =decoder( message.text[4:] )
        bot.send_message(message.chat.id, f"bin: <pre>{b}</pre>\nid: <pre>{id}</pre>", parse_mode='html')

#testing
@bot.message_handler(commands=['test','t','ping','p'])
def testing(message):
    bot.send_message(message.chat.id, f"{'pong' if message.text.find('t') == -1 else 'tost'}\nзатримка: {round(time()-message.date,2)} сек\nваш статус: {bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id).status}\n версія: 4.6.0")
    information(message)

@bot.message_handler(commands=['situation'])
def sit(message):
    if message.from_user.id==secret.ADMIN_ID:
        for file in os.listdir("data"):
            bot.send_document(secret.ADMIN_ID, open('data/'+a,'rb'))
#stiker
@bot.message_handler(commands=['s'])
def stiker(message):
    bot.send_sticker(message.chat.id , open('static/map.png' , "rb"))
    information(message)

@bot.message_handler(commands=['start','help'])
def start(message):
    bot.send_message(message.chat.id, "/info - Надсилаю перелік з інформацію про стан у регіонах Україні\n/map - Надсилаю мапу тривог України\n/form - Налаштування надсилання повідомлень про початок або відбій тривоги\n\n<b><a href='https://t.me/+FeZvEeXW5lIzMjYy'>Support Тривога Бот</a>\n<a href='https://t.me/+GCh0rwIVS-tkNmIy'>Пропозиції та звіти помилок</a></b>",parse_mode='html')
    information(message)

@bot.message_handler(commands=['info'])
def info(message):
    #situation_situation
    situation = load(open('data/situation.json' , "rb"))
    if message.from_user.id in ban_list or message.chat.id in ban_list:
        situation = [{"Name" : x["Name"], "alarm" : randint(0,1), "data" : time()-randint(0,86400)} for x in situation]
    text = f"Станом на {datetime.fromtimestamp(path.getmtime('data/situation.json'), tz=timezone('Europe/Kiev')).strftime('%d.%m %H:%M')} за Києвом\n\nСитуація у: \n"
    statistic = 0

    #[(f"{k}. <b>{x['Name']}</b> - 🚨" if x["alarm"] else f"{k}. {x['Name']} - ✅") + timedelta(x['data']) for k, x in enumerate(situation, start=1)]

    for k, x in enumerate(situation, start=1):
        if x["alarm"]:
            statistic+=4
            text += f"{k}. <b>{x['Name']}</b> - 🚨"
        else:
            text += f"{k}. {x['Name']} - ✅"
        text += timedelta(x['data'])+"\n"
    if statistic:
        text += f"\nНа {statistic}% території України оголошено тривогу!"
    else:
        text += "\n<b>Тривоги немає</b> ✅"

    bot.send_message(message.chat.id, (stenography(text, message.from_user.id) if security_level else text) +"\n\n@YBAGA_bot",parse_mode='html')
    information(message)

@bot.message_handler(commands=['map'])
def map(message):
    situation = load(open('data/situation.json' , "rb"))
    if message.from_user.id in ban_list or message.chat.id in ban_list:
        situation = [{"Name" : x["Name"], "alarm" : randint(0,1), "data" : time()-randint(0,86400)} for x in situation]
    text=f"""
Станом на {datetime.fromtimestamp(path.getmtime('data/situation.json'), tz=timezone('Europe/Kiev')).strftime('%d.%m %H:%M')} за Києвом

Тривога у:
"""+"\n".join(
[f"{k}. {x['Name']}" for k, x in enumerate(
filter((lambda a: a["alarm"]), situation),
start=1
)]
)

    if text[-1] == '\n':
        text = text.replace("Тривога у:","Тривоги немає ✅")

    global file_id
    if file_id[-1] == path.getmtime('data/situation.json') and not (message.from_user.id in ban_list or message.chat.id in ban_list) and security_level<3:
        bot.send_photo(message.chat.id, file_id[0] ,text+"\n@YBAGA_bot",parse_mode='html')
    else:
        pal = list()
        if security_level ==2:
            maket, pal = stenography_img(time())
        if security_level ==3:
            maket, pal = stenography_img(message.from_user.id)

        image = Image.open("static/map.png")
        image.putpalette([c for x in situation for c in color(x["data"], x["alarm"])]+ [
        150,0,0,
        100,0,0,
        50,0,0,
        0,120,0,
        0,120,50,
        0,120,100,
        0,0,0,
        30,30,30,
        100,100,100,
        130,130,130,
        255,255,255, #
]+ pal)

        if security_level>1:
            image.paste(maket)
        if security_level<3:
            file_id = (bot.send_photo(message.chat.id, image, text+"\n\n@YBAGA_bot",parse_mode='html').photo[-2].file_id, path.getmtime('data/situation.json'))
        else:
            bot.send_photo(message.chat.id, image, text+"\n\n@YBAGA_bot",parse_mode='html').photo[-2].file_id, path.getmtime('data/situation.json')
    information(message)

@bot.message_handler(commands=['form'])
def form(message):
    if message.chat.type != "private" and not customizer_chek(message.chat.id, message.from_user.id):
            bot.send_message(message.chat.id, 'Налаштувати надсилання повідомлень у групу про початок або відбій тривоги може тільки <b>автор групи</b> або <b>адмінітратор</b>',parse_mode='html')
            return
    markup = types.InlineKeyboardMarkup()
    for stat in subscribers:
        if message.chat.id in subscribers[stat]:
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
            if call.message.chat.type != "private" and not customizer_chek(call.message.chat.id, call.from_user.id):
                bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Взаємодіяти з цією формою може тільки автор групи або адмінітратор")
                return
            global subscribers
            if call.message.chat.type != "private" :
                sleep(0.5)
            if call.data == 'close':
                dump(subscribers, open('data/users.json', 'w'))
                t = "Повідомлення будуть надходити, коли змінюватиметься ситуація у: "
                k = 1
                for i in subscribers:
                    if call.message.chat.id in subscribers[i]:
                        t += f"\n {k}. "+i
                        k += 1
                if k == 1:
                    t = "Повідомлення не будуть надходити"
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t, reply_markup=None)
                return
            elif call.data[0] == "x":
                subscribers[call.data[1::]].remove(call.message.chat.id)
            else:
                subscribers[call.data].append(call.message.chat.id)

            # remove inline buttons
            markup = types.InlineKeyboardMarkup()
            for stat in subscribers:
                if call.message.chat.id in subscribers[stat]:
                    markup.add(types.InlineKeyboardButton(stat+" ✅",callback_data="x"+stat))
                else:
                    markup.add(types.InlineKeyboardButton(stat,callback_data=stat))

            markup.add(types.InlineKeyboardButton("Зберегти налаштування ⚙️",callback_data="close"))
            #call.message.from_user.id
            #call.message.chat.id

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=markup)


    except Exception as e1:
        try:
            bot.send_message(secret.ADMIN_ID, str(e1))
        except Exception as e2:
            print("Bad connection, Telegram API does not work")
            print(e2)
            print()
            print(str(e1))
        bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Відбувся збій")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Відбувся збій.\nПовторіть спробу, будь ласка')

bot.polling(none_stop=True, interval = 1)
