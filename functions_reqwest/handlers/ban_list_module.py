import json
from functions_reqwest.handlers.reporter_error import report_error

__all__ = ['Ban_list']

class Ban_list(list):
    """
    ban_list: [sub_id, ]
    """

    def __new__(cls, path, edit_mode=False):
        try:
            f_read = open(path, "rb")
            new_ban_list = json.load(f_read)
            f_read.close()
        except Exception as e:
            report_error(repr(e))
            new_ban_list = list()
            print("Ban_list generated WITHOUT  BANED_USERS")
        return super().__new__(cls, new_ban_list)

    def __init__(self, path, edit_mode=False):
        self.edit_mode = edit_mode
        self.path = path

    def add_ui(self, user_id):
        if not self.edit_mode:
            print("Ban_list() was initialized not in edit-mode. Addition is not possible", end = 2*'\n')
            return

        if user_id not in self:
            self.append(user_id)
        return

    def del_ui(self, user_id):
        if not self.edit_mode:
            print("Ban_list() was initialized not in edit-mode. Deletion is not possible", end = 2*'\n')
            return

        self.remove(user_id)

    def save(self):
        if not self.edit_mode:
            print("Ban_list() was initialized not in edit-mode. Saving is not possible", end = 2*'\n')
            return

        try:
            f_write = open(self.path, 'w')
            json.dump(self, f_write)
            f_write.close()
        except Exception as e:
            report_error(repr(e))
        return
