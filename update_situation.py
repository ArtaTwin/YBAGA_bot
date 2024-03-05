import json
import time
import traceback
import urllib.request
from datetime import datetime

from telebot  import TeleBot, apihelper
from pytz     import timezone

import secret

def report_error(RE): #repr(exception)
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
_Format exception_ :
```{FE}```

_Repr exception_ :
```{RE}```
""",
parse_mode='Markdown') #MarkdownV2
    time.sleep(1)

def chek(state_id):
    timeout = 10
    while True:
        try:
            return urllib.request.urlopen(f'https://air-save.ops.ajax.systems/api/mobile/status?regionId={state_id}').length != 13
        except Exception as e:
            report_error(repr(e))
            e = str(e)
            if '<urlopen error [Errno 16] Device or resource busy>' in e or 'HTTP Error 504: Gateway Time-out' in e or 'HTTP Error 403: Forbidden' in e:
                time.sleep(timeout)
                timeout += 10

def notifications(_states, alarm):
    if alarm:
        start, end = f'🚨 {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\n🚨<b>У ', ' розпочалася тривога </b> 🚨'
        if len(_states) > 12: #MiG-31K
            end += "\nМожливі пуски ракет з МіГ-31К"
    else:
        start, end = f'✅ {datetime.now(tz=timezone("Europe/Kiev")).strftime("%H:%M %d.%m")}\nУ <b>', '</b> відбій тривоги ✅'

    for state in _states:
        text = start+state+end
        for sub_id in audience.getSubscribers(state):
            try:
                bot.send_message(sub_id, text, parse_mode='html')
            except apihelper.ApiTelegramException as e:
                e = str(e)
                tuple_exception_example = (
                    "Error code: 403",
                    "Error code: 400. Description: Bad Request: chat not found",
                    "Error code: 400. Description: Bad Request: group chat was upgraded to a supergroup chat"
                )
                for exception_example in tuple_exception_example:
                    if exception_example in e:
                        audience.cleenSubId(sub_id)
                        bot.send_message(secret.ADMIN_ID, f"id removed <pre>{sub_id}</pre>", parse_mode='html')
                        break
                else:
                    report_error(repr(e))

class Audience(str):
    """
    state: str
    sub_id: int
    subscribers: list[sub_id]
    audience: dict[state:subscribers]
    """

    changed = bool()

    def __init__(self, path):
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

    def getSubscribers(self, state):
        return tuple(self.__audience[state])

    def delSubId(self, state, sub_id):
        if sub_id in self.__audience[state]:
            self.__audience[state].remove(sub_id)

    def cleenSubId(self, sub_id):
        for state in self.__audience:
            self.delSubId(state, sub_id)

    def save(self, path):
        if not self.changed:
            return
        try:
            f_write = open(path, 'w')
            json.dump(self.__audience, f_write)
            f_write.close()
        except Exception as e:
            report_error(repr(e))

time.sleep(5)

bot = TeleBot(secret.TOKEN)
print("update_situatiaon.py started")

while True:
    try:
        #initialization
        with open('static/states_info.json' , "rb") as f:
            states_info = tuple(json.load(f))

        try:
            with open('data/situation.json' , "rb") as f:
                situation = tuple(json.load(f))
        except Exception as e:
            report_error(repr(e))
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

        #making of update
        t = time.time()
        for state_situation, state in zip(situation, states_info, strict=True):
            alarm_state = chek(state["stateId"])
            if alarm_state == state_situation["alarm"]:
                continue
            state_situation["alarm"] = alarm_state
            state_situation["date"] = int(time.time())
            if alarm_state:
                bad_list.aalarm_stateppend(state["Name"])
            else:
                good_list.append(state["Name"])

        print(time.time()-t)
        with open('data/situation.json', 'w') as f:
            json.dump(situation, f)

        del states_info, situation, state, state_situation, alarm_state

        #notifications to users
        if good_list or bad_list:
            audience = Audience(r'data/audience.json')

            notifications(good_list, False)
            notifications(bad_list, True)

            audience.save(r'data/audience.json')

            del good_list, bad_list, audience

            time.sleep(15)
        else:
            time.sleep(20)

    except Exception as e:
        report_error(repr(e))
        time.sleep(10)
