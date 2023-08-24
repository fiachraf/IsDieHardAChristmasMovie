
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

        # chris = movieChris(page, 'https://www.rottentomatoes.com/m/sound_of_freedom')
        # print(chris)
        # chris = movieChris(page, 'https://www.rottentomatoes.com/m/elf')
        # print(chris)

        # print(mvGenre)
        page.goto('https://www.rottentomatoes.com/m/joy_ride_2023')
        # test = rottenLink(page, 'joy ride 23')
        # print(test)
        # test = rottenSearch(page, 'Spider-Man: No Way Hom')
        # print(f'2 {test}')
        # rottenSearch(page, 'elf')
        # mDir = movieDir(page, 'https://www.rottentomatoes.com/m/schindlers_list')

        print(rottenLink(page, 'The Godfather Part II'))
        # print(mDir)
        browser.close()



def movieChris(mvPage, url, goto=True):
    #get the title of the movie from the webpage
    if goto == True:
        mvPage.goto(url)
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    # print('test5')
    html = mvPage.content()
    # print('test6')
    soup = BeautifulSoup(html, 'html.parser')
    # print('test7')


    for k in soup.find_all(class_='genre'):
        # print(mvPage, 'chris3', k)
        grape = k.get_text()
        # print(f'grape: {grape}')
        if grape.find('holiday') == -1 and grape.find('Holiday') == -1:
            continue
        else:
            return True
        continue
    return False

def movieDir(mvPage, url, goto=True):
    #get the title of the movie from the webpage
    if goto == True:
        mvPage.goto(url)
    #get the html from the imdb page and then use beautiful soup to parse it and find the desired info
    # print('test5')
    html = mvPage.content()
    # print('test6')
    soup = BeautifulSoup(html, 'html.parser')
    # print('test7')

    for l in soup.find_all("a", {"data-qa" : "movie-info-director"}):
        # print('l',l)
        # print('l.get_text()',l.get_text())
        return l.get_text()


def rottenLink(mvPage, mvName: str) -> str:
    mvName = mvName.lower()
    mv_Name_1 = mvName.replace(' ', '_')
    mv_Name = mv_Name_1.replace('-', '_')
    link = 'https://www.rottentomatoes.com/m/' + mv_Name

    try:
        mvPage.goto(link)
        testLink = mvPage.get_by_role("heading", name="404 - Not Found")
        # testLink.wait_for()
        if testLink.is_visible() == True:
            #if it gets a 404 then it will try search for the movie
            #if the link returns a 404 then return an empty string
            mvPage.goto('https://www.rottentomatoes.com/')
            link = rottenSearch(mvPage, mvName)
            return link
    except Exception as e:
        pass

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
    #wait for the page to load fully
    mvPage.locator("#scoreboard").get_by_text("Tomatometer").wait_for()
    html = mvPage.content()
    soup = BeautifulSoup(html, 'html.parser')
    #find the title as listed on the page
    grape = soup.find_all('h1', class_='title')
    # for k in grape:
    #     print('k', k)
    #     ape = k.get_text()
    #     #if the name supplied to search for matches exactly with the rotten tomatoes title
    #     if mvName == ape:
    #         return mvPage.url
    #     else:
    #         return ''
    # doing check for same director in main script as if I need to search rotten Tomatoes then the name probably won't be an exact match
    return mvPage.url

if __name__ == '__main__':
    main()
