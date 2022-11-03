from urllib.request import urlopen
from json           import load, dump
from PIL            import Image
from datetime       import datetime
from time           import time, sleep
from pytz           import timezone
from telebot        import TeleBot
from traceback      import format_exc
import secret

from migrations import migration_1_fix_luhansk_data

print("update_situatiaon.py started")

bot = TeleBot(secret.TOKEN)
inactive_users = set()

def chek(x):
    #False if ok
    try:
        return urlopen(f'https://air-save.ops.ajax.systems/api/mobile/status?regionId={x}').read(12) != b'{"alarms":[]'
    except Exception as e:
        print("\n", datetime.now().strftime("%x %X"), ">>> Maybe bad internet connection. Error`s name is :\n", repr(e))
        print("program stopped to 20 seconds...")
        sleep(20)
        return chek(x)

def color(t,alarm):
    score = (int(time())-t)//7200 #one score is two hours. score = [0;2]
    if score>1: #2 or more
        return (50,0,0) if alarm else (0,120,100)
    if score == 1: #1
        return (100,0,0) if alarm else (0,120,50)
    if score<0: #result cannot be negative
        bot.send_message(965712322, f'Прийнято {score}. t1 = {int(time())}, t2 = {t}') #sending about flaw, score = min, 0
    return (150,0,0) if alarm else (0,120,0) #if score == 0

def draw(color,coordinat):
    global pixlist
    pixels,next_pixels = {tuple(coordinat)}, set()
    while pixels:
        for i in pixels:
            for n in ((-1,0),(1,0),(0,-1),(0,1)) :
                if pixlist[i[0]+n[0],i[1]+n[1]] == (255,0,255):
                    next_pixels.add((i[0]+n[0],i[1]+n[1]))
                    pixlist[i[0]+n[0],i[1]+n[1]] = color
        pixels,next_pixels = next_pixels, set()

while True:
    try:

        #load
        try:
            situation = load(open('JSONs/new_situation.json' , "rb"))["situation"]
        except Exception as e:
            print(e)
            situation = [
                {"stateName": "Вінницька область", "alarm": False, "data" : 0},
                {"stateName": "Волинська область", "alarm": False, "data" : 0},
                {"stateName": "Дніпропетровська область", "alarm": False, "data" : 0},
                {"stateName": "Донецька область", "alarm": False, "data" : 0},
                {"stateName": "Житомирська область", "alarm": False, "data" : 0},
                {"stateName": "Закарпатська область", "alarm": False, "data" : 0},
                {"stateName": "Запорізька область", "alarm": False, "data" : 0},
                {"stateName": "Івано-Франківська область", "alarm": False, "data" : 0},
                {"stateName": "Київська область", "alarm": False, "data" : 0},
                {"stateName": "Кіровоградська область", "alarm": False, "data" : 0},
                {"stateName": "Луганська область", "alarm": False, "data" : 0},
                {"stateName": "Львівська область", "alarm": False, "data" : 0},
                {"stateName": "Миколаївська область", "alarm": False, "data" : 0},
                {"stateName": "Одеська область", "alarm": False, "data" : 0},
                {"stateName": "Полтавська область", "alarm": False, "data" : 0},
                {"stateName": "Рівненська область", "alarm": False, "data" : 0},
                {"stateName": "Сумська область", "alarm": False, "data" : 0},
                {"stateName": "Тернопільська область", "alarm": False, "data" : 0},
                {"stateName": "Харківська область", "alarm": False, "data" : 0},
                {"stateName": "Херсонська область", "alarm": False, "data" : 0},
                {"stateName": "Хмельницька область", "alarm": False, "data" : 0},
                {"stateName": "Черкаська область", "alarm": False, "data" : 0},
                {"stateName": "Чернівецька область", "alarm": False, "data" : 0},
                {"stateName": "Чернігівська область", "alarm": False, "data" : 0},
                {"stateName": "м. Київ", "alarm": False, "data" : 0}
            ]
        statsM = load(open('JSONs/stats-M.json' , "rb"))
        image = Image.open("PICTURES/O.png").convert('RGB')
        pixlist = image.load()
        good_list = []
        bad_list = []
        new = False

        for x in range(25):
            statsM_x = statsM[x]
            if (chek_x := chek(statsM_x["stateId"])) != situation[x]["alarm"] :
                new = True
                if chek_x:
                    situation[x]["alarm"] = True
                    bad_list.append(statsM_x["stateName"])
                else:
                    situation[x]["alarm"] = False
                    good_list.append(statsM_x["stateName"])
                situation[x]["data"] = int(time())
            draw(color(situation[x]["data"], chek_x), statsM_x["coordinat"])

        maket = Image.open('PICTURES/L.png')
        image.paste(maket, (0, 0), maket)
        image.save("PICTURES/N.png")

        #clearing RAM
        del statsM_x, chek_x, image, pixlist, statsM, maket

        #save
        with open('JSONs/new_situation.json', 'w') as f:
            dump({"data":datetime.now(tz=timezone("Europe/Kiev")).strftime("%d.%m %H:%M"), "situation":situation}, f)

        #clearing RAM
        del situation

        #notifications to users
        if new:
            Info = load(open('JSONs/Info.json' , "rb"))

            for stat in good_list:
                for user_id in Info[stat]:
                    try:
                        bot.send_message(user_id, f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b>{stat}</b> відбій тривоги ✅', parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)

            for stat in bad_list:
                for user_id in Info[stat]:
                    try:
                        bot.send_message(user_id, f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У {stat} розпочалася тривога</b> 🚨',parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)

            bot.send_message(965712322, f"🔴 <pre>len : {len(inactive_users)}</pre>\n\n {inactive_users}",parse_mode='html')

        #clearing RAM
        del good_list, bad_list, new
    except Exception as e1:
        print(e1)
        var = format_exc()
        print(var)
        try:
            bot.send_message(965712322, str(e1)+"\n\n"+var)
        except Exception as e2:
            print("Bad connection, Telegram API does not work")
            print(e2)
    sleep(30)
