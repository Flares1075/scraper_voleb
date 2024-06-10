import requests as req
from bs4 import BeautifulSoup as bs
import sys

if len(sys.argv) < 3:
    print("Je zapotřebí zadat odkaz na územní celek a název výstupního souboru")
    sys.exit(1)

# get the page and make it work-with-able
main_page = bs(req.get(sys.argv[1]).text, features="html.parser")

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
for tag in main_page.find_all('td', {'class' : 'center'}):
    children = tag.findChildren()
    links.append(children[0]['href'])
    #print("tag:", tag, "childern:", children)

print("links:", links)