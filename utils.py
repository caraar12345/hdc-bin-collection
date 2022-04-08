"""A module that finds the next bin collection dates for a specific address in Market Harborough, UK. Uses the UPRN to find the address."""
from datetime import datetime

from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.fccenvironment.co.uk/harborough/"
BIN_DATA_URL = BASE_URL + "detail-address"

def collect_data(uprn):
    """
    Returns the next collection dates from the bin collection page.

    :param uprn: The UPRN of the address to find the next collection dates for.
    :return: A dictionary containing the bin types that HDC collect as keys, and the next collection dates as values.
    """

    bin_data_site = requests.post(BIN_DATA_URL, data={"Uprn": uprn})
    soup = BeautifulSoup(bin_data_site.content, "html.parser")
    bin_div = soup.select_one(".block-your-next-scheduled-bin-collection-days")
    bin_types = [bin_type.strip()
                for bin_type in bin_div.find_all(text=True)
                if bin_type.parent.name == "li"
                and "green" not in bin_type]
    bin_dates = [datetime.strptime(bin_date.strip() + " @ 07:00", '%d %B %Y @ %H:%M')
                for bin_date in bin_div.find_all(text=True)
                if bin_date.parent.name == "span"
                and "subscribed" not in bin_date]
    return dict(zip(bin_types, bin_dates))

if __name__ == "__main__":
    uprn = input("Enter UPRN: ")
    for key, value in collect_data(uprn).items():
        print(key, value.strftime("%d %B %Y @ %H:%M"))
