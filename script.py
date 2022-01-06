import requests
import json
import time
import glob
import os

def analysis(card_list_data):
    response = requests.get("https://v6.exchangerate-api.com/v6/0e164fc6317a50745338c53e/latest/USD")
    eur_to_usd = float(response.json()["conversion_rates"]["EUR"])
    output = []
    for item in card_list_data:
        usd = item["prices"]["usd"]
        if usd is None:
            usd = 0
        else:
            usd = float(usd)
        eur = item["prices"]["eur"]
        if eur is None:
            eur = 0
        else:
            eur = float(eur)
        if usd > 2 and eur > 0:
            dif = usd - eur * eur_to_usd
            per_dif_us = 100 * dif/(eur * eur_to_usd)
            if per_dif_us > 100 or dif > 20:
                output.append({
                    "name": item["name"],
                    "usd": usd, 
                    "eur": eur,
                    "eur_in_usd": eur * eur_to_usd,
                    "dif": dif,
                    "percent_dif": per_dif_us,
                    "uri": item["scryfall_uri"]
                    })
    return output

response = requests.get("https://api.scryfall.com/bulk-data")

timestr = time.strftime("%Y%m%d-%H%M%S")
with open("bulk_data/" + timestr + ".json", "w+") as bdf:
    json.dump(response.json(), bdf)

print("Fetched Bulk File....")

bulk_dir = glob.glob("bulk_data/*")
latest_f_name = max(bulk_dir, key=os.path.getctime)

with open(latest_f_name) as lbf:
    data = json.load(lbf)

default_data = data["data"][2]

response = requests.get(default_data["download_uri"])

timestr = time.strftime("%Y%m%d-%H%M%S")
with open("json_bulk/" + timestr + ".json", "w+") as bdf:
    json.dump(response.json(), bdf)

print("Fetched default cards file...")

json_dir = glob.glob("json_bulk/*")
latest_f_name = max(json_dir, key=os.path.getctime)

with open(latest_f_name) as lbf:
    data = json.load(lbf)

print("Running analysis...")

picks = analysis(data)

print("Complete! Now dumping picks...")

timestr = time.strftime("%Y%m%d-%H%M%S")
with open("picks_json/" + timestr + ".json", "w+") as bdf:
    json.dump(picks, bdf)
