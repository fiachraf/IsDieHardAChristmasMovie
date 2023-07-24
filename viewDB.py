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
res = (cur.execute('SELECT * FROM movie'))
print('res.fetchall()', res.fetchall())

con.close()