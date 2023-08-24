import TrendDataDownloader as gtrend
import rottenScraper as rotten
import IMDBScraper as imdb
import sqlite3 as sql
from playwright.sync_api import Playwright, sync_playwright, expect
import json

con = sql.connect('movie.db')
cur = con.cursor()

# print(res := (cur.execute('SELECT name FROM sqlite_master WHERE name="movie"')))
# print(res.fetchone())
# print(res.fetchall())
# try:
#     res = (cur.execute('SELECT name FROM sqlite_master WHERE name="movie"'))
#     print('res.fetchone()', res.fetchone())
#     if res.fetchone()[0] != 0:
#         cur.execute('CREATE TABLE movie(Mindex, title, imdb_link, bool_christmas, rotten_link, trend_path)')
# except:
#     pass
try:
    #statements only get called once the result can only be used once and then after that the result seems to be garbage collected
    res = (cur.execute('SELECT name FROM sqlite_master'))
    # print('res.fetchone()', res.fetchone())
    if 'movie' not in res.fetchall():
        cur.execute('CREATE TABLE movie(Mindex, title, imdb_link, bool_christmas, rotten_link, trend_path)')
except:
    pass

with sync_playwright() as playwright:
    # Load the cookies
    #create a headed browser so I can click refresh so it won't think I'm a bot
    browser = playwright.firefox.launch(headless=False)
    context = browser.new_context()

    try:
        #adding cookies
        with open("cookies.json", "r") as f:
            cookies = json.loads(f.read())
            context.add_cookies(cookies)
    except:
        pass
    page1 = context.new_page()
    page2 = context.new_page()
    page3 = context.new_page()

    #try get the list of top 250 movies
    try:
        imdb_list = imdb.imdbTop250New(page1)
    except Exception as e:
        imdb_list = imdb.imdbTop250(page1)

    #open the google trends page
    gtrend.gotoGTrend(page2)

    #create index for key column
    cindex = 0
    with open("cookies.json", "w") as f:
        f.write(json.dumps(context.cookies()))
    #for each link from the imdb top 250 page
    for index, imdbLink in enumerate(imdb_list):
        try:
            data = []
            res = cur.execute('SELECT title FROM movie WHERE imdb_link=(?)', (imdbLink,))
            # print(f'{}')
            # print(f'res:{res}')
            # print(f'res.fetchone():{res.fetchone()}')
            # print(f'len(res.fetchall()):{len(res.fetchall())}')
            print(f'res.fetchall():{res.fetchall()}')
            # test = res.fetchall()
            # print(f'len(test): {len(test)}')
            # print(f'test: {test}')
            # print(f'type(res.fetchall()):{type(res.fetchall())}')
            res = cur.execute('SELECT title FROM movie WHERE imdb_link=(?)', (imdbLink,))
            if len(res.fetchall()) == 0:
                print('no')
                mvTitle = imdb.movieTitle(page1, imdbLink)
                page1.wait_for_timeout(1500)
                print(f'mvTitle: {mvTitle}')
                #see if the movie can be found on rotten tomatoes
                rLink = rotten.rottenLink(page3, mvTitle)
                if rLink == '':
                    print('test')
                    continue
                print('chris1')
                page3.wait_for_timeout(1500)
                christmas = rotten.movieChris(page3, rLink, goto=False)
                print('chris2')
                page3.wait_for_timeout(1500)
                #search for the google trends data
                # gtrend.searchNewTrend(page2, mvTitle)
                # page2.wait_for_timeout(1500)
                # trend_path = gtrend.dlTrendCSV(page2, '/home/fiachra/atom_projects/IsDieHardAChristmasMovie/GoogleTrends/Data', mvTitle)
                # page2.wait_for_timeout(1500)
                #get the last entry in the table so new entries can be inserted after it
                res = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC')
                lIndex = res.fetchone()[0]

                # data = [lIndex + 1, mvTitle, imdbLink, christmas, rLink, trend_path]
                data = [lIndex + 1, mvTitle, imdbLink, christmas, rLink]
                # cur.execute('INSERT INTO movie VALUES(?, ?, ?, ?, ?, ?)', data)
                cur.execute('INSERT INTO movie (Mindex, title, imdb_link, bool_christmas, rotten_link) VALUES(?, ?, ?, ?, ?)', data)
                con.commit()

        except Exception as E:
            print(E)
            print(data)
        #break for initial testing
        # break

    #get even more movies based on the genre lists from imdb
    for genre in ['https://www.imdb.com/search/title/?genres=Action&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Animation&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Biography&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Comedy&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Crime&explore=genres&title_type=feature',
    #documentary category doesn't seemt to exist
    #'https://www.imdb.com/search/title/?genres=Documentary&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Drama&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Family&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Fantasy&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=History&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Horror&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Music&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Mystery&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Romance&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Sci-Fi&explore=genres&title_type=feature',
    'https://www.imdb.com/search/title/?genres=Thriller&explore=genres&title_type=feature']:
        imdb_list = imdb.imdbGenre250(page1, genre)
        for index, imdbLink in enumerate(imdb_list):
            try:
                data = []
                res = cur.execute('SELECT title FROM movie WHERE imdb_link=(?)', (imdbLink,))
                if len(res.fetchall()) == 0:
                    mvTitle = imdb.movieTitle(page1, imdbLink)
                    page1.wait_for_timeout(1500)
                    #see if the movie can be found on rotten tomatoes
                    rLink = rotten.rottenLink(page3, mvTitle)
                    if rLink == '':
                        print('test')
                        continue
                    christmas = rotten.movieChris(page3, rLink, goto=False)
                    page3.wait_for_timeout(1500)
                    #search for the google trends data
                    # gtrend.searchNewTrend(page2, mvTitle)
                    # page2.wait_for_timeout(1500)
                    # trend_path = gtrend.dlTrendCSV(page2, '/home/fiachra/atom_projects/IsDieHardAChristmasMovie/GoogleTrends/Data', mvTitle)
                    # page2.wait_for_timeout(1500)

                    res = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC')
                    lIndex = res.fetchone()[0]

                    # data = [lIndex + 1, mvTitle, imdbLink, christmas, rLink, trend_path]
                    data = [lIndex + 1, mvTitle, imdbLink, christmas, rLink]
                    # cur.execute('INSERT INTO movie VALUES(?, ?, ?, ?, ?, ?)', data)
                    cur.execute('INSERT INTO movie (Mindex, title, imdb_link, bool_christmas, rotten_link) VALUES(?, ?, ?, ?, ?)', data)
                    con.commit()
                    # print(f'cindex: {cindex}')
                # break for initial testing
                # break
            except Exception as E:
                print(E)
                print(data)
     # Save the cookies
    with open("cookies.json", "w") as f:
        f.write(json.dumps(context.cookies()))




    #add loop to go through the now 250 entries in the table, and get the 'adjacent' imdb links for more movies, check if these new ones already exist in the table and if not then add them to the table

    browser.close()
con.close()