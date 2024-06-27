import os
import json

from .reporter_error import report_error

__all__ = ['Audience']

class Audience(dict):
    """
    state: str
    audience: dict{state:subscribers,}
    """

    def __init__(self, path):
        print("Initialization Audience")

#        if not os.access(path, os.R_OK):
#            raise FileNotFoundError(f"File \'{path}\' cannot read")
#
#        if not os.access(path, os.W_OK):
#            print(f"File \'{path}\' cannot rewrite")
#
        self.path = path

        try:
            f_read = open(path, 'rb')
            new_audience = json.load(f_read)
            f_read.close()

            for key, value in new_audience.items():
                self[key] = value
        except Exception as e:
            reporter_error.report_error(repr(e))

            with open(r'static/states_info.json','rb') as f:
                states_info = json.load(f)
                state_names = (state["Name"] for state in states_info)

            for key in state_names:
                self[key] = list()

            self["send map"] = list()

            print("Audience generated WITHOUT  SUBSCRIBERS")

    def add_SubId(self, state, sub_id):
        if sub_id not in self[state]:
            self[state].append(sub_id)

    def get_Subscribers(self, state):
        return self[state]

    def del_SubId(self, state, sub_id):
        if sub_id in self[state]:
            self[state].remove(sub_id)

    def cleen_SubId(self, sub_id):
        for state in self:
            self.del_SubId(state, sub_id)

    def all_SubId(self):
        return {
            sub_id
            for subscribers in self.values()
            for sub_id in subscribers
        }

    def find_SubId(self, sub_id): #get list of available subscriptions of SubId
        return [
            state
            for state, subscribers in self.items()
            if sub_id in subscribers
        ]

    def get_SubscriptionsOfSubId(self, sub_id): #get list of subscriptions of SubId
        return [
            (state, sub_id in subscribers)
            for state, subscribers in self.items()
        ]

    def reload(self):
        self.__init__(self.path)

    def save(self):
        try:
            f_write = open(self.path, 'w')
            json.dump(self, f_write)
            f_write.close()
        except Exception as e:
            report_error(repr(e))
