import os

if __name__ == "__main__":
    print("migration 3 is run as a standalone program")
    os.chdir('..')

if os.path.exists('JSONs'):
    if "Info.json" in os.listdir("JSONs"):
        os.renames('JSONs/Info.json', 'data/users.json')
    if "new_situation.json" in os.listdir("JSONs"):
        os.renames('JSONs/new_situation.json', 'data/situation.json')
    print("migration 3 done")

elif os.path.exists('data'):
    print("renaming of version 4.6.0 completed")

else:
    print("migration 3 can not do")
    raise os.error("migration 3 can not do")
