import json
import threading
import time
from datetime import datetime

import requests
from pytz     import timezone
from telebot  import TeleBot, types, apihelper, util

import secret
from handlers.Audience_meneger import Audience
from handlers.BanList_meneger import BanTuple
from handlers.error_handler import *
from functions_reqwest import _photo


def check(state_id):
    my_timeout = 10
    while True:
        try:
            r= requests.get(
                'https://air-save.ops.ajax.systems/api/mobile/status',
                params={'regionId':state_id},
                headers={'Connection': 'close'},
                timeout=my_timeout
            )
        except requests.exceptions.Timeout:
            my_timeout += 10
        except Exception as e:
            make_warning(40, f"Error with data updating. {repr(e)}", exc_info=True)
        else:
            if r.ok:
                return bool(
                    r.json()["alarms"]
                )
            elif my_timeout < 60:
                make_warning(30, f"Problem with data updating. Code: {r.status_code}. Text: {r.text}")
                my_timeout += 10
            else: #total: 210 sec waiting
                make_warning(40, f"Problem with data updating. Code: {r.status_code}. Text: {r.text}")
                return None

def notifications(good_list, bad_list):
    audience = Audience(r'data/audience.json')
    photo_sub = audience['Україні (мапа)'].copy()
    ban_tuple = BanTuple(r'data/ban_list.json')
    date = datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")
    bot = TeleBot(secret.TOKEN)
    text = str()

    def distribution(subscribers, send_text):
        for sub_id in subscribers:
            if sub_id in ban_tuple:
                continue
            try:
                util.antiflood(bot.send_message, chat_id= sub_id, text= send_text,
                    parse_mode= 'html', disable_web_page_preview= True
                )
                if sub_id in photo_sub:
                    send_photo(sub_id)
                    photo_sub.remove(sub_id)
            except apihelper.ApiTelegramException as e:
                e = str(e)
                tuple_exception_example = (
                    "Error code: 403",
                    "Error code: 400. Description: Bad Request: chat not found",
                    "Error code: 400. Description: Bad Request: group chat was upgraded to a supergroup chat"
                )
                for exception_example in tuple_exception_example:
                    if exception_example in e:
                        audience.del_SubId(sub_id)
                        bot.send_message(secret.ADMIN_ID, f"id removed <pre>{sub_id}</pre>", parse_mode='html')
                        break
                else:
                    bot.send_message(secret.ADMIN_ID, f"sub_id was <pre>{sub_id}</pre>", parse_mode='html')
                    if 0 > sub_id:
                        bot.leave_chat(sub_id)
            except Exception as e:
                make_warning(40, f"Error with notifications. {repr(e)}", exc_info=True)

    text= '✅ '+ date+ '\nУ <b><a href="https://t.me/YBAGA_bot">{state}</a></b> відбій тривоги ✅'

    for state in good_list:
        distribution(subscribers= audience[state],
            send_text= text.format(state=state)
        )

    text= '🚨 '+ date+ '\n<b>У <a href="https://t.me/YBAGA_bot">{state}</a> розпочалася тривога </b> 🚨'
    if len(bad_list) > 10:
        text += "\nМожливі пуски ракет з МіГ-31К"

    for state in bad_list:
        distribution(subscribers= audience[state],
            send_text= text.format(state=state)
        )

    audience.save()

def send_photo(chat_id):
    from_user = types.User(id=chat_id, is_bot=None, first_name=None)
    about_chat = types.Chat(id=chat_id, type=None)

    message = types.Message(message_id=None, from_user= from_user,
        date=None, chat=about_chat, content_type=None,
        options=(), json_string=None)
    _photo.photo(message)

def main():
    print(f"<{datetime.now().strftime('%x %X')}> update_situatiaon.py started. Waiting 5 sec for main.")
    time.sleep(5)
    print(f"<{datetime.now().strftime('%x %X')}> main of update_situatiaon.py started")

    def N(x, state_info): #!!! rename
        alarm_state = check(state_info["stateId"])
        if alarm_state == None:
            return

        state_situation = situation[x]
        if alarm_state == state_situation["alarm"]:
            return

        state_situation["alarm"] = alarm_state
        state_situation["date"] = int(time.time())
        if alarm_state:
            bad_list.append(state_info["Name"])
        else:
            good_list.append(state_info["Name"])


    with open('static/states_info.json' , "rb") as f:
        states_info = tuple(json.load(f))

    try:
        with open('data/situation.json' , "rb") as f_read:
            situation = tuple(json.load(f_read))
    except Exception as e:
        make_warning(30, f"Problem with loadding of \'data/situation.json\'. {repr(e)}")
        situation = [
            {
                "Name": state["Name"],
                "alarm": False,
                "date": int(time.time())
            }
            for state in states_info
        ]

    good_list = list()
    bad_list = list()

    while True:
        list_threads= [
            threading.Thread(target=N, args=values)
            for values in enumerate(states_info)
        ]

        for thread in list_threads:
            thread.start()

        for thread in list_threads:
            thread.join(timeout=240.0)

        list_threads.clear()

        with open('data/situation.json', 'w') as f:
            json.dump(situation, f)

        if good_list or bad_list:
            notifications(good_list, bad_list)

            good_list.clear()
            bad_list.clear()

        time.sleep(20)

if __name__ == '__main__':
    main()
