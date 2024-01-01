import os
import json

if __name__ == "__main__":
    print("migration 6 is run as a standalone program")
    os.chdir('..')

try:
    situation = json.load(open('data/situation.json' , "rb"))
    if len(situation) ==2:
        situation = situation["situation"]
        with open('data/situation.json', 'w') as f:
            json.dump(situation, f)
            f.close()
        print("migration 6 done")
    else:
        print("situation.json reformation of version 4.6.0 completed")
except Exception as e:
    print("migration 6 can not do")
    raise os.error("migration 6 can not do")
