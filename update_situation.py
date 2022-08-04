from urllib.request import urlopen
from json           import load, dump
from PIL            import Image
from datetime       import datetime
from time           import time, sleep
from pytz           import timezone
from telebot        import TeleBot
print("update_situatiaon.py started")

bot = TeleBot('5126680353:AAEBPAGPSNfb-_g-yxBdEd7Ku3vtdP0mbBM')

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
    if (x := (int(time())-t)//7200) > 2:
        return (50,0,0) if alarm else (0,120,100)
    elif x == 0 or x == 1:
        return (150,0,0) if alarm else (0,120,0)
    elif x == 2:
        return (100,0,0) if alarm else (0,120,50)
    raise ValueError(f'Прийнято {x}. t1 = {t1}, t2 = {t2}')

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
    #load
    situation = load(open('new_situation.json' , "rb"))["situation"]
    statsM = load(open('stats-M.json' , "rb"))
    image = Image.open("O.png").convert('RGB')
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

    maket = Image.open('L.png')
    image.paste(maket, (0, 0), maket)
    image.save("N.png")

    #clearing RAM
    del statsM_x, chek_x, image, pixlist, statsM, maket

    #save
    data = "Станом на " +datetime.now(tz=timezone("Europe/Kiev")).strftime("%d.%m %H:%M")+" за Києвом\n\n"
    with open('new_situation.json', 'w') as f:
        dump({"data":data, "situation":situation}, f)

    #clearing RAM
    del situation

    #notifications to users
    if new:
        Info = load(open('Info.json' , "rb"))

        for stat in good_list:
            for user_id in Info[stat]:
                bot.send_message(user_id, f"У {statsM_x_name} закінчилася тривога",parse_mode='html')

        for stat in bad_list:
            for user_id in Info[stat]:
                bot.send_message(user_id, f"У {statsM_x_name} почалася тривога",parse_mode='html')

    #clearing RAM
    del good_list, bad_list, new

    sleep(30)
