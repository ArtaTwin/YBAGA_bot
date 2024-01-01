import os

if __name__ == "__main__":
    print("migration 4 is run as a standalone program")
    os.chdir('..')

with open('data/situation.json', 'r') as f:
    situation = f.read()
    f.close()

if situation.find("stateName") != -1:
    situation = situation.replace("stateName", "Name")
    with open('data/situation.json', 'w') as f:
        f.write(situation)
        f.close()
    print("migration 4 done")

elif situation.find("stateName") == -1 and situation.find("Name") != -1:
    print("situation.json edit of version 4.6.0 completed")

else:
    print("migration 4 can not do")
    raise os.error("migration 4 can not do")
