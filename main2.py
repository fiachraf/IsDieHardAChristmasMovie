import TrendDataDownloader as gtrend
import rottenScraper as rotten
import IMDBScraper as imdb
import sqlite3 as sql
from playwright.sync_api import Playwright, sync_playwright, expect
import json
import logging




def IMDBscraping():
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
        try:
            imdb_list = imdb.imdbTop250New(page1)
        except Exception as e:
            imdb_list = imdb.imdbTop250(page1)
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #for each link from the imdb top 250 page
        for index, imdbLink in enumerate(imdb_list):
            try:
                data = []
                res = cur.execute('SELECT title FROM movie WHERE imdb_link=(?)', (imdbLink,))
                logging.debug(f'res.fetchall():{res.fetchall()}')
                res = cur.execute('SELECT title FROM movie WHERE imdb_link=(?)', (imdbLink,))
                resDir = cur.execute('SELECT director FROM movie WHERE imdb_link=(?)', (imdbLink,))
                if len(res.fetchall()) == 0:
                    # print('rest')
                    logging.debug('no')
                    mvTitle = imdb.movieTitle(page1, imdbLink)
                    mvDir = imdb.movieDirector(page1)
                    page1.wait_for_timeout(1500)
                    logging.debug(f'mvTitle: {mvTitle}')
                    res = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC')
                    lIndex = res.fetchone()[0]
                    data = [lIndex + 1, mvTitle, imdbLink, mvDir]
                    cur.execute('INSERT INTO movie (Mindex, title, imdb_link, director) VALUES(?, ?, ?, ?)', data)
                    con.commit()
                elif len(resDir.fetchall()) == 0:
                    # print('rest1')
                    mvTitle = imdb.movieTitle(page1, imdbLink)
                    mvDir = imdb.movieDirector(page1)
                    data = [mvDir, imdbLink]
                    cur.execute('UPDATE movie SET director = (?) WHERE imdb_link=(?)', data)
                    con.commit()
            except Exception as E:
                logging.error(E, exc_info=True)
                logging.error(data)

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
                    resDir = cur.execute('SELECT director FROM movie WHERE imdb_link=(?)', (imdbLink,))
                    if len(res.fetchall()) == 0:
                        mvTitle = imdb.movieTitle(page1, imdbLink)
                        page1.wait_for_timeout(1500)
                        res = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC')
                        lIndex = res.fetchone()[0]
                        data = [lIndex + 1, mvTitle, imdbLink, mvDir]
                        cur.execute('INSERT INTO movie (Mindex, title, imdb_link, director) VALUES(?, ?, ?, ?)', data)
                        con.commit()
                    elif len(resDir.fetchall()) == 0:
                        # print('rest1')
                        mvTitle = imdb.movieTitle(page1, imdbLink)
                        mvDir = imdb.movieDirector(page1)
                        data = [mvDir, imdbLink]
                        cur.execute('UPDATE movie SET director = (?) WHERE imdb_link=(?)', data)
                        con.commit()
                except Exception as E:
                    logging.error(E, exc_info=True)
                    logging.error(data)
         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        browser.close()
    return

def IMDB_DirFix(start_index=0):
    #made a mistake with my initial code somewhere and it got the wrong director for a lot of movies
    #my code doesn't work for any movie with > 1 director, it lists it as None directors. Might need to fix, depends on how many movies have > 1 director
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

        page3 = context.new_page()

        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #create index for key column, makes it easier with sqlite if it's a list
        cindex = [start_index]

        # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
        entryList = cur.execute('SELECT title, imdb_link, director FROM movie').fetchall()


        last_index = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC LIMIT 1;').fetchone()[0]
        while cindex[0] <= last_index:
            #close the browser context every once in a while to try avoid playwright memory leak
            if cindex[0] % 50 == 0:
                context.close()
                context = browser.new_context()
                try:
                    #adding cookies
                    with open("cookies.json", "r") as f:
                        cookies = json.loads(f.read())
                        context.add_cookies(cookies)
                except:
                    pass

                page3 = context.new_page()

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))
            entry = entryList[cindex[0]]
            print(entry)
            print(cindex[0])
            try:

                eTitle = entry[0]
                eILink = entry[1]
                eDirector = entry[2]

                page3.goto(eILink)
                page3.wait_for_timeout(1100)
                fixDir = imdb.movieDirector(page3)

                # page3.wait_for_timeout(1100)
                data = [fixDir, cindex[0]]
                if fixDir != eDirector:
                    cur.execute('UPDATE movie SET director = (?) WHERE Mindex=(?)', data)
                    con.commit()

                logging.info(cindex[0])
                cindex[0] += 1

                 # Save the cookies
                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

            except Exception as E:
                logging.error(E, exc_info=True)
                try:
                    logging.error(data)
                except Exception as E:
                    pass

         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        browser.close()
    con.close()




def rottenScraping(start_index=0):
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

        page3 = context.new_page()

        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #create index for key column, makes it easier with sqlite if it's a list
        cindex = [start_index]

        # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
        entryList = cur.execute('SELECT title, rotten_link, director FROM movie').fetchall()


        last_index = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC LIMIT 1;').fetchone()[0]
        while cindex[0] <= last_index:
            #close the browser context every once in a while to try avoid playwright memory leak
            if cindex[0] % 50 == 0:
                context.close()
                context = browser.new_context()
                try:
                    #adding cookies
                    with open("cookies.json", "r") as f:
                        cookies = json.loads(f.read())
                        context.add_cookies(cookies)
                except:
                    pass

                page3 = context.new_page()

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))
            entry = entryList[cindex[0]]
            print(entry)
            print(cindex[0])
            try:

                eTitle = entry[0]
                eRLink = entry[1]
                eDirector = entry[2]
                # if eRLink is None:
                #     continue
                # else:
                rLink = rotten.rottenLink(page3, eTitle)
                print('rLink: ', rLink)
                if rLink == '':
                    print('test')
                    cindex[0] += 1

                    continue
                page3.wait_for_timeout(1100)
                christmas = rotten.movieChris(page3, rLink, goto=False)

                page3.wait_for_timeout(1100)
                mDir = rotten.movieDir(page3, rLink, goto=False)
                page3.wait_for_timeout(1100)
                print(f'mDir:{mDir} eDirector:{eDirector}')
                if mDir == eDirector:
                    data = [rLink, cindex[0]]
                    cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                    con.commit()
                else:
                    data = [None, cindex[0]]
                    cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                    con.commit()

                logging.info(cindex[0])
                cindex[0] += 1

                 # Save the cookies
                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

            except Exception as E:
                logging.error(E, exc_info=True)
                try:
                    logging.error(data)
                except Exception as E:
                    pass

         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        browser.close()
    con.close()

def rottenScraping2(start_index=0):
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

        page3 = context.new_page()

        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #create index for key column, makes it easier with sqlite if it's a list
        # cindex = [start_index]

        # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
        entryList = cur.execute('SELECT title, rotten_link, director, Mindex FROM movie WHERE rotten_link IS NULL;').fetchall()


        last_index = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC LIMIT 1;').fetchone()[0]
        for index, entry in enumerate(entryList):
            print('entry', entry, 'index', index)
        # while cindex[0] <= last_index:
            #close the browser context every once in a while to try avoid playwright memory leak
            if index % 50 == 0:
                context.close()
                context = browser.new_context()
                try:
                    #adding cookies
                    with open("cookies.json", "r") as f:
                        cookies = json.loads(f.read())
                        context.add_cookies(cookies)
                except:
                    pass

                page3 = context.new_page()

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))
            # entry = entryList[cindex[0]]
            print(entry)
            # print(cindex[0])
            try:

                eTitle = entry[0]
                eRLink = entry[1]
                eDirector = entry[2]
                eMindex = entry[3]
                if eMindex < start_index:
                    continue
                # if eRLink is None:
                #     continue
                # else:
                rLink = rotten.rottenLink(page3, eTitle, listPlace=2)
                print('rLink: ', rLink)
                if rLink == '':
                    print('test')
                    # cindex[0] += 1

                    continue

                page3.wait_for_timeout(1100)
                christmas = rotten.movieChris(page3, rLink, goto=False)

                page3.wait_for_timeout(1100)
                mDir = rotten.movieDir(page3, rLink, goto=False)
                page3.wait_for_timeout(1100)
                print(f'mDir:{mDir} eDirector:{eDirector}')
                if mDir == eDirector:
                    data = [rLink, eMindex]
                    cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                    con.commit()
                else:
                    data = [None, eMindex]
                    cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                    con.commit()

                logging.info(eMindex)
                # cindex[0] += 1

                 # Save the cookies
                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

            except Exception as E:
                logging.error(E, exc_info=True)
                try:
                    logging.error(data)
                except Exception as E:
                    pass

         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        browser.close()
    con.close()

def rottenScraping3(start_index=0):
    #didn't get the christmas movie bool
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

        page3 = context.new_page()

        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #create index for key column, makes it easier with sqlite if it's a list
        # cindex = [start_index]

        # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
        entryList = cur.execute('SELECT title, rotten_link, director, Mindex FROM movie WHERE bool_christmas IS NULL AND rotten_link IS NOT NULL;').fetchall()


        last_index = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC LIMIT 1;').fetchone()[0]
        for index, entry in enumerate(entryList):
            print('entry', entry, 'index', index)
        # while cindex[0] <= last_index:
            #close the browser context every once in a while to try avoid playwright memory leak
            if index % 50 == 0:
                context.close()
                context = browser.new_context()
                try:
                    #adding cookies
                    with open("cookies.json", "r") as f:
                        cookies = json.loads(f.read())
                        context.add_cookies(cookies)
                except:
                    pass

                page3 = context.new_page()

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))
            # entry = entryList[cindex[0]]
            print(entry)
            # print(cindex[0])
            try:

                eTitle = entry[0]
                eRLink = entry[1]
                eDirector = entry[2]
                eMindex = entry[3]
                if eMindex < start_index:
                    continue
                # if eRLink is None:
                #     continue
                # else:
                # rLink = rotten.rottenLink(page3, eTitle, listPlace=2)
                # print('rLink: ', rLink)
                # if rLink == '':
                #     print('test')
                #     # cindex[0] += 1
                #
                #     continue

                # page3.wait_for_timeout(1100)
                christmas = rotten.movieChris(page3, eRLink, goto=True)

                page3.wait_for_timeout(1100)
                # mDir = rotten.movieDir(page3, rLink, goto=False)
                # page3.wait_for_timeout(1100)
                # print(f'mDir:{mDir} eDirector:{eDirector}')

                data = [christmas, eMindex]
                cur.execute('UPDATE movie SET bool_christmas = (?) WHERE Mindex=(?)', data)
                con.commit()

                logging.info(eMindex)
                # cindex[0] += 1

                 # Save the cookies
                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

            except Exception as E:
                logging.error(E, exc_info=True)
                try:
                    logging.error(data)
                except Exception as E:
                    pass

         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))

        browser.close()
    con.close()

def gTrendScraping(start_index=0):
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

        # page2 = context.new_page()
        page3 = context.new_page()



        #open the google trends page
        gtrend.gotoGTrend(page3)
        page3.wait_for_timeout(2000)

        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))
        #create index for key column, makes it easier with sqlite if it's a list
        cindex = [start_index]

        # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
        entryList = cur.execute('SELECT title, rotten_link, trend_path FROM movie WHERE rotten_link IS NOT NULL;').fetchall()
        # entry = entryList[cindex[0]]
        # # entry = res.fetchone()
        # eTitle = entry[0]
        # eRLink = entry[1]
        # eDirector = entry[2]

        last_index = cur.execute('SELECT Mindex FROM movie ORDER BY Mindex DESC LIMIT 1;').fetchone()[0]
        while cindex[0] <= last_index:
            #close the browser context every once in a while to try avoid playwright memory leak
            if cindex[0] % 50 == 0:
                context.close()
                context = browser.new_context()
                try:
                    #adding cookies
                    with open("cookies.json", "r") as f:
                        cookies = json.loads(f.read())
                        context.add_cookies(cookies)
                except:
                    pass

                page3 = context.new_page()
                #open the google trends page
                gtrend.gotoGTrend(page3)
                page3.wait_for_timeout(2000)

                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))
            entry = entryList[cindex[0]]
            print(entry)
            print(cindex[0])
            try:

                eTitle = entry[0]
                eRLink = entry[1]
                ePath = entry[2]
                # if eRLink is None:
                #     continue
                # else:

                # if rLink == '':
                #     print('test')
                #     cindex[0] += 1
                #     # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
                #     # entry = entryList[cindex[0]]
                #     continue
                # page3.wait_for_timeout(1100)
                # christmas = rotten.movieChris(page3, rLink, goto=False)
                #search for the google trends data
                gtrend.searchNewTrend(page3, eTitle)
                page3.wait_for_timeout(1100)
                trend_path = gtrend.dlTrendCSV(page3, '/home/fiachra/atom_projects/IsDieHardAChristmasMovie/GoogleTrends/Data', eTitle)

                page3.wait_for_timeout(1100)
                data = [trend_path, cindex[0]]
                cur.execute('UPDATE movie SET trend_path = (?) WHERE Mindex=(?)', data)
                con.commit()
                # mDir = rotten.movieDir(page3, rLink, goto=False)
                # page3.wait_for_timeout(1100)
                # print(f'mDir:{mDir} eDirector:{eDirector}')
                # if mDir == eDirector:
                #     data = [rLink, cindex[0]]
                #     cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                #     con.commit()
                # else:
                #     data = [None, cindex[0]]
                #     cur.execute('UPDATE movie SET rotten_link = (?) WHERE Mindex=(?)', data)
                #     con.commit()

                logging.info(cindex[0])
                cindex[0] += 1
                # entry = cur.execute('SELECT title, rotten_link, director FROM movie WHERE Mindex=(?);', cindex).fetchone()
                # entry = entryList[cindex[0]]
                 # Save the cookies
                with open("cookies.json", "w") as f:
                    f.write(json.dumps(context.cookies()))

            except Exception as E:
                logging.error(E, exc_info=True)
                try:
                    logging.error(data)
                except Exception as E:
                    pass
         # Save the cookies
        with open("cookies.json", "w") as f:
            f.write(json.dumps(context.cookies()))



if __name__ == '__main__':
    logging.basicConfig(filename='outlog.log', filemode='a', level=logging.NOTSET)

    mode = input('IMDB, rotten or GTrend or IMDB fix dir or rotten2 or rotten3: ')

    con = sql.connect('movie.db')
    cur = con.cursor()

    try:
        #statements only get called once the result can only be used once and then after that the result seems to be garbage collected
        res = (cur.execute('SELECT name FROM sqlite_master'))
        # print('res.fetchone()', res.fetchone())
        if 'movie' not in res.fetchall():
            cur.execute('CREATE TABLE movie(Mindex, title, imdb_link, bool_christmas, rotten_link, trend_path)')
    except:
        pass

    if mode == 'IMDB':
        IMDBscraping()
    elif mode == 'rotten':
        start_point = input('choose starting index. Default 0: ')
        if start_point == '':
            start_point = 0
        else:
            start_point = int(start_point)
        rottenScraping(start_point)
    elif mode == 'rotten2':
        start_point = input('choose starting index. Default 0: ')
        if start_point == '':
            start_point = 0
        else:
            start_point = int(start_point)
        rottenScraping2(start_point)
    elif mode == 'rotten3':
        start_point = input('choose starting index. Default 0: ')
        if start_point == '':
            start_point = 0
        else:
            start_point = int(start_point)
        rottenScraping3(start_point)
    elif mode == 'GTrend':
        start_point = input('choose starting index. Default 0: ')
        if start_point == '':
            start_point = 0
        else:
            start_point = int(start_point)
        gTrendScraping(start_point)
    elif mode == 'IMDB fix dir':
        start_point = input('choose starting index. Default 0: ')
        if start_point == '':
            start_point = 0
        else:
            start_point = int(start_point)
        IMDB_DirFix(start_point)
    else:
        print('try again')
    con.close()