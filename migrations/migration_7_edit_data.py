import os
import json

if __name__ == "__main__":
    print("migration 7 is run as a standalone program")
    os.chdir('..')

def renaming_users_to_audience():
    if os.path.exists("data/audience.json"):
        pass
    elif os.path.exists("data/users.json"):
        os.rename(r"data/users.json", r"data/audience.json")
    else:
        old_path = r"data/users.json"
        new_path =  r"data/audience.json"
        raise FileNotFoundError(f"Migration_7 cannot find the file \'{old_path}\' for renaming to \'{new_path}\'")

def edit_data():
    appendage = " \u043e\u0431\u043b\u0430\u0441\u0442\u0456" # " області"
    root = "\u0414\u043d\u0456\u043f\u0440\u043e\u043f\u0435\u0442\u0440\u043e\u0432\u0441\u044c\u043a\u0456" # "Днiпpопетpoвcькі"
    mask = root+appendage
    replacement = root+"\u0439"+appendage #"Днiпpопетpoвcькі"+"й"+" області"

    def edit_audience():
        audience_path = r"data/audience.json"

        if not os.path.exists(audience_path):
            raise FileNotFoundError(f"Migration_7 cannot find the file \'{audience_path}\' for editing")

        with open(audience_path,'rb') as f_read:
            audience = json.load(f_read)

        if mask in audience and replacement not in audience: #double check
            audience[replacement] = audience.pop(mask)
            print(f"correction of \'{audience_path}\' done")
        else:
            print(f"correction of \'{audience_path}\' completed")
            return 0

        with open(audience_path,'w') as f_write:
            json.dump(audience, f_write)

    def edit_situation():
        situation_path = r"data/situation.json"

        if not os.path.exists(situation_path):
            raise FileNotFoundError(f"Migration_7 cannot find the file \'{situation_path}\' for editing")

        fix_name = bool()
        fix_keys = bool()
        OSS = os.stat(situation_path) #os.stat of situation

        with open(situation_path,'rb') as f_read:
            situation = json.load(f_read)

        for state in situation:
            if state["Name"] == mask:
                state["Name"] = replacement
                fix_name = True

            if "data" in state:
                state["date"] = state.pop("data")
                fix_keys = True

        if fix_name or fix_keys:
            print(f"correction of \'{situation_path}\' done")

            with open(situation_path,'w') as f_write:
                json.dump(situation, f_write)

            os.utime(situation_path, times=(OSS.st_atime, OSS.st_mtime))
        else:
            print(f"correction of \'{situation_path}\' completed")

    edit_audience()
    edit_situation()

renaming_users_to_audience()
edit_data()

print("migration_7 finished", end=2*'\n')
