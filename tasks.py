from robocorp import workitems, log
from robocorp.tasks import task
from RPA.Browser.Selenium import Selenium, ChromeOptions
from apnews_robot import APNewsRobot
from utils import save_dict_in_excel
from search_adapter import SearchParamsAdapter

def get_search_params():
    """
    a function to get search params from work items or other sources.

    Item payload:
    {
        "phrase": "Lorem ipsum dolor sit amet",
        "months": positive integer,
        "sort_by": "Relevance | Newest | Oldest
    }
    """
    search_params = SearchParamsAdapter(workitems.inputs.current.payload)
    return search_params

@task
def minimal_task():
    search_params = get_search_params()

    search_params.get_dict()
    news_robot = APNewsRobot()

    options = ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-extensions")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    browser = Selenium()
    browser.open_available_browser(options=options)

    log.info(f"Starting Browser in: {news_robot.url}")
    browser.go_to(news_robot.url)
    
    news_robot.load_driver(browser.driver)

    news_robot.dismiss_onetrust_banner()
    news_robot.execute_search(search_params)
    news_robot.select_sort_by_options()   

    results = news_robot.get_results()
    if len(results) > 0:
        save_dict_in_excel([result.get_dict() for result in results], 'news')
    else:
        save_dict_in_excel([{'results': 'not found'}], 'news_not_found')
