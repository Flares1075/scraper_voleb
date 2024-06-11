import requests as req
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from time import sleep
from random import choice
import sys

def get_page(link):
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

def count_results(results_page):
    print("counting results")
    return


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
for tag in main_page.find_all('td', {'class' : 'center'}):
    children = tag.findChildren()
    links.append(children[0]['href'])
    #print("tag:", tag, "childern:", children)

#print("links:", links)

# first row should be headers then data
rows = []
# headers are: "kód obce", "název obce", "voliči v seznamu", "vydané obálky", "platné hlasy", party names
# party names should be scraped, everthing else can be hardcoded
# a random page will be selected and the party name will be taken from there
# definetly not the most "optimální" way but it is simple
page = get_page(urljoin(main_link, choice(links)))
# some pages show results, some devide into "okrsky"
# same thing is below
if page.find("h2").text.strip() == "Výsledky hlasování za územní celky – výběr okrsku":
    page = get_page(urljoin(main_link, choice(page.find_all('td', {'class' : 'cislo'})).findChildren()[0]["href"])) ### what did I just write
elif page.find("h2").text.strip() == "Výsledky hlasování za územní celky":
    pass
else:
    print("ERROR - page not recongnised")
    #print(page)

headers = ["kód obce", "název obce", "okrsek", "voliči v seznamu", "vydané obálky", "platné hlasy"]
for party_name in page.find_all("td", {"class" : "overflow_name"}):
    headers.append(party_name.text)

rows.append(headers)
print(headers)
print(rows[0])

for link in links:
    page = get_page(urljoin(main_link, link))
    # some pages show results, some devide into "okrsky"
    if page.find("h2").text.strip() == "Výsledky hlasování za územní celky – výběr okrsku":
        # print("\"výběr okrsku\" detected")
        # this loop is very similar to "for tag in main_page..."
        for tag in page.find_all('td', {'class' : 'cislo'}):
            #print(tag.findChildren()[0]["href"])
            count_results(get_page(urljoin(main_link, tag.findChildren()[0]["href"])))
    elif page.find("h2").text.strip() == "Výsledky hlasování za územní celky":
        # print("results detected")
        count_results(page)
    else:
        print("ERROR - page not recongnised")
        #print(page)
        continue
