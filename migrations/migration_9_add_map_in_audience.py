import os
import json

if __name__ == "__main__":
    print("migration 9 is run as a standalone program")
    os.chdir('..')

NEW_KEY= 'Україні (мапа)'
PATH_AUDIENCE= r'data/audience.json'

with open(PATH_AUDIENCE, 'rb') as f:
    audience = json.load(f)

if NEW_KEY in audience:
    print(f"migration 9 completed")
else:
    audience[NEW_KEY] = list()

    with open(PATH_AUDIENCE, 'w') as f:
        json.dump(audience, f)

    print(f"migration 9 done")
