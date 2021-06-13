import pandas as pd
import re
from pathlib import Path

#takes a string with 3 letter currency code followed by amount in millions
#return float of number in thousands
#converts couple of hard-coded non-EURO currencies in the set
def convert_currency(amount):

    number = 1000 * float(re.search(r'\s(\d+\.\d+)', amount).group(1))

    currency = amount[:3]
    if currency != "EUR":
        if currency == "BOB":
            conv = 8.3725
        elif currency == "DKK":
            conv = 7.4374
        elif currency == "GEL":
            conv = 3.8279
        elif currency == "INR":
            conv = 88.6972
        elif currency == "JOD":
            conv = 0.8585
        elif currency == "KES":
            conv = 130.5909
        elif currency == "LKR":
            conv = 239.5998
        elif currency == "NGN":
            conv = 498.8897
        elif currency == "NPR":
            conv = 142.5807
        elif currency == "TRY":
            conv = 10.1572
        elif currency == "USD":
            conv = 1.2108
        elif currency == "ZAR":
            conv = 16.6102
        else:
            print("warning, non-defined currency in dataset")
            conv = 1

        number = number / conv

    return number

def check_search_term(description, search_terms):
    for term in search_terms:
        if term in description:
            return True
    return False

#Reading the data
folder = Path("scrapeddata")
file_to_open = folder / "fmo.csv"
cols = pd.read_csv(file_to_open, sep=",", nrows=1).columns
df = pd.read_csv(file_to_open, sep=",", usecols=cols[:6]) #Leave out couple of empty columns at end of file

#add a column with converted amounts in EUR as numbers
df["EUR_amounts"] = [convert_currency(amount) for amount in df["amount"]]

#Test investments for being other fund rather than direct
search_terms = ["fund", "vehicle"]
df["fund"] = [check_search_term(description, search_terms) for description in df["description"]]

#Test economic inclusion
search_terms = ["inclusive", "inclusion", "empowerment", "microfinance", "smallholder", "ineqaulity"]
df["inclusion"] = [check_search_term(description, search_terms) for description in df["description"]]

#Test climate
search_terms = ["green", "renewable", "climate", "sustainable"]
df["climate"] = [check_search_term(description, search_terms) for description in df["description"]]

#Test gender
search_terms = ["gender", "female", "women"]
df["gender"] = [check_search_term(description, search_terms) for description in df["description"]]

#Test human rights
search_terms = ["equal rigths", "human rights", "justice"]
df["human_rights"] = [check_search_term(description, search_terms) for description in df["description"]]

#Test economic growth
search_terms = ["economic growth"]
df["economic_growth"] = [check_search_term(description, search_terms) for description in df["description"]]

print(df['gender'])
