import os
import json

if __name__ == "__main__":
    print("migration 8 is run as a standalone program")
    os.chdir('..')

with open(r"data/audience.json") as f_audience, open(r"static/states_info.json") as f_states:
    audience = json.load(f_audience)
    states_info = json.load(f_states)

states_names = [state["Name"] for state in states_info]
audience_names = list(audience.keys())

if states_names == audience_names:
    print(f"migration 8 completed")
else:
    new_audience = {
        sn : audience[sn]
        for sn in states_names
    }

    with open(r"data/audience.json", "w") as f_audience:
        json.dump(new_audience, f_audience)

    print(f"migration 8 done")
