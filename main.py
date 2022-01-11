from datetime import datetime
import tools

def main():

    print("Welcome to MTGArbitrage!")
    refresh_mode = True if input("Would you like to [1] refresh existing data or [2] generate new picks?\nEnter 1 or 2\n") == "1" else False
    if refresh_mode:
        print("Refreshing last picks...")
        newest_picks = tools.get_newest_file("output/")
        tools.refresh(newest_picks)
    else:
        min_delta = float(input("Please enter minimum delta value (think price difference of cards between US and EU markets): \n"))
        min_price = float(input("Please enter minimum price (think lowest price for a card in USD in both US and EU markets): \n"))
        max_price = float(input("Please enter maximum price (think highest value for a card in USD in both US and EU markets): \n"))

        current_time = datetime.now()

        #Check if newest bulk reference is stale (older than 12 hours)
        newest_bulk_ref = tools.get_newest_file("bulk_references/")

        if newest_bulk_ref is None or tools.diff_in_hours(current_time, tools.get_file_time(newest_bulk_ref)) > 12:
            if newest_bulk_ref:
                print("Bulk reference is older than 12 hours...")
            print("Fetching new references...")
            newest_bulk_ref = tools.fetch_bulk_reference()
            print("Now fetching new data from scryfall...")
            new_data = tools.fetch_json(newest_bulk_ref)
            print("Now generating new picks...")
            tools.generate_picks(new_data, min_delta, min_price, max_price)
        else:
            print("Data is less than 12 hours old... Making picks off existing data and updating with latest prices")
            new_data = tools.get_newest_file("data/")
            tools.generate_picks(new_data, min_delta, min_price, max_price)  

    print("Complete!")

main()