
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
        browser = playwright.firefox.launch(headless=False, slow_mo=50)
        page = browser.new_page()

        chris = movieChris(page, 'https://www.rottentomatoes.com/m/sound_of_freedom')
        # print(chris)
        # chris = movieChris(page, 'https://www.rottentomatoes.com/m/elf')
        # print(chris)

        # print(mvGenre)
        page.goto('https://www.rottentomatoes.com/m/joy_ride_202')
        rottenSearch(page, 'elf')
        browser.close()



def movieChris(mvPage, url, goto=True):
    #get the title of the movie from the webpage
    if goto == True:
        mvPage.goto(url)
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    html = mvPage.content()
    soup = BeautifulSoup(html, 'html.parser')

    for k in soup.find_all(class_='info-item-value'):
        if 'genre"' in k.attrs:
            grape = k.get_text()
            # print(f'grape: {grape}')
            if grape.find('holiday') == -1 and grape.find('Holiday') == -1:
                continue
            else:
                return True
            continue
    return False

def rottenLink(mvName: str) -> str:
    mvName = mvName.lower()
    mvName = mvName.replace(' ', '_')
    link = 'https://www.rottentomatoes.com/m/' + mvName
    return link

def rottenSearch(mvPage, mvName):
    try:
        searchBox = mvPage.get_by_placeholder("Search movies, TV, actors, more...")
    except Exception as e:
        dummy = input('require use input, prob')
    searchBox.click()
    searchBox.fill(mvName)
    riop = mvPage.locator('html body.body.no-touch.js-mptd-layout.roma div.container.roma-layout__body.layout-body rt-header#header-main.navbar search-algolia search-algolia-results search-algolia-results-category ul li a').first.click()
    #using the false can cause a cookie banner to appear and cause interference and it may give the weong result
    # print(movieChris(mvPage, mvPage.url, False))
    # print(movieChris(mvPage, mvPage.url))
    return mvPage.url

if __name__ == '__main__':
    main()
