import json
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


def new_sess():
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=50,
        pool_maxsize=50)
    sess.mount('https://air-save.ops.ajax.systems/', adapter)

    return sess

def check_alarm(state_id, sess):
    my_timeout = 10
    my_waiting = 10
    while True:
        try:
            r= sess.get(
                'https://air-save.ops.ajax.systems/api/mobile/status',
                params={'regionId':state_id},
                timeout=my_timeout
            )
        except requests.exceptions.Timeout:
            my_timeout += 10
        except Exception as e:
            make_warning(40, f"Error with data updating. Next try in {my_waiting} sec. {repr(e)}", exc_info=True)
            my_waiting += 10
        else:
            if r.ok:
                time.sleep(1)
                return bool(
                    r.json()["alarms"]
                )
            else:
                my_waiting += 10
                make_warning(40, f"Problem with data updating. Next try in {my_waiting} sec. Code: {r.status_code}. Text: {r.text}")
        time.sleep(my_waiting)

def send_photo(chat_id):
    from_user = types.User(id=chat_id, is_bot=None, first_name=None)
    about_chat = types.Chat(id=chat_id, type=None)

    message = types.Message(message_id=None, from_user= from_user,
        date=None, chat=about_chat, content_type=None,
        options=(), json_string=None)

    _photo.photo(message)

def notifications(good_list, bad_list):
    if not (good_list or bad_list):
        return 0
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
        distribution(audience[state],
            text.format(state=state,
                duration_past_status=duration_past_status
            )
        )

    text= '🚨 '+ date+ '\n<b>У <a href="https://t.me/YBAGA_bot">{state}</a> розпочалася тривога </b> 🚨\nТиша тривала: {duration_past_status}'
    if len(bad_list) > 10:
        text += "\nМожливі пуски ракет з МіГ-31К"

    for state, duration_past_status in bad_list.items():
        distribution(audience[state],
            text.format(state=state,
                duration_past_status=duration_past_status
            )
        )

    audience.save()


LOOP= True

def main():
    global LOOP
    print(f"<{datetime.now().strftime('%x %X')}> update_situatiaon.py started. Waiting 5 sec for main.")
    time.sleep(5)
    print(f"<{datetime.now().strftime('%x %X')}> main of update_situatiaon.py started")

    with open('static/states_info.json' , "rb") as f:
        states_info = tuple(
            json.load(f)
        )

    try:
        with open('data/situation.json' , "rb") as f_read:
            situation = tuple(
                json.load(f_read)
            )
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

    if len(situation)!=len(states_info):
        make_warning(40, f"len of situation IS NOT LIKE len of states_info'.")
        exit(1)

    good_dict = dict()
    bad_dict = dict()

    while LOOP:
        sess = new_sess()
        for num, state in enumerate(states_info):
            print(num)
            situation_num= situation[num]
            new_alarm = check_alarm(state["stateId"], sess)
            if new_alarm==situation_num["alarm"]:
                continue
    #Sorting
            if new_alarm==True:
                bad_dict[state["Name"]
                ]= timedelta(situation_num["date"])
            else:
                good_dict[state["Name"]
                ]= timedelta(situation_num["date"])
    #Synchronization
            situation_num["alarm"]= new_alarm
            situation_num["date"]= int(
                time.time()
            )
    #
        sess.close()
    #Saving the situation
        print("Saving the situation")
        with open('data/situation.json', 'w') as f:
            json.dump(situation, f)
    #
        notifications(good_dict, bad_dict)
    #Memory cleaning
        good_dict.clear()
        bad_dict.clear()
    else:
        return 0

if __name__ == '__main__':
    main()
