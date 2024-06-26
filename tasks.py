from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium, ChromeOptions
from apnews_robot import APNewsRobot
from utils import save_dict_in_excel

def get_search_params():
    return {
        "phrase_to_search": "EUA Elections",
        "months": 1
    }

@task
def minimal_task():
    search_params = get_search_params()
    news_robot = APNewsRobot()

    options = ChromeOptions()
    options.page_load_strategy = 'eager'
    
    browser = Selenium()
    browser.open_available_browser(options=options)
    browser.go_to(news_robot.url)
    
    news_robot.load_driver(browser.driver)
    news_robot.acept_onetrust_banner()
    news_robot.execute_search(search_params)

    results = news_robot.get_results()
    if len(results) > 0:
        save_dict_in_excel([result.get_dict() for result in results], 'news')
    else:
        save_dict_in_excel([{'results': 'not found'}], 'news_not_found')
