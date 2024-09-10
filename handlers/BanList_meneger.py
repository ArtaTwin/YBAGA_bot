import json

from handlers.error_handler import make_warning


class BanList(list):
    """
    ban_list: [sub_id, ]
    """

    def __init__(self, path):
        try:
            with open(path, "rb") as f_read:
                self.extend(
                    json.load(f_read)
                )
        except Exception as e:
            make_warning(50, f"BanList generated WITHOUT  BANED_USERS. {repr(e)}")

        self.path = path

    def save(self):
        with open(self.path, 'w') as f_write:
            json.dump(self, f_write)

class BanTuple(tuple):
    def __new__(cls, path):
        try:
            with open(path, "rb") as f_read:
                ban_list = tuple(json.load(f_read))
        except Exception as e:
            make_warning(50, f"BanTuple generated WITHOUT  BANED_USERS. {repr(e)}")
            ban_list = tuple()
        return super().__new__(cls, ban_list)

    def __init__(self, path):
        self.path = path

    def reload(self):
        self.__new__(self.path)
