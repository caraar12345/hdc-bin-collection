"""A module that finds the next bin collection dates for a specific address in Market Harborough, UK. Uses the UPRN to find the address."""
from datetime import datetime

from bs4 import BeautifulSoup
import aiohttp
import asyncio

BASE_URL = "https://www.fccenvironment.co.uk/harborough/"
BIN_DATA_URL = BASE_URL + "detail-address"

async def collect_data(uprn):
    """
    Returns the next collection dates from the bin collection page.

    :param uprn: The UPRN of the address to find the next collection dates for.
    :return: A dictionary containing the bin types that HDC collect as keys, and the next collection dates as values.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(BIN_DATA_URL, data={"Uprn": uprn}) as resp:
            if resp.status == 200:
                bin_data_site = await resp.text()

    soup = BeautifulSoup(bin_data_site, "html.parser")
    bin_div = soup.select_one(".block-your-next-scheduled-bin-collection-days")
    bin_types = [bin_type.strip()
                for bin_type in bin_div.find_all(text=True)
                if bin_type.parent.name == "li"
                and "green" not in bin_type]
    bin_dates = [datetime.strptime(bin_date.strip() + " @ 07:00", '%d %B %Y @ %H:%M').isoformat()
                for bin_date in bin_div.find_all(text=True)
                if bin_date.parent.name == "span"
                and "subscribed" not in bin_date]
    for x in range(len(bin_types)):
        bin_types[x] = bin_types[x][bin_types[x].find("(")+1:bin_types[x].find(")")][:-4].split("-")[0]
    return dict(zip(bin_types, bin_dates))

if __name__ == "__main__":
    import json
    import argparse
    parser = argparse.ArgumentParser(description="Find the next collection dates for a specific address in Market Harborough, UK.")
    parser.add_argument("uprn", type=int, help="The UPRN of the address to find the next collection dates for.")
    args = parser.parse_args()
    print(json.dumps(asyncio.run(collect_data(args.uprn)), indent=4, sort_keys=True))
