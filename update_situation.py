from urllib.request import urlopen
from json           import load, dump
from PIL            import Image
from datetime       import datetime
from time           import time, sleep
from pytz           import timezone
from telebot        import TeleBot
from traceback      import format_exc
from threading      import Thread
import secret

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
    return (150,0,0) if alarm else (0,120,0) #if score == 0

def draw(color,coordinat):
    pixels,next_pixels = {tuple(coordinat)}, set()
    while pixels:
        for i in pixels:
            for n in ((-1,0),(1,0),(0,-1),(0,1)) :
                if pixlist[i[0]+n[0],i[1]+n[1]] == (255,0,255):
                    next_pixels.add((i[0]+n[0],i[1]+n[1]))
                    pixlist[i[0]+n[0],i[1]+n[1]] = color
        pixels,next_pixels = next_pixels, set()

def sr(x): #State Research
    statsM_x = statsM[x]
    chek_x = chek(statsM_x["stateId"])
    if chek_x != situation[x]["alarm"]:
        gb_lists[chek_x].append(statsM_x["stateName"])
        situation[x]["alarm"] = chek_x
        situation[x]["data"] = int(time())
    draw(color(situation[x]["data"], chek_x), statsM_x["coordinat"])
    global done
    done+=1


while True:
    try:

        #load
        try:
            situation = load(open('JSONs/new_situation.json' , "rb"))["situation"]
        except Exception as e:
            print(e)

            situation = [{"stateName": i, "alarm": False, "data" : int(time())} for i in [
            'Вінницькій області', 'Волинській області', 'Дніпропетровські області', 'Донецькій області', 'Житомирській області', 'Закарпатській області', 'Запорізькій області', 'Івано-Франківській області', 'Київській області', 'Кіровоградській області', 'Луганській області', 'Львівській області', 'Миколаївській області', 'Одеській області', 'Полтавській області', 'Рівненській області', 'Сумській області', 'Тернопільській області', 'Харківській області', 'Херсонській області', 'Хмельницькій області', 'Черкаській області', 'Чернівецькій області', 'Чернігівській області', 'м. Києві'
            ]]

        statsM = load(open('JSONs/stats-M.json' , "rb"))
        image = Image.open("PICTURES/O.png").convert('RGB')
        pixlist = image.load()
        gb_lists = ( [], [] ) #good + bad lists = ( [good], [bad] )
        done = 0

        for i in range(25):
            Thread(target=sr, args=[i], daemon=True).start()

        while done < 25:
            sleep(0.05)

        del done

        maket = Image.open('PICTURES/L.png')
        image.paste(maket, (0, 0), maket)
        image.save("PICTURES/N.png")

        #clearing RAM
        del image, pixlist, statsM, maket

        #save
        with open('JSONs/new_situation.json', 'w') as f:
            dump({"data":datetime.now(tz=timezone("Europe/Kiev")).strftime("%d.%m %H:%M"), "situation":situation}, f)

        #clearing RAM
        del situation

        #notifications to users
        if bool(gb_lists[0]) or bool(gb_lists[1]):
            Info = load(open('JSONs/Info.json' , "rb"))

            for stat in gb_lists[0]: #good
                for user_id in Info[stat]:
                    try:
                        bot.send_message(user_id, f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b>{stat}</b> відбій тривоги ✅', parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)

            for stat in gb_lists[1]: #bad
                for user_id in Info[stat]:
                    try:
                        bot.send_message(user_id, f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У {stat} розпочалася тривога </b> 🚨',parse_mode='html')
                    except Exception as e:
                        if 'A request to the Telegram API was unsuccessful. Error code: 403. Description: Forbidden: bot was blocked by the user' == str(e):
                            inactive_users.add(user_id)
            del Info

            bot.send_message(965712322, f"🔴 <pre>len : {len(inactive_users)}</pre>\n\n {inactive_users}",parse_mode='html')

        #clearing RAM
        del gb_lists
    except Exception as e1:
        print(e1)
        var = format_exc()
        print(var)
        try:
            bot.send_message(965712322, str(e1)+"\n\n"+var)
        except Exception as e2:
            print("Bad connection, Telegram API does not work")
            print(e2)
    sleep(60)
