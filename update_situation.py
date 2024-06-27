import sys
import json
import time
import urllib.request
from datetime import datetime
import threading

from telebot  import TeleBot, types, apihelper
from pytz     import timezone

import secret
from functions_reqwest.handlers.audience_module import Audience
from functions_reqwest.handlers.reporter_error import *
from functions_reqwest import _photo

def chek(state_id):
    timeout = 10
    while True:
        try:
            # "urlopen(...).length != 13" 2*10**(-8) sec faster
            return urllib.request.urlopen(f'https://air-save.ops.ajax.systems/api/mobile/status?regionId={state_id}').read() != b'{"alarms":[]}'
        except Exception as e:

            if timeout> 50: #total: 150
                handlers.report_error(repr(e)) #!!!

            e = str(e)
            tuple_exception_example = (
                '<urlopen error [Errno 16] Device or resource busy>',
                'HTTP Error 504: Gateway Time-out',
                'HTTP Error 403: Forbidden'
            )

            for exception_example in tuple_exception_example:
                if exception_example in e:
                    print("chek sleep:", timeout)
                    time.sleep(timeout)
                    timeout += 10
                    break

def distribution(subscribers, func, **kwargs):
     for sub_id in subscribers:
         try:
             func(chat_id=sub_id, **kwargs)
         except apihelper.ApiTelegramException as e:
             e = str(e)
             tuple_exception_example = (
                 "Error code: 403",
                 "Error code: 400. Description: Bad Request: chat not found",
                 "Error code: 400. Description: Bad Request: group chat was upgraded to a supergroup chat"
             )
             for exception_example in tuple_exception_example:
                 if exception_example in e:
                     audience.cleen_SubId(sub_id)
                     bot.send_message(secret.ADMIN_ID, f"id removed <pre>{sub_id}</pre>", parse_mode='html')
                     break
             else:
                 bot.send_message(secret.ADMIN_ID, f"sub_id was <pre>{sub_id}</pre>", parse_mode='html')
                 if 0 > sub_id:
                     bot.leave_chat(sub_id)

def notifications(_states, alarm):
    if alarm:
        start, end = f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У ', ' розпочалася тривога </b> 🚨'
        if len(_states) > 12: #MiG-31K
            end += "\nМожливі пуски ракет з МіГ-31К"
    else:
        start, end = f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b>', '</b> відбій тривоги ✅'

    end += "\n\n<b><a href='https://t.me/YBAGA_bot'>YBAGA_bot</a></b>"

    for state in _states:
        text = start+state+end
        distribution(
            subscribers= audience.get_Subscribers(state),
            func= bot.send_message,
            text= text,
            parse_mode= 'html'
        )

def send_photo(chat_id):
    from_user = types.User(id=chat_id, is_bot=None, first_name=None)
    about_chat = types.Chat(id=chat_id, type=None)

    message = types.Message(message_id=None, from_user= from_user,
        date=None, chat=about_chat, content_type=None,
        options=(), json_string=None)
    _photo.photo(message, 0)

def N(x, state_info): #!!! rename
    alarm_state = chek(state_info["stateId"])
    state_situation = situation[x]
    if alarm_state == state_situation["alarm"]:
        return

    state_situation["alarm"] = alarm_state
    state_situation["date"] = int(time.time())
    if alarm_state:
        bad_list.append(state_info["Name"])
    else:
        good_list.append(state_info["Name"])

time.sleep(5)

bot = TeleBot(secret.TOKEN)

print(f"<{datetime.now().strftime('%x %X')}> update_situatiaon.py started")

while True:
    #initialization
    with open('static/states_info.json' , "rb") as f:
        states_info = tuple(json.load(f))

    try:
        with open('data/situation.json' , "rb") as f:
            situation = tuple(json.load(f))
    except Exception as e:
        handlers.report_error(repr(e)) #!!!
        situation = [
            {
                "Name": state["Name"],
                "alarm": False,
                "date": int(time.time())
            }
            for state in states_info
        ]

    #making of update
    good_list = list()
    bad_list = list()

    t=time.time()
    list_threads=[
        threading.Thread(target=N, args=values)
        for values in enumerate(states_info)
    ]

    for thread in list_threads: #start
        thread.start()

    for thread in list_threads: #wait
        thread.join()

    print(time.time()-t)
    with open('data/situation.json', 'w') as f:
        json.dump(situation, f)

    del states_info, situation, list_threads

    #notifications to users
    if good_list or bad_list:
        audience = Audience(r'data/audience.json')

        notifications(good_list, False)
        notifications(bad_list, True)

        audience.save()

        distribution(
            subscribers= audience.get_Subscribers('Україні (мапа)'),
            func= send_photo,
        )

        del good_list, bad_list, audience

        time.sleep(15)
    else:
        time.sleep(20)
