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
from handlers.situation_getter import timedelta

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100)
sess.mount('https://air-save.ops.ajax.systems', adapter)

def check_alarm(state_id):
    my_timeout = 10
    my_waiting = 10
    while True:
        try:
            r= sess.get(
                'https://air-save.ops.ajax.systems/api/mobile/status',
                params={'regionId':state_id},
                timeout=my_timeout
            )
            sess.close()
        except requests.exceptions.Timeout:
            my_timeout += 10
        except Exception as e:
            make_warning(40, f"Error with data updating. Next try in {my_waiting} sec. {repr(e)}", exc_info=True)
            my_waiting += 10
        else:
            if r.ok:
                return bool(
                    r.json()["alarms"]
                )
            elif my_waiting < 120:
                my_waiting += 10
                make_warning(30, f"Problem with data updating. Next try in {my_waiting} sec. Code: {r.status_code}. Text: {r.text}")
            else: #total: 210 sec waiting
                make_warning(40, f"Problem with data updating. Code: {r.status_code}. Text: {r.text}")
                return None
        finally:
            time.sleep(my_waiting)

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

    text= '✅ '+ date+ '\nУ <b><a href="https://t.me/YBAGA_bot">{state}</a></b> відбій тривоги ✅\nТривога тривала: {duration_past_status}'

    for state, duration_past_status in good_list.items():
        distribution(subscribers= audience[state],
            send_text= text.format(state=state, duration_past_status=duration_past_status)
        )

    text= '🚨 '+ date+ '\n<b>У <a href="https://t.me/YBAGA_bot">{state}</a> розпочалася тривога </b> 🚨\nТиша тривала: {duration_past_status}'
    if len(bad_list) > 10:
        text += "\nМожливі пуски ракет з МіГ-31К"

    for state, duration_past_status in bad_list.items():
        distribution(subscribers= audience[state],
            send_text= text.format(state=state, duration_past_status=duration_past_status)
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
        alarm_state = check_alarm(state_info["stateId"])
        if alarm_state == None:
            return

        state_situation = situation[x]
        if alarm_state == state_situation["alarm"]:
            return

        duration_past_status = timedelta(state_situation["date"])

        state_situation["alarm"] = alarm_state
        state_situation["date"] = int(time.time())
        if alarm_state:
            bad_list[state_info["Name"]] = duration_past_status
        else:
            good_list[state_info["Name"]] = duration_past_status


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

    good_list = dict() #!!! rename
    bad_list = dict() #!!! rename

    while True:
        list_threads= [
            threading.Thread(target=N, args=values, daemon=True)
            for values in enumerate(states_info)
        ]

        for thread in list_threads:
            thread.start()

        for thread in list_threads:
            thread.join(timeout=300.)

        sess.close()
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
