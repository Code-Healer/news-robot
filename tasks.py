from robocorp.tasks import task
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import ChromiumOptions

from apnews_robot import APNewsRobot

class Settings:
    news_website: str = "APNEWS"
    phrase_to_search: str = "EUA Election"

@task
def minimal_task():
    options = ChromiumOptions()
    options.page_load_strategy = 'eager'
    with Chrome(options=options) as driver:
        news_robot = APNewsRobot(driver)
        news_robot.open_website()
        news_robot.execute_search(Settings.phrase_to_search)
        results = news_robot.get_results()
