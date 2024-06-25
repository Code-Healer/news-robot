from selenium.webdriver.common.by import By

class APNewsRobot:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://apnews.com/"

    def open_website(self):
        self.driver.get(self.url)

    def execute_search(self, phrase_to_search):
        search_btn = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-button'
        )
        search_btn.click()

        search_input = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-input'
        )
        search_input.send_keys(phrase_to_search)

        search_submit = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-submit'
        )
        search_submit.click()