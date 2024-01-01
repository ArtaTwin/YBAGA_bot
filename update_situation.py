from urllib.request import urlopen
from json           import load, dump
from datetime       import datetime
from time           import time, sleep
from pytz           import timezone
from telebot        import TeleBot
from traceback      import format_exc
import secret
sleep(5)

print("update_situatiaon.py started")


bot = TeleBot(secret.TOKEN)
inactive_users = set()

def sur(text): # str to url-format
    text = str(text.encode('utf-8'))[2:-1]
    for a,b in ((r"\x","%"),("\n","%0A"),(" ","%20")):
        text = text.replace(a, b)
    return text

def chek(x):
    time_sleep = 40
    while True:
        try:
            return urlopen(f'https://air-save.ops.ajax.systems/api/mobile/status?regionId={x}').read(12) != b'{"alarms":[]'
        except Exception as e:
            var = format_exc()
            try:
                urlopen(f"https://api.telegram.org/bot{secret.TOKEN}/sendMessage?chat_id={secret.ADMIN_ID}&text={datetime.now().strftime('%x+%X')}%0AError:{e}%0A%0Avar:{var}")
            except Exception:
                print("Bad connection, Telegram API does not work")
            print("\n", datetime.now().strftime("%x %X"), ">>> Maybe bad internet connection. Error`s name is :\n", repr(e))
            if str(e) == '<urlopen error [Errno 16] Device or resource busy>' or str(e) == 'HTTP Error 504: Gateway Time-out' or str(e) == 'HTTP Error 403: Forbidden':
                sleep(time_sleep)
                time_sleep += 5
                bot.send_message(secret.ADMIN_ID, f"{datetime.now().strftime('%x %X')}\nerorr completed")
            else:
                time_sleep = 40
            sleep(20)

while True:
    try:
        #load
        try:
            situation = load(open('data/situation.json' , "rb"))
        except Exception as e:
            print(e)
            situation = [{"Name": state["Name"], "alarm": False, "data" : int(time())} for state in load(open('static/states-info.json' , "rb"))]

        good_list = list()
        bad_list = list()

        for situation_x, state in zip( situation, load(open('static/states-info.json' , "rb")) ):
            chek_x = chek(state["stateId"])
            if chek_x == situation_x["alarm"]:
                continue
            situation_x["alarm"] = chek_x
            situation_x["data"] = int(time())
            if chek_x:
                bad_list.append(state["Name"])
            else:
                good_list.append(state["Name"])

        #save
        with open('data/situation.json', 'w') as f:
            dump(situation, f)
            f.close()

        #clearing RAM
        del situation, situation_x, state, chek_x

        #notifications to users
        if good_list or bad_list:
            users = load(open('data/users.json' , "rb"))

            for state in good_list: #good
                for user_id in users[state]:
                    try:
                        bot.send_message(user_id, f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b>{state}</b> відбій тривоги ✅', parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)
                        else:
                            print(str(e))
                            bot.send_message(secret.ADMIN_ID, str(e))

            if len(bad_list) > 12:
                add = "\nМожливі пуски ракет з МіГ-31К"
            else:
                add = str()

            for state in bad_list: #bad
                for user_id in users[state]:
                    try:
                        bot.send_message(user_id, f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У {state} розпочалася тривога </b> 🚨'+add,parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)
                        else:
                            print(str(e))
                            bot.send_message(secret.ADMIN_ID, str(e))
            #clearing RAM
            del users, good_list, bad_list

            bot.send_message(secret.ADMIN_ID, f"🔴 <pre>len : {len(inactive_users)}</pre>\n\n {inactive_users}",parse_mode='html') #for statistics
            sleep(15)
        else:
            sleep(20)
    except Exception as e1:
        var = format_exc()
        try:
            bot.send_message(secret.ADMIN_ID, f"{datetime.now().strftime('%x %X')}\nError:{e1}\n\nvar:{var}")
        except Exception as e2:
            print("Bad connection, Telegram API does not work")
            print(e2)
        sleep(10)
