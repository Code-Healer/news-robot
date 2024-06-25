from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException 

from utils import download_image
from models import News

class APNewsRobot:
    def __init__(self):
        self.driver = None
        self.url = "https://apnews.com/"

    def load_driver(self, driver):
        self.driver = driver    
    
    def execute_search(self, phrase_to_search):
        search_btn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'SearchOverlay-search-button'))
        )
        self.driver.get_screenshot_as_file('output/coockies_img.png')
        search_btn.click()

        search_input = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-input'
        )
        search_input.send_keys(phrase_to_search)

        search_submit = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-submit'
        )
        search_submit.click()

    def get_results(self):
        items = self.driver.find_elements(
        By.CSS_SELECTOR, 
            ('div.SearchResultsModule-results div.PageList-items '
            'div.PageList-items-item')
        )
        results = []
        for item in items:
            news_item = self.apnews_element_parser(item)
            if news_item.have_image():
                download_image(news_item.img_link, news_item.img_file_name)
            
            results.append(news_item)
        
        return results

    def apnews_element_parser(self, base_item_element):
        content = base_item_element.find_element(
            By.CSS_SELECTOR, 'div.PagePromo-content'
        )
        apnews_item = News()
        
        apnews_item.title = content.find_element(
            By.CSS_SELECTOR,
            "div.PagePromo-title span.PagePromoContentIcons-text"
        ).text

        print(f"Parsing data to:{apnews_item.title}...")

        apnews_item.description = content.find_element(
            By.CSS_SELECTOR,
            "div.PagePromo-description span.PagePromoContentIcons-text"
        ).text

        timestamp_str = content.find_element(
            By.CSS_SELECTOR,
            'div.PagePromo-date bsp-timestamp'
        ).get_dom_attribute('data-timestamp')

        apnews_item.post_datetime = datetime.fromtimestamp(int(timestamp_str) / 1e3)
        
        try: 
            media = base_item_element.find_element(
                By.CSS_SELECTOR, 'div.PagePromo>div.PagePromo-media'
            )
            
            apnews_item.img_link = media.find_element(
                By.CSS_SELECTOR, 'img.Image'
            ).get_dom_attribute('src')
        except NoSuchElementException:
            apnews_item.img_link = None

        apnews_item.img_file_name = f'{apnews_item.code}.webp'

        return apnews_item