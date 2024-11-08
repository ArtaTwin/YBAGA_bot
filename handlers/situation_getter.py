import json
import random
import time

from handlers.BanList_meneger import BanTuple

def get_situation(sub_id):
    bt = BanTuple(r"data/ban_list.json")
    if sub_id in bt:
        with open(r'static/states_info.json' , "rb") as f:
            states_info = json.load(f)

        situation = [
            {
                "Name"  : state["Name"],
                "alarm" : random.randrange(2),
                "date"  : time.time()-random.randrange(86401)
            }

            for state in tuple(states_info)
        ]
    else:
        with open(r'data/situation.json' , "rb") as f:
            situation = json.load(f)

    return situation

def timedelta(t):
    t = time.time()-t
    if t < 120:
        return " 1 хв"
    elif t < 3600:
        return f" {t//60:.0f} хв"
    elif t < 86400:
        return f" {t//3600:.0f} год"
    else:
        return f" {t//86400:.0f} д"
