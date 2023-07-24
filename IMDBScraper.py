
from playwright.sync_api import Playwright, sync_playwright, expect
import pathlib
from bs4 import BeautifulSoup
import re

#gets the path of this file
thisPath = pathlib.Path(__file__).parent.resolve()
# by default just use test as the first search term
trendTerm = 'test'

def main() -> None:
    with sync_playwright() as playwright:
        #create a headed browser so I can click refresh so it won't think I'm a bot
        browser = playwright.firefox.launch(headless=False)
        page = browser.new_page()

        #try get the list from the top 250 page, it will fail if it loads the new imdb wesite and so it will keeo trying until it loads the old one
        # try:
            # linkList = imdbTop250(page)
        # except Exception as e:
        #     new_page = True
        #     #keep trying to load old page
        #     while new_page:
        #         page.close()
        #         page = browser.new_page()
        #         try:
        #             linkList = imdbTop250(page)
        #             new_page = False
        #         except Exception as e:
        #             pass
        # print(linkList)
        # linkList = imdbTop250(page)
        # try:
        #     linkList = imdbTop250New(page)
        # except Exception as e:
        #     linkList = imdbTop250(page)
        # print(linkList)

        print(imdbGenre250(page,'https://www.imdb.com/search/title/?title_type=feature&genres=animation&start=1&explore=genres&ref_=adv_nxt'))
        # print(imdbGenre250(page,'https://www.imdb.com/search/title/?title_type=feature&genres=animation&start=1&explore=genres&ref_=adv_nxt'))
        #get the title of the movie from the webpage
        mvTitle = movieTitle(page, 'https://www.imdb.com/title/tt0111161/')

        print(mvTitle)

        browser.close()


def imdbTop250(Top250Page: Playwright) -> list:
    # go to top 250 movies Top250Page to get the list of 250 urls to them do some meddling with to get 5000 movie titles
    Top250Page.goto("https://www.imdb.com/chart/top/?ref_=nv_mv_250")
    #this waits for the specified element to be loaded on the Top250Page. This will ensure that the table is loaded. If it doesn't load it will timeout and crash
    # get it to close and open another tab if it opens the new imdb website
    lastEntry=Top250Page.get_by_role("cell", name=re.compile(r"^250\."))
    lastEntry.wait_for()
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    html = Top250Page.content()
    soup = BeautifulSoup(html, 'html.parser')
    #finds all the rows in the table that contain the movie title as well as part of the link for that movie on imdb
    row_entries = soup.find_all(class_='titleColumn')
    websiteList = []
    #for each row
    for k in row_entries:
        #find the a tag in the row, is of type <class 'bs4.element.Tag'>
        ape = k.find('a')
        #get the partial link is of type <class 'str'>
        partial_link = ape.get('href')
        #fix link
        link = 'https://www.imdb.com' + partial_link[:17]
        #get the text/title, is of type <class 'str'>
        mvTitle = ape.get_text()
        # print(f'link: {link}\nmvTitle: {mvTitle}')
        websiteList.append(link)
    return list

def imdbTop250New(Top250Page: Playwright) -> list:
    # go to top 250 movies Top250Page to get the list of 250 urls to them do some meddling with to get 5000 movie titles
    Top250Page.goto("https://www.imdb.com/chart/top/?ref_=nv_mv_250")
    #this waits for the specified element to be loaded on the Top250Page. This will ensure that the table is loaded. If it doesn't load it will timeout and crash
    # get it to close and open another tab if it opens the new imdb website
    lastEntry=Top250Page.get_by_role("listitem").filter(has_text=re.compile(r"^250\."))
    lastEntry.wait_for()
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    html = Top250Page.content()
    soup = BeautifulSoup(html, 'html.parser')
    row_entries = soup.find_all(class_='ipc-title-link-wrapper')
    websiteList = []
    for k in row_entries:
        #k has type <class 'bs4.element.Tag'>
        partial_link = k.get('href')
        link = 'https://www.imdb.com' + partial_link[:17]
        if link.find('title') == -1:
            continue
        #k has sub tag of h3 that has the movie title
        grape = k.find('h3')
        grapeText = grape.get_text()
        mvTitle = grapeText[grapeText.find(' ') + 1:]
        # print(f'link: {link}\nmvTitle: {mvTitle}')
        websiteList.append(link)
    return websiteList

def imdbGenre250(G250Page, url):
    #get the first 250 movies listed for the genre
    # go to the genre page
    G250Page.goto(url)
    websiteList = []
    extraPages = ['50.', '100.', '150.', '200.', '250.', '300.']
    for limit in extraPages:
        lastEntry=G250Page.get_by_role("heading").filter(has_text=limit)
        #this waits for the specified element to be loaded on the page. This will ensure that the table is loaded. If it doesn't load it will timeout and crash
        lastEntry.wait_for()
        #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
        html = G250Page.content()
        soup = BeautifulSoup(html, 'html.parser')
        row_entries = soup.find_all(class_='lister-item-header')
        for k in row_entries:
            ape = k.find('a')
            #ape has type <class 'bs4.element.Tag'>
            partial_link = ape.get('href')
            link = 'https://www.imdb.com' + partial_link[:17]
            if link.find('title') == -1:
                continue
            websiteList.append(link)
        #click through to the next page
        G250Page.get_by_role("link", name="Next »").nth(1).wait_for()
        G250Page.get_by_role("link", name="Next »").nth(1).click()
    return websiteList

def movieTitle(mvPage, url) -> str:
    #get the title of the movie from the webpage
    mvPage.goto(url)
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    html = mvPage.content()
    soup = BeautifulSoup(html, 'html.parser')
    mvTitle = soup.find('title').get_text()
    print(f'mvTitle: {mvTitle}')
    titleEndIndex = (re.search(r"\s*\(.*\)", mvTitle)).span()[0]
    return mvTitle[:titleEndIndex]


if __name__ == '__main__':
    main()
