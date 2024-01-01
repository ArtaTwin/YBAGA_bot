import os

if __name__ == "__main__":
    print("migration 5 is run as a standalone program")
    os.chdir('..')

if os.path.exists('data/ban_list.json'):
    print("creating 'ban_list.json' of version 4.6.0 completed")
else:
    try:
        with open('data/ban_list.json', 'w') as f:
            f.write("[]")
            f.close()
        print("migration 5 done")
    except Exception as e:
        print("migration 5 can not do")
        raise os.error("migration 5 can not do\n"+str(e))
        #raise str(e)
