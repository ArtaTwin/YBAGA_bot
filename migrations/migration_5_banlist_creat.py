import os

if __name__ == "__main__":
    print("migration 4 is run as a standalone program")
    os.chdir('..')

if 'ban_list.json' in os.listdir("data") :
    print("creating 'ban_list.json' of version 4.6.0 completed")
else:
    with open('data/ban_list.json', 'w') as f:
        f.write("[]")
        f.close()
    print("migration 5 done")
