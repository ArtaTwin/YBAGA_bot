import json
import random
import time
import traceback
from datetime  import datetime
from pathlib   import Path
from threading import Thread

from PIL       import Image
from pytz      import timezone
from telebot   import TeleBot, types, apihelper

import secret

def updater():
    while True:
        try:
            import update_situation
        except Exception as e:
            report_error(repr(e))
            time.sleep(10)

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

def color(t, alarm):
    score = (time.time()-t)/7200 #one score is two hours

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
    pal=[255 if s=="1" else 20 for s in f"{abs(num):b}"]

    if len(pal)%3:
        for i in range(3-len(pal)%3):
            pal.append(20)

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

def markup_generator(sub_id):
    markup = types.InlineKeyboardMarkup()
    audience.reload()
    for i, SubscriptionOfSubId in enumerate(audience.getSubscriptionsSubId(sub_id)):
        state, subscription_is_available = SubscriptionOfSubId
        markup.add(
            types.InlineKeyboardButton(
                state+(" ✅" if subscription_is_available else ""),
                callback_data=str(
                    (i, subscription_is_available, sub_id) # have to spare memory. 1-64 bytes
                )
            )
        )

    markup.add(types.InlineKeyboardButton("Зберегти налаштування ⚙️", callback_data=str((-1, 0, sub_id)) )) #save and close
    return markup

def get_situation(sub_id):
    if sub_id in ban_list:
        with open(r'static/states_info.json' , "rb") as f:
            states_info = json.load(f)

        situation = [
            {
                "Name"  : state["Name"],
                "alarm" : random.randrange(2),
                "date"  : time.time()-random.randrange(86401)
            }

            for state in tuple(states_info)
        ]
    else:
        with open(r'data/situation.json' , "rb") as f:
            situation = json.load(f)

    return situation

def uncustomizer_chek(chat_id, user_id):
    if chat_id == user_id: #chat.type  == "private"
        return False
    else:
        return not (
            user_id in map(
                lambda admin: admin.user.id,
                bot.get_chat_administrators(chat_id)
            )
            or
            user_id == 1087968824 # anonymous id = 1087968824. Additional information: https://t.me/GroupAnonymousBot
        )

def information(message):
    if security_level:
        bot.send_message(secret.ADMIN_ID, f"""
🔵 {datetime.fromtimestamp(message.date).strftime('%d/%m/%Y %H:%M:%S')}

Ім я: <pre>{message.from_user.first_name}</pre>
Псевдонім: <pre>{message.from_user.username}</pre>
User_id= <pre>{message.from_user.id}</pre>
message_id= {message.message_id}\nlast_name:<pre>{message.from_user.last_name}</pre>
Вид чату: {message.chat.type}\nChat_id = <pre>{message.chat.id}</pre>
text: {message.text}
""",parse_mode='html')

def report_error(RE): #RE = repr(exception)
    FE = traceback.format_exc()
    print(
datetime.now().strftime('\t %x %X'),
"Format exception:",
FE,
"Repr exception:",
RE,
sep="\n", end="\n"*3)

    bot.send_message(secret.ADMIN_ID, f"""
❗️ {datetime.now().strftime('%x %X')}
*ERROR* :
__Format exception__ :
```{FE}```

__Repr exception__ :
```{RE}```
""",
parse_mode='MarkdownV2')
    time.sleep(1)

class Audience(str):
    """
    state: str
    sub_id: int
    subscribers: list[sub_id]
    audience: dict[state:subscribers]
    """

    path = None

    def __init__(self, path):
        self.path = path
        try:
            f_read = open(path, "rb")
            self.__audience  = json.load(f_read)
            f_read.close()
        except Exception as e:
            report_error(repr(e))

            with open(r'static/states_info.json','rb') as f:
                states_info = json.load(f)

            self.__audience = {
                state["Name"] : list()
                for state in states_info
            }

            print("Audience generated without Subscribers")

    def reload(self):
        self.__init__(self.path)

    def addSubId(self, state, sub_id):
        if sub_id not in self.__audience[state]:
            self.__audience[state].append(sub_id)

    def delSubId(self, state, sub_id):
        if sub_id in self.__audience[state]:
            self.__audience[state].remove(sub_id)

    def countSubId(self):
        return {
            sub_id
            for subscribers in self.__audience.values()
            for sub_id in subscribers
        }

    def findSubId(self, sub_id):
        return [
            state
            for state, subscribers in self.__audience.items()
            if sub_id in subscribers
        ]

    def getSubscriptionsSubId(self, sub_id): #get list of subscriptions of SubId
        return [
            (state, sub_id in subscribers)
            for state, subscribers in self.__audience.items()
        ]

    def save(self, path):
        try:
            f_write = open(path, 'w')
            json.dump(self.__audience, f_write)
            f_write.close()
        except Exception as e:
            report_error(repr(e))

bot = TeleBot(secret.TOKEN)

security_level = 1
data_map = {
    "file_id" : str(),
    "version_time" : float()
}

audience = Audience(r"data/audience.json")
with open(r"data/ban_list.json", "rb") as f:
    try:
        ban_list = json.load(f)
    except Exception as e:
        report_error(repr(e))
        ban_list = list()

Thread(target=updater, args=(), daemon=True).start()
bot.send_message(secret.ADMIN_ID, "Trevoga_bot.py started")
print("Trevoga_bot.py started")

@bot.message_handler(commands=['restart', 'r'])
def restart(message):
    if message.from_user.id==secret.ADMIN_ID or message.chat.id==552733968:
        bot.send_message(
            message.chat.id,
            f"{datetime.fromtimestamp(message.date).strftime('%d.%m.%Y %H:%M:%S')}\n Bot start to restart"
        )
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

@bot.message_handler(commands=['cs']) #info of users
def count_sub(message):
    if message.from_user.id==secret.ADMIN_ID:
        audience.reload()
        CSI = audience.countSubId()
        bot.send_message(secret.ADMIN_ID, f"<pre>len: {len(CSI)}</pre>\n\n{CSI}", parse_mode='html')
        with open(r'data/audience.json','rb') as f:
            bot.send_document(secret.ADMIN_ID, f)

@bot.message_handler(commands=['ban', 'b'])
def ban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = message.text[message.text.find("\n"):]
        try:
            id = int(id)
        except ValueError:
            bot.send_message(message.chat.id, "id is not correct\n"+id)
        if id not in ban_list:
            ban_list.append(id)
            with open('data/ban_list.json', 'w') as f:
                json.dump(ban_list, f)
        bot.send_message(message.chat.id, f"user banned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['unban', 'ub'])
def unban_user(message):
    if message.from_user.id==secret.ADMIN_ID:
        id = message.text[message.text.find("\n"):]
        try:
            id = int(id)
        except ValueError:
            bot.send_message(message.chat.id, "id is not correct\n"+id)

        try:
            ban_list.remove(id)
        except ValueError:
            bot.send_message(message.chat.id, "id not found\n"+str(id))
            return

        with open('data/ban_list.json', 'w') as f:
            json.dump(ban_list, f)

        bot.send_message(message.chat.id, f"user unbanned\n<pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['sbl']) #send ban_list
def sbl(message):
    if message.from_user.id==secret.ADMIN_ID:
        bot.send_message(message.chat.id, f"<pre>len: {len(ban_list)}</pre>\n\n{ban_list}", parse_mode='html')

        with open('data/ban_list.json','rb') as f:
            bot.send_document(message.chat.id, f)

@bot.message_handler(commands=['decoder', 'dc'])
def dc(message):
    if message.from_user.id==secret.ADMIN_ID:
        bin, id =decoder(
            message.text[message.text.find("\n"):]
        )
        bot.send_message(message.chat.id, f"bin: <pre>{bin}</pre>\nid: <pre>{id}</pre>", parse_mode='html')

@bot.message_handler(commands=['test','t','ping','p']) #testing
def testing(message):
    bot.send_message(message.chat.id,
        f"""
{'tost' if "t" in message.text else 'pong'}
затримка: {round(time.time()-message.date,2)} сек
ваш статус: {bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id).status}
версія: 4.7.4
        """
    )
    information(message)

@bot.message_handler(commands=['stiker', 's'])
def stiker(message):
    with open('static/map.png' , "rb") as f:
        bot.send_sticker(message.chat.id , f)
    information(message)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(
        message.chat.id,
        """
/info - Надсилаю перелік з інформацію про стан у регіонах Україні
/map - Надсилаю мапу тривог України
/form - Налаштування надсилання повідомлень про початок або відбій тривоги
<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>

<b><a href='https://t.me/+FeZvEeXW5lIzMjYy'>Support Тривога Бот</a>
<a href='https://t.me/+GCh0rwIVS-tkNmIy'>Пропозиції та звіти помилок</a></b>""",
        parse_mode='html',
        disable_web_page_preview= True
    )
    information(message)

@bot.message_handler(commands=['info', 'i'])
def info(message):
    date= datetime.fromtimestamp(
        Path(r'data/situation.json').lstat().st_mtime,
        tz=timezone('Europe/Kiev')
    )
    text= f"Станом на {date.strftime('%d.%m %H:%M')} за Києвом\n\nСитуація у: \n"
    alarm = bool()

    for i, state in enumerate(get_situation(message.from_user.id), start=1):
        if state["alarm"]:
            text+= f"\n{i}. <b>{state['Name']}</b> - 🚨"
            alarm= True
        else:
            text+= f"\n{i}. {state['Name']} - ✅"
        text+= timedelta(state['date'])

    if alarm:
        text+= f'\n\nНа {text.count("🚨")*4}% території України оголошено тривогу!'
    else:
        text+= "\n\n<b>Тривоги немає</b> ✅"

    if security_level:
        text= stenography(text, message.from_user.id)

    text+= "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    bot.send_message(message.chat.id, text, parse_mode='html')
    information(message)

@bot.message_handler(commands=['map', 'm'])
def photo(message):
    situation = get_situation(message.from_user.id)
    situation_mtime= Path(r'data/situation.json').lstat().st_mtime

    text= f"Станом на {datetime.fromtimestamp(situation_mtime, tz=timezone('Europe/Kiev')).strftime('%d.%m %H:%M')} за Києвом\n\n"
    iterator = enumerate(
        filter(
            (lambda x: x["alarm"]),
            situation
        ),
        start=1
    )

    if iterator:
        text+= "Тривога у:\n"
        text+= "\n".join(
            (
                f"{i}. {state['Name']}"
                for i, state in iterator
            )
        )
    else:
        text+= "Тривоги немає ✅\n"
    text+= "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    global data_map
    if data_map["version_time"] == situation_mtime and message.from_user.id not in ban_list and security_level<3:
        bot.send_photo(message.chat.id, data_map["file_id"], text, parse_mode='html')
    else:
        pal = [
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
            255,255,255
        ]

        if security_level < 2:
            maket, stenography_pal = stenography_img(0)
        elif security_level == 2:
            maket, stenography_pal = stenography_img(
                int(time.time())
            )
        else:
            maket, stenography_pal = stenography_img(message.from_user.id)

        image = Image.open("static/map.png")

        image.putpalette(
            [
                primary_color
                for state in situation
                for primary_color in color(state["date"], state["alarm"])
            ]+ pal+ stenography_pal
        )

        image.paste(maket)

        if security_level<3:
            data_map = {
                "file_id" : bot.send_photo(message.chat.id, image, text, parse_mode='html').photo[-2].file_id,
                "version_time" : situation_mtime
            }
        else:
            bot.send_photo(message.chat.id, image, text, parse_mode='html')
    information(message)

@bot.message_handler(commands=['form', 'f'])
def form(message):
    if uncustomizer_chek(message.chat.id, message.from_user.id):
        bot.send_message(message.chat.id,
            'Налаштувати надсилання повідомлень у групу про початок або відбій тривоги може тільки <b>автор групи</b> або <b>адмініcтратор</b>. І бот повинен мати права адмінстратора',
            parse_mode='html'
        )
        return

    if message.reply_to_message:
        a = message.reply_to_message.forward_from_chat

        if a == None or a.type != 'channel':
            bot.send_message(
                message.chat.id,
                "Налаштовувати сповіщення таким чином можна тільки для каналів\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        try:
            bot.get_chat(a.id)
        except apihelper.ApiTelegramException:
            bot.send_message(
                message.chat.id,
                "Бот не знаходится у каналі\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        if uncustomizer_chek(a.id, message.from_user.id):
            bot.send_message(
                message.chat.id,
                "Ви не є адмінстартором цього каналу\n<b><a href='https://t.me/SupYb/24'>Інструкція налаштування для каналів</a></b>",
                parse_mode='html'
            )
            return

        bot.reply_to(
            message.reply_to_message,
            f'Надсилати повідомлення до каналу \'<b>{a.title}</b>\', коли тривога буде у:',
            parse_mode='html',
            reply_markup=markup_generator(a.id)
        )
    else:
        bot.send_message(message.chat.id, 'Надсилати повідомлення, коли тривога буде у:', reply_markup=markup_generator(message.chat.id))
    information(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if uncustomizer_chek(call.message.chat.id, call.from_user.id):
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Взаємодіяти з цією формою може тільки автор групи або адмінітратор")
            time.sleep(1)
            return
        global audience

        i, subscription_is_available, sub_id = eval(call.data)
        if i == -1: #close
            audience.save(r'data/audience.json')
            afsi = audience.findSubId(sub_id) #audience find Sub Id

            if afsi:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text="Повідомлення будуть надходити, коли змінюватиметься ситуація у:\n"+"\n".join([f" {k}. {state}" for k, state in enumerate(afsi,start=1)]),
                reply_markup=None)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                text="Повідомлення не будуть надходити",
                reply_markup=None)
            return

        cmrk = call.message.reply_markup.keyboard[i][0] #OPTIMIZE: link. But I cannot create a link by cmrk.text
        if subscription_is_available:
            cmrk.text = state = cmrk.text[:-2]
            audience.delSubId(cmrk.text, sub_id)
        else:
            audience.addSubId(cmrk.text, sub_id)
            cmrk.text += " ✅"

        cmrk.callback_data= str(
            (i, not subscription_is_available, sub_id)
        )

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Надсилати повідомлення, коли тривога буде у:", reply_markup=call.message.reply_markup)


    except Exception as e:
        report_error(repr(e))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Відбувся збій.\nПовторіть спробу, будь ласка')

bot.polling(none_stop=True, interval = 1)
