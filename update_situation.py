import json
import threading
import time
import urllib.request
from datetime import datetime

from pytz     import timezone
from telebot  import TeleBot, types, apihelper#, util

import secret
from handlers.Audience_meneger import Audience
from handlers.BanList_meneger import BanTuple
from handlers.error_handler import *
from functions_reqwest import _photo


def check(state_id):
    timeout = 10
    while True:
        try:
            request_urlopen= urllib.request.urlopen(
                f'https://air-save.ops.ajax.systems/api/mobile/status?regionId={state_id}'
            )
            return request_urlopen.read() != b'{"alarms":[]}'
        except Exception as e:

            if timeout> 50: #total: 150
                make_warning(40, f"Problem with request. Timeout: {timeout}s.", exc_info=True)

            e = str(e)
            tuple_exception_example = (
                '<urlopen error [Errno 16] Device or resource busy>',
                'HTTP Error 504: Gateway Time-out',
                'HTTP Error 403: Forbidden'
            )

            for exception_example in tuple_exception_example:
                if exception_example in e:
                    time.sleep(timeout)
                    timeout += 10
                    break
            else:
                make_warning(40, f"I cannot make a request. {repr(e)}", exc_info=True)

def notifications(good_list, bad_list):
    audience = Audience(r'data/audience.json')
    ban_tuple = BanTuple(r'data/ban_list.json')
    photo_sub = audience['Україні (мапа)'].copy()
    bot = TeleBot(secret.TOKEN)
    start= str()
    end= str()

    def distribution(subscribers, send_text):
        for sub_id in subscribers:
            if sub_id in ban_tuple:
                continue
            try:
                #util.antiflood(bot.send_message, chat_id=sub_id, text= send_text, parse_mode= 'html')
                bot.send_message(sub_id, send_text, parse_mode= 'html')
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

    start= f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b><a href="https://t.me/YBAGA_bot">'
    end= '</a></b> відбій тривоги ✅'

    for state in good_list:
        text = start+state+end
        distribution(subscribers= audience[state], send_text= text)


    start= f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У <a href="https://t.me/YBAGA_bot">'
    end= '</a> розпочалася тривога </b> 🚨'
    if len(bad_list) > 12:
        end += "\nМожливі пуски ракет з МіГ-31К"

    for state in bad_list:
        text = start+state+end
        distribution(subscribers= audience[state], send_text= text)

    audience.save()

def send_photo(chat_id):
    from_user = types.User(id=chat_id, is_bot=None, first_name=None)
    about_chat = types.Chat(id=chat_id, type=None)

    message = types.Message(message_id=None, from_user= from_user,
        date=None, chat=about_chat, content_type=None,
        options=(), json_string=None)
    _photo.photo(message, 0)

def main():
    print(f"<{datetime.now().strftime('%x %X')}> update_situatiaon.py started. Waiting 5 sec for main.")
    time.sleep(5)
    print(f"<{datetime.now().strftime('%x %X')}> main of update_situatiaon.py started")

    def N(x, state_info): #!!! rename
        alarm_state = check(state_info["stateId"])
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


    while True:

        good_list = list()
        bad_list = list()
        list_threads=[
            threading.Thread(target=N, args=values)
            for values in enumerate(states_info)
        ]

        for thread in list_threads:
            thread.start()

        for thread in list_threads:
            thread.join()

        with open('data/situation.json', 'w') as f:
            json.dump(situation, f)

        if good_list or bad_list:
            notifications(good_list, bad_list)

        time.sleep(20)

if __name__ == '__main__':
    main()
