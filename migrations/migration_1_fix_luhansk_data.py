import json

j = json.load(open('new_situation.json' , "rb"))

j["situation"][10]['data'] = 1649090700

json.dump(j,open('new_situation.json', 'w'))
