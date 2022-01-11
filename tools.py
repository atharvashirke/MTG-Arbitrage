from datetime import datetime
import time
import glob
import requests
import json
import os

def get_exchange_rate(from_currency, to_currency):
    """
    Given two currencies, returns a float representing
    the exchange rate. 
        Parameters:
            from_currency (string): abbreviated currency to exchange [ex:"USD"]
            to_currency (string): abbreviated currency after conversion [ex: "EUR"]
        Returns:
            exchange_rate (float): rate of exchange for from_currency:to_currency
    """
    response = requests.get("https://v6.exchangerate-api.com/v6/0e164fc6317a50745338c53e/latest/" + from_currency)
    exchange_rate = float(response.json()["conversion_rates"][to_currency])
    return exchange_rate
    

def make_picks(card_list_data, min_delta, min_price, max_price):
    """
    Given a list of card objects, return a list of objects (picks)
    with arbitrage opportunities.
        Parameters:
            card_list_data (list): list of card objects fetched from Scryfall API
            min_delta (float): minimum price difference between markets
            min_price (float): minimum price of card in all markets (in USD)
            max_price(float): maximum price of card in all markets (in USD)
        Returns:
            picks (list): list of objects representing arbitrage picks.
    """
    picks = []
    eur_to_usd = get_exchange_rate("EUR", "USD")
    
    for item in card_list_data:
        usd_price = float(item["prices"]["usd"]) if item["prices"]["usd"] else 0
        eur_price = float(item["prices"]["eur"]) if item["prices"]["eur"] else 0
        eur_price_in_usd = eur_price * eur_to_usd if eur_price else 0

        if usd_price > min_price and eur_price_in_usd > min_price:
            if usd_price < max_price and eur_price_in_usd < max_price:
                if min_delta <= abs(usd_price - eur_price_in_usd):
                    picks.append({
                        "name": item["name"],
                        "set": item["set"],
                        "set_name": item["set_name"],
                        "usd": usd_price, 
                        "eur": eur_price,
                        "eur_in_usd": eur_price_in_usd,
                        "delta": abs(usd_price - eur_price_in_usd),
                        "percent_dif": 100 * abs(usd_price - eur_price_in_usd)/eur_price_in_usd,
                        "uri": item["scryfall_uri"]
                    })
    
    return picks

def write_time_file(dir_path_str, content, ftype=".json"):
    """
    Writes a timestamped file to the given directory.
        Parameters:
            dir_path_str (string): string path of file to write
            ftype (string): string file suffix
            content (string): content to write to file
        Returns:
            path (string): path of written file
    """
    timestr = time.strftime("%Y%m%d-%H%M%S")
    path = dir_path_str + timestr + ftype
    with open(path, "w+") as bdf:
        if ftype == ".json":
            json.dump(content, bdf)
        else:
            bdf.write(content)
    return path

def get_newest_file(dir_path_str, ftype=""):
    """
    Finds and returns path to newest file in given directory.
        Paramaters:
            dir_path_str (string): string path of file to write
            ftype (string): file suffix to filter search
        Returns:
            newest_file (string): path of newest file in dir
    """
    cur_dir = glob.glob(dir_path_str + "*" + ftype)
    if len(cur_dir) > 0:
        newest_file = max(cur_dir, key=os.path.getctime)
        return newest_file
    else:
        return None

def get_file_time(file_path):
    """
    Finds and returns creation time of files timestamped
    with write_time_file. 
        Parameters:
            file_path (string): string file path 
        Returns:
            file_date (datetime object): time file was created
    """
    file_path = file_path.split("/", 1)[1].split(".", 1)[0]
    file_date = datetime.strptime(file_path, "%Y%m%d-%H%M%S")
    return file_date

def diff_in_hours(time1, time2):
    """
    Finds and returns the difference between
    two datetimes in hours.
        Parameters:
            time1 (datetime object): End time
            time2 (datetime object): Start time
        Returns:
            hours (int): difference in hours
    """
    hours = (time1 - time2).total_seconds() / 3600
    return int(hours)

def fetch_bulk_reference():
    """
    Fetch a new file of bulk data references
    from the scryfall API
        Parameters:
            None
        Returns:
            bulk_ref_path (string): string path of created file
    """
    response = requests.get("https://api.scryfall.com/bulk-data")
    return write_time_file("bulk_references/", response.json())


def fetch_json(bulk_file_path, uri_type=2):
    """
    Given a bulk data reference file, download
    bulk json data from select uri.
        Parameters:
            bulk_file_path (string): target bulk file path
            uri_type (int): int representing download uri type
        Returns:
            json_path (string): path of produced json
    """
    with open(bulk_file_path) as bdf:
        data = json.load(bdf)["data"][uri_type]
    
    response = requests.get(data["download_uri"])
    print("Fetched new json bulk file...")
    return write_time_file("data/", response.json())

def generate_picks(json_file_path, min_delta, min_price, max_price):
    """
    Given a json data file, analyze
    the data and create a new picks file
        Parameters: 
            json_file_path (string): target json file path
            min_delta (float): minimum price difference between markets
            min_price (float): minimum price of card in all markets (in USD)
            max_price(float): maximum price of card in all markets (in USD)
        Returns:
            picks_path (string): path of generated file
    """
    with open(json_file_path) as df:
        data = json.load(df)
    filters = {"min_delta": min_delta, "min_price": min_price, "max_price": max_price}
    output = {"search_filters": filters, "picks": make_picks(data, min_delta, min_price, max_price)}
    print("Complete! Now dumping picks...")
    return write_time_file("output/", output)

def refresh(picks_file_path):
    """
    Given a picks json file, create a new 
    picks file with updated values for each
    of the original picks with API calls
        Parameters:
            picks_file_path (string): path of target picks json file
        Returns:
            new_pick_data (string): path of refreshed pick data
    """
    with open(picks_file_path) as df:
        content = json.load(df)

    filters = content["search_filters"]
    data = content["picks"]
    
    multi_requests = False
    identifiers = []
    for pick in data:
        identifiers.append({"name": pick["name"], "set": pick["set"]})

    if len(identifiers) > 75:
        multi_requests = True
        temp = []
        while len(identifiers) > 75:
            temp.append(identifiers[0:75])
            identifiers = identifiers[75:]
        temp.append(identifiers)
        identifiers = temp
    
    if multi_requests:
        multi_response = []
        for query_set in identifiers:
            try:
                query = {"identifiers": query_set}
                response = requests.post("https://api.scryfall.com/cards/collection", json=query)
            except requests.exceptions.HTTPError as err:
                SystemExit(err)
            multi_response.extend(response.json()["data"])
            response = multi_response
    else:
        try:
            query = {"identifiers": identifiers}
            response = requests.post("https://api.scryfall.com/cards/collection", json=query)
            response = response.json()["data"]

        except requests.exceptions.HTTPError as err:
            SystemExit(err)
    
    new_data_path = write_time_file("refresh_data/", response)
    return generate_picks(new_data_path, filters["min_delta"], filters["min_price"], filters["max_price"])