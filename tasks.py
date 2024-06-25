import os
from robocorp.tasks import task
# from selenium.webdriver import Chrome, ChromeOptions
from RPA.Browser.Selenium import Selenium, ChromeOptions
from selenium.webdriver.common.by import By
from apnews_robot import APNewsRobot
from utils import save_dict_in_excel

class Settings:
    news_website: str = "APNEWS"
    phrase_to_search: str = "EUA Election"

@task
def minimal_task():
    news_robot = APNewsRobot()

    options = ChromeOptions()
    options.page_load_strategy = 'eager'
    
    browser = Selenium()
    browser.open_available_browser(options=options)
    browser.go_to(news_robot.url)
    
    news_robot.load_driver(browser.driver)
    news_robot.acept_onetrust_banner()
    news_robot.execute_search(Settings.phrase_to_search)

    results = news_robot.get_results()
    save_dict_in_excel([result.get_dict() for result in results], 'news')
