#lowest log /2065760/
#kimo = 76561197992327511
#deity = 76561198076020012
#july 8th 2018 = 1530997200 unix timestamp
from functools import wraps
from time import sleep, time
import shutil
import json
import os
import requests
import converter as steamid #stolen lmao

if os.path.exists("logs"):
    pass
else:
    os.mkdir("logs")

if os.path.exists("LIST.txt"):
    os.remove("LIST.txt")
else:
    pass

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print(f'Function {f.__name__} took {te-ts:2.4f} seconds')
        return result
    return wrap

players = input("Enter steamID64 or multiple separated by a comma for context: ")

@timing
def sort_response():
    data = requests.get(f"https://logs.tf/api/v1/log?limit=10000&player={players}").json()
    logs = []
    
    sorted_logs = [element for element in data['logs'] if element['id'] >= 2065760 and element['players'] >= 17 and ("+" or ":" not in element['map'])]
    
    open("logs.json", "w").write(
        json.dumps(sorted_logs, sort_keys=True, indent=4, separators=(',', ': '))
    )

    with open('logs.json', 'r') as f:
        data = json.load(f)
        for key in data:
            logs.append(f"http://logs.tf/json/{key['id']}")

    return logs

@timing
def get_logs():
    logs = sort_response()
    counter = 0
    for link in logs:
        counter += 1
        print(f"Downloading log: {counter}/{len(logs)}")
        data = requests.get(link).json()
        with open(f"logs/log{link[20:28]}.json", 'w') as file:
            json.dump(data, file, sort_keys=True, indent=4, separators=(',', ': '))
        sleep(0.2)

@timing
def sort_logs():
    player_id = steamid.to_steamID3(f"{players[:17]}")
    player_id2 = steamid.to_steamID3(f"{players[:-18]}")
    log_dir = "logs"

    result = []

    for file in os.listdir(log_dir):
        log = os.path.join(log_dir, file)
        with open (log, 'r') as f:
            data = json.load(f)
            if data["players"][f"{player_id}"]["team"] == data["players"][f"{player_id2}"]["team"] and data["info"]["map"]:
                killstreak = [element for element in data["killstreaks"] if element['steamid'] == player_id and element["streak"] >= 4 and element["time"] > 0]
                if killstreak:
                    result.append(f"https://logs.tf/{log[8:15]}#{steamid.to_steamID64(player_id)} : {killstreak[0]['streak']} kills at {killstreak[0]['time']*66}")
    return result

@timing
def result():
    data = sort_logs()
    with open("LIST.txt", "w") as f:
        for line in data:
            f.write(line+"\n")
    os.remove("logs.json")
    shutil.rmtree("logs")

get_logs()
sort_response()
result()