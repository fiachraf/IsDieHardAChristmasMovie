
from playwright.sync_api import Playwright, sync_playwright, expect
import pathlib

#gets the path of this file
thisPath = pathlib.Path(__file__).parent.resolve()
# by default just use test as the first search term
trendTerm = 'test'

# def run(playwright: Playwright) -> None:
#
#     #commented out as new context creates it with no cookies
#     #context = browser.new_context()
#     #page = context.new_page()
#
#     # try get some cookies so that google trends doesn't block me
#     #context.cookies()
#     page.goto("https://docs.python.org/3/reference/datamodel.html")
#
#     #seems that google is able to detect my bot and I need to click refresh and then it will continue for at least 2 search terms
#
#     #go to first page
#     # google trends urls have a pattern, this one looks for data from all time, worldwide
#     page.goto("https://trends.google.com/trends/explore?date=all&q=test&hl=en-GB")
#     #click the download csv file
#     with page.expect_download() as download_info:
#         page.locator("widget").filter(has_text="Interest over time help_outline Help file_download code share ‪1 Jan 2004‬‪1 Oct").get_by_role("button", name="file_download").click()
#     download = download_info.value
#     download.save_as(f'{thisPath}/{trendTerm}.csv')
#     # click the search term box, type in the term 'help', press Enter then download the csv again
#     page.get_by_role("searchbox", name="Add a search term").click()
#     page.get_by_role("searchbox", name="Add a search term").fill("help")
#     page.get_by_role("searchbox", name="Add a search term").press("Enter")
#     with page.expect_download() as download1_info:
#         page.locator("widget").filter(has_text="Interest over time help_outline Help file_download code share ‪1 Jan 2004‬‪1 Oct").get_by_role("button", name="file_download").click()
#     download1 = download1_info.value
#
#     # ---------------------
#     context.close()
#     browser.close()

def gotoGTrend(GTrendPage):
    #go to first page
    # google trends urls have a pattern, this one looks for data from all time, worldwide
    GTrendPage.goto("https://trends.google.com/trends/explore?date=all&q=test&hl=en-GB")
    #As the page is being passed as an object between the functions I shouldn't have to return anything
    if GTrendPage.get_by_text("That's an error").count() > 0:
        print('Error occured, waiting for human intervention')
        dummy = input('check web browser, maybe it needs to be refreshed')
    return None

def dlTrendCSV(GTrendPage, thisPath, trendTerm):
    #click the download csv file
    with GTrendPage.expect_download() as download_info:
        GTrendPage.locator("widget").filter(has_text="Interest over time help_outline Help file_download code share ‪1 Jan 2004‬‪1 Oct").get_by_role("button", name="file_download").click()
    download = download_info.value
    download.save_as(f'{thisPath}/{trendTerm}.csv')
    return None

def searchNewTrend(GTrendPage, newTerm):
    # click the search term box, type in the term 'help', press Enter then download the csv again
    GTrendPage.get_by_role("searchbox", name="Add a search term").click()
    GTrendPage.get_by_role("searchbox", name="Add a search term").fill("help")
    GTrendPage.get_by_role("searchbox", name="Add a search term").press("Enter")

    if GTrendPage.get_by_text("That's an error").count() > 0:
        print('Error occured, waiting for human intervention')
        dummy = input('check web browser, maybe it needs to be refreshed')
    # page.get_by_text("429. That’s an error.").click()
    # page.get_by_text("429.").click()
    # page.get_by_text("That’s an error.").click()
    return None

def main():
    with sync_playwright() as playwright:
        #run(playwright)
        #create a headed browser so I can click refresh so it won't think I'm a bot
        browser = playwright.firefox.launch(headless=False)
        page = browser.new_page()
        #gets the path of this file
        thisPath = pathlib.Path(__file__).parent.resolve()
        # by default just use test as the first search term
        trendTerm = 'test'
        trendTerm2 = 'chicken'
        gotoGTrend(page)
        # #force it to wait for me to reload the page and then enter anything
        # dummy = input('refresh the page and then press enter here')
        dlTrendCSV(page, thisPath, trendTerm)
        searchNewTrend(page, trendTerm2)
        dlTrendCSV(page, thisPath, trendTerm2)

        browser.close()
        return None


if __name__ == '__main__':
    main()
