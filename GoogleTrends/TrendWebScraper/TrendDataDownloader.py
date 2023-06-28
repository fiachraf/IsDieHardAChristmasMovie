
from playwright.sync_api import Playwright, sync_playwright, expect
import pathlib

#gets the path of this file
thisPath = pathlib.Path(__file__).parent.resolve()
# by default just use test as the first search term
trendTerm = 'test'

def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=False)
    #commented out as new context creates it with no cookies
    #context = browser.new_context()
    #page = context.new_page()
    page = browser.new_page()
    # try get some cookies so that google trends doesn't block me
    #context.cookies()
    page.goto("https://docs.python.org/3/reference/datamodel.html")

    #seems that google is able to detect my bot and I need to click refresh and then it will continue for at least 2 search terms

    #go to first page
    # google trends urls have a pattern, this one looks for data from all time, worldwide
    page.goto("https://trends.google.com/trends/explore?date=all&q=test&hl=en-GB")
    #click the download csv file
    with page.expect_download() as download_info:
        page.locator("widget").filter(has_text="Interest over time help_outline Help file_download code share ‪1 Jan 2004‬‪1 Oct").get_by_role("button", name="file_download").click()
    download = download_info.value
    download.save_as(f'{thisPath}/{trendTerm}.csv')
    # click the search term box, type in the term 'help', press Enter then download the csv again
    page.get_by_role("searchbox", name="Add a search term").click()
    page.get_by_role("searchbox", name="Add a search term").fill("help")
    page.get_by_role("searchbox", name="Add a search term").press("Enter")
    with page.expect_download() as download1_info:
        page.locator("widget").filter(has_text="Interest over time help_outline Help file_download code share ‪1 Jan 2004‬‪1 Oct").get_by_role("button", name="file_download").click()
    download1 = download1_info.value

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
