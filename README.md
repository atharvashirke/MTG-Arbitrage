
# MTG Arbitrage

Utilizing card pricing data from multiple international sellers, MTG Arbitrage automatically generates "picks" of cards with large differences in price across markets after currency conversion. Using this tool, users can identify cards that are profitable to import/export.


## Installation

Clone the repo and run the following.

```bash
cd MTG-Arbitrage
python3 main.py
```
    

## Usage/Examples

```
Welcome to MTGArbitrage!
Would you like to [1] refresh existing data or [2] generate new picks?
Enter 1 or 2
>>> 2
Please enter minimum delta value (think price difference of cards between US and EU markets): 
>>> 10
Please enter minimum price (think lowest price for a card in USD in both US and EU markets): 
>>> 5
Please enter maximum price (think highest value for a card in USD in both US and EU markets):
>>> 100
Bulk reference is older than 12 hours...
Fetching new references...
Now fetching new data from scryfall...
Fetched new json bulk file...
Now generating new picks...
Complete! Now dumping picks...
Complete! 
```

JSON output with stored picks will be available in the output directory generated by the script. To ensure responsible API usage, the script will run subsequent searches on local bulk data until the rate limit has been exhausted.
