"""A module that finds the next bin collection dates for a specific address in Market Harborough, UK. Uses the UPRN to find the address."""
from datetime import datetime
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
import aiohttp
import asyncio
import ssl

BASE_URL = "https://harborough.fccenvironment.co.uk/"
BIN_DATA_URL = BASE_URL + "detail-address"

CA_PEM = """-----BEGIN CERTIFICATE-----
MIIDjjCCAnagAwIBAgIQAzrx5qcRqaC7KGSxHQn65TANBgkqhkiG9w0BAQsFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH
MjAeFw0xMzA4MDExMjAwMDBaFw0zODAxMTUxMjAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IEcyMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuzfNNNx7a8myaJCtSnX/RrohCgiN9RlUyfuI
2/Ou8jqJkTx65qsGGmvPrC3oXgkkRLpimn7Wo6h+4FR1IAWsULecYxpsMNzaHxmx
1x7e/dfgy5SDN67sH0NO3Xss0r0upS/kqbitOtSZpLYl6ZtrAGCSYP9PIUkY92eQ
q2EGnI/yuum06ZIya7XzV+hdG82MHauVBJVJ8zUtluNJbd134/tJS7SsVQepj5Wz
tCO7TG1F8PapspUwtP1MVYwnSlcUfIKdzXOS0xZKBgyMUNGPHgm+F6HmIcr9g+UQ
vIOlCsRnKPZzFBQ9RnbDhxSJITRNrw9FDKZJobq7nMWxM4MphQIDAQABo0IwQDAP
BgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBhjAdBgNVHQ4EFgQUTiJUIBiV
5uNu5g/6+rkS7QYXjzkwDQYJKoZIhvcNAQELBQADggEBAGBnKJRvDkhj6zHd6mcY
1Yl9PMWLSn/pvtsrF9+wX3N3KjITOYFnQoQj8kVnNeyIv/iPsGEMNKSuIEyExtv4
NeF22d+mQrvHRAiGfzZ0JFrabA0UWTW98kndth/Jsw1HKj2ZL7tcu7XUIOGZX1NG
Fdtom/DzMNU+MeKNhJ7jitralj41E6Vf8PlwUHBHQRFXGU7Aj64GxJUTFy8bJZ91
8rGOmaFvE7FBcf6IKshPECBV1/MUReXgRPTqh5Uykw7+U0b6LJ3/iyK5S9kJRaTe
pLiaWN0bfVKfjllDiIGknibVb63dDcY3fe0Dkhvld1927jyNxF1WW6LZZm6zNTfl
MrY=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIEszCCA5ugAwIBAgIQCyWUIs7ZgSoVoE6ZUooO+jANBgkqhkiG9w0BAQsFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH
MjAeFw0xNzExMDIxMjI0MzNaFw0yNzExMDIxMjI0MzNaMGAxCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xHzAdBgNVBAMTFlJhcGlkU1NMIFRMUyBSU0EgQ0EgRzEwggEiMA0GCSqGSIb3
DQEBAQUAA4IBDwAwggEKAoIBAQC/uVklRBI1FuJdUEkFCuDL/I3aJQiaZ6aibRHj
ap/ap9zy1aYNrphe7YcaNwMoPsZvXDR+hNJOo9gbgOYVTPq8gXc84I75YKOHiVA4
NrJJQZ6p2sJQyqx60HkEIjzIN+1LQLfXTlpuznToOa1hyTD0yyitFyOYwURM+/CI
8FNFMpBhw22hpeAQkOOLmsqT5QZJYeik7qlvn8gfD+XdDnk3kkuuu0eG+vuyrSGr
5uX5LRhFWlv1zFQDch/EKmd163m6z/ycx/qLa9zyvILc7cQpb+k7TLra9WE17YPS
n9ANjG+ECo9PDW3N9lwhKQCNvw1gGoguyCQu7HE7BnW8eSSFAgMBAAGjggFmMIIB
YjAdBgNVHQ4EFgQUDNtsgkkPSmcKuBTuesRIUojrVjgwHwYDVR0jBBgwFoAUTiJU
IBiV5uNu5g/6+rkS7QYXjzkwDgYDVR0PAQH/BAQDAgGGMB0GA1UdJQQWMBQGCCsG
AQUFBwMBBggrBgEFBQcDAjASBgNVHRMBAf8ECDAGAQH/AgEAMDQGCCsGAQUFBwEB
BCgwJjAkBggrBgEFBQcwAYYYaHR0cDovL29jc3AuZGlnaWNlcnQuY29tMEIGA1Ud
HwQ7MDkwN6A1oDOGMWh0dHA6Ly9jcmwzLmRpZ2ljZXJ0LmNvbS9EaWdpQ2VydEds
b2JhbFJvb3RHMi5jcmwwYwYDVR0gBFwwWjA3BglghkgBhv1sAQEwKjAoBggrBgEF
BQcCARYcaHR0cHM6Ly93d3cuZGlnaWNlcnQuY29tL0NQUzALBglghkgBhv1sAQIw
CAYGZ4EMAQIBMAgGBmeBDAECAjANBgkqhkiG9w0BAQsFAAOCAQEAGUSlOb4K3Wtm
SlbmE50UYBHXM0SKXPqHMzk6XQUpCheF/4qU8aOhajsyRQFDV1ih/uPIg7YHRtFi
CTq4G+zb43X1T77nJgSOI9pq/TqCwtukZ7u9VLL3JAq3Wdy2moKLvvC8tVmRzkAe
0xQCkRKIjbBG80MSyDX/R4uYgj6ZiNT/Zg6GI6RofgqgpDdssLc0XIRQEotxIZcK
zP3pGJ9FCbMHmMLLyuBd+uCWvVcF2ogYAawufChS/PT61D9rqzPRS5I2uqa3tmIT
44JhJgWhBnFMb7AGQkvNq9KNS9dd3GWc17H/dXa1enoxzWjE0hBdFjxPhUb0W3wi
8o34/m8Fxw==
-----END CERTIFICATE-----"""

SSL_CONTEXT = ssl.create_default_context(cadata=CA_PEM)


async def collect_data(session: aiohttp.ClientSession, uprn):
    """
    Returns the next collection dates from the bin collection page.

    :param uprn: The UPRN of the address to find the next collection dates for.
    :return: A dictionary containing the bin types that HDC collect as keys, and the next collection dates as values.
    """
    try:
        async with session.post(
            BIN_DATA_URL, data={"Uprn": uprn}, allow_redirects=False, ssl=SSL_CONTEXT
        ) as resp:
            if resp.status == 200:
                bin_data_site = await resp.text()
            elif resp.status == 302:
                return "invalid_uprn"
            else:
                print()
                return f"connection_error: {str(resp.status)}"
    except aiohttp.ClientConnectorError as e:
        return f"connection_error: {e}"

    soup = BeautifulSoup(bin_data_site, "html.parser")
    bin_div = soup.select_one(".block-your-next-scheduled-bin-collection-days")
    bin_types = [
        bin_type.strip()
        for bin_type in bin_div.find_all(string=True)
        if bin_type.parent.name == "li" and "green" not in bin_type
    ]

    bin_dates = [
        datetime.strptime(bin_date.strip() + " @ 07:00", "%d %B %Y @ %H:%M").replace(tzinfo=ZoneInfo('Europe/London'))
        for bin_date in bin_div.find_all(string=True)
        if bin_date.parent.name == "span" and "subscribed" not in bin_date
    ]
    for x in range(len(bin_types)):
        bin_types[x] = bin_types[x][
            bin_types[x].find("(") + 1 : bin_types[x].find(")")
        ][:-4].split("-")[0]

    bin_list = []

    for i in range(len(bin_types)):
        bin_list.append(
            {"bin_type": bin_types[i], "collection_timestamp": bin_dates[i]}
        )

    # return dict(zip(bin_types, bin_dates))
    return bin_list


async def verify_uprn(session: aiohttp.ClientSession, uprn):
    """
    Verifies that the UPRN is valid and that Harborough District Council is the authority for the address.

    :param uprn: The UPRN of the address to verify.
    :return: (True,  "") if the UPRN is valid and Harborough District Council is the authority for the address.\n
             (False, "invalid_uprn") if not.\n
             (False, "connection_error: [message]") if there was an unexpected error.
    """

    try:
        async with session.post(
            BIN_DATA_URL, data={"Uprn": uprn}, allow_redirects=False, ssl=SSL_CONTEXT
        ) as resp:
            if resp.status == 200:
                return True, ""
            elif resp.status == 302:
                return False, "invalid_uprn"
            else:
                print()
                return False, f"connection_error: {str(resp.status)}"
    except aiohttp.ClientConnectorError as e:
        return False, f"connection_error: {e}"


async def main(args):
    async with aiohttp.ClientSession() as session:
        if await verify_uprn(session, args.uprn):
            bin_data = await collect_data(session, args.uprn)
            if bin_data == "invalid_uprn":
                print("The UPRN is not valid for Harborough District Council.")
            elif str(bin_data).startswith("connection_error"):
                print(f"Connection error: {bin_data.split(': ')[1]}")
            else:
                print(json.dumps(bin_data, indent=4, sort_keys=True, default=str))

        else:
            print("The UPRN is not valid for Harborough District Council.")


if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(
        description="Find the next collection dates for a specific address in Market Harborough, UK."
    )
    parser.add_argument(
        "uprn",
        type=int,
        help="The UPRN of the address to find the next collection dates for.",
    )
    args = parser.parse_args()
    asyncio.run(main(args))

