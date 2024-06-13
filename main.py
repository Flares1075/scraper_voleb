import requests as req
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse, parse_qs
from time import sleep
from random import choice
import sys
import csv

def get_page(link: str):
    # exceptions often thrown becouse of "MaxRetryError"
    # try to get page if refused sleep 10s if refused again sleep 20s... up to a minute
    # else "oh no"
    for pokus in range(1, 7):
        try:
            print("getting", link)
            # get the page and make it work-with-able
            page = bs(req.get(link).text, features="html.parser")
            print("success")
            return page
        except req.exceptions.ConnectionError:
            print("Connection refused, sleeping for", 10 * pokus)
            sleep(10 * pokus)
    print("ERROR - get_page unsuccessful")
    return


# returns row of data for "rows" list
# row should be: "kód obce", "název obce", "okrsek", "voliči v seznamu", "vydané obálky", "platné hlasy", party results
# params page with results and the page url literally only for "kód obce" that isn't on the results page anywhere but is in the URL
### it would probably be better if it just got the link, and then called get_page itself
def count_results(results_page: bs, link: str):
    print("counting results from", link)
    row = []
    # get kód obece from the url, inspiration here: https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url
    row.append(parse_qs(urlparse(link).query)["xobec"][0])
    # název obce
    for h3 in results_page.find_all("h3"):
        if "Obec:" in h3.text:
            row.append(h3.text.strip()[6:])
            break
    # okresek (appears only sometimes) is actually also in the URL, hooray
    try:
        row.append(parse_qs(urlparse(link).query)["xokrsek"][0])
    except KeyError:
        row.append("N/A")
    # voliči v seznamu
    row.append(results_page.find("td", {"headers": "sa2"}).text)
    # vydané obálky
    row.append(results_page.find("td", {"headers": "sa3"}).text)
    # platné hlasy
    row.append(results_page.find("td", {"headers": "sa6"}).text)
    # party results
    for result in results_page.find_all(
        "td", {"headers": "t1sa2 t1sb3"}
    ) + results_page.find_all("td", {"headers": "t2sa2 t2sb3"}):
        row.append(result.text)
    # print(row)
    return row


##################################################################################################


if len(sys.argv) < 3:
    print("Je zapotřebí zadat odkaz na územní celek a název výstupního souboru")
    sys.exit(1)

main_link = sys.argv[1]
main_page = get_page(sys.argv[1])

# print some important(?) info from the main page
print(main_page.find("h1").text)
# hl.m. Praha doesn't have h3 with "okres: ..."
if "Praha" in main_page.find_all("h3")[0].text:
    print(main_page.find_all("h3")[0].text)
else:
    print(main_page.find_all("h3")[0].text, main_page.find_all("h3")[1].text)
### this code probably isn't very "optimální" but it's only some string-work soooo....

links = []
# find all "td" tags with class "center" (those are the ones that contain wanted a tags)
# then get the childern of that tag (should be only an "a" tag)
# and put the url inside href into list "links"
# inspiration here: https://stackoverflow.com/questions/44958587/python-beautifulsoup-get-tag-within-a-tag
for tag in main_page.find_all("td", {"class": "center"}):
    children = tag.findChildren()
    links.append(children[0]["href"])
    # print("tag:", tag, "childern:", children)

# first row should be headers then data
rows = []
# headers are: "kód obce", "název obce", "okrsek", "voliči v seznamu", "vydané obálky", "platné hlasy", party names
# party names should be scraped, everthing else can be hardcoded
# a random page will be selected and the party name will be taken from there
# definetly not the most "optimální" way but it is simple
page = get_page(urljoin(main_link, choice(links)))
# some pages show results, some devide into "okrsky"
# same thing is below
if page.find("h2").text.strip() == "Výsledky hlasování za územní celky – výběr okrsku":
    page = get_page(
        urljoin(
            main_link,
            choice(page.find_all("td", {"class": "cislo"})).findChildren()[0]["href"],
        )
    )  ### what did I just write
elif page.find("h2").text.strip() == "Výsledky hlasování za územní celky":
    pass
else:
    print("ERROR - page not recongnised")

headers = [
    "kód obce",
    "název obce",
    "okrsek",
    "voliči v seznamu",
    "vydané obálky",
    "platné hlasy",
]
for party_name in page.find_all("td", {"class": "overflow_name"}):
    headers.append(party_name.text)

rows.append(headers)

for link in links:
    page = get_page(urljoin(main_link, link))
    # some pages show results, some devide into "okrsky"
    if (
        page.find("h2").text.strip() == "Výsledky hlasování za územní celky – výběr okrsku"
    ):
        # this loop is very similar to "for tag in main_page..."
        for tag in page.find_all("td", {"class": "cislo"}):
            rows.append(
                count_results(
                    get_page(urljoin(main_link, tag.findChildren()[0]["href"])),
                    urljoin(main_link, tag.findChildren()[0]["href"]),
                )
            )
    elif page.find("h2").text.strip() == "Výsledky hlasování za územní celky":
        rows.append(count_results(page, urljoin(main_link, link)))
    else:
        print("ERROR - page not recongnised")
        continue

with open(sys.argv[2], 'w', newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(rows)
