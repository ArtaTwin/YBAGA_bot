import os
import json

from handlers.error_handler import make_warning


class Audience(dict):
    """
    state: str
    audience: dict{state:subscribers,}
    """
    def __init__(self, path):
        #print("Initialization Audience")
        def emergency_load():
            with open(r'static/states_info.json','rb') as f:
                states_info = json.load(f)

            self.update(
                [
                    (state["Name"], [])
                    for state in states_info
                ]
            )
            self['Україні (мапа)'] = list()

            make_warning(40, "Audience generated WITHOUT  SUBSCRIBERS")

        if not (os.path.exists(path) and os.path.isfile(path)):
            make_warning(30, f"Initialization of Audience. File \'{path}\' not exists or not file")
            self.path = os.path.dirname(path)+"/emergency_load_audience.json"
            emergency_load()
            return

        if not os.access(path, os.R_OK):
            make_warning(50, f"Initialization of Audience. File \'{path}\' cannot read")
            self.path = os.path.dirname(path)+"/emergency_load_audience.json"
            emergency_load()
            return

        with open(path, 'rb') as f_read:
            loaded_audience= json.load(f_read)
        self.update(
            loaded_audience.items()
        )

        if not os.access(path, os.W_OK):
            make_warning(40, f"Initialization of Audience. File \'{path}\' cannot rewrite")
            path = os.path.dirname(path)+"/new_audience.json"

        self.path= path
    def del_SubId(self, sub_id):
        for state in self:
            if sub_id in self[state]:
                self[state].remove(sub_id)

    def all_SubId(self):
        return {
            sub_id
            for subscribers in self.values()
            for sub_id in subscribers
        }

    def get_subscriptions(self, sub_id):
        return [
            state
            for state, subscribers in self.items()
            if sub_id in subscribers
        ]

    def reload(self):
        self.__init__(self.path)

    def save(self):
        with open(self.path, 'w') as f_write:
            json.dump(self, f_write)
