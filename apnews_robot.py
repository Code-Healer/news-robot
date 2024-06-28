from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
TimeoutException, StaleElementReferenceException)
from robocorp import log


from utils import (
    download_image, get_period, is_date_within_period, check_money_values, 
    count_occurrences
)
from models import News

IGNORED_EXCEPTIONS = (StaleElementReferenceException)

class APNewsRobot:
    """Associated Press crawler"""
    def __init__(self):
        self.driver = None
        self.url = "https://apnews.com/"

    def load_driver(self, driver):
        self.driver = driver
    
    def dismiss_onetrust_banner(self):
        """function to dismiss privacy popup, clicking in 'I Agree' button"""

        self.driver.get_screenshot_as_file('output/onetrust_popup.png')
        try:
            onetrust_privacy_popup_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(
                    (By.ID, 'onetrust-accept-btn-handler')
                )
            )

            self.driver.get_screenshot_as_file('output/onetrust_popup.png')
            onetrust_privacy_popup_btn.click()
            log.info("onetrust banner open and dismissed")
        except NoSuchElementException:
            log.warn("onetrust banner didn't open: Not Found")
        except TimeoutException:
            log.warn("onetrust banner didn't open: Timeout")

    def execute_search(self, search_params):
        """execute main search in site
        
        :param SearchParamsAdapter search_params: The params to search
        """
        
        log.info(f"searching by {search_params.phrase}")
        self.search_params = search_params
        search_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'SearchOverlay-search-button'))
        )
        
        search_btn.click()        

        search_input = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-input'
        )
        search_input.send_keys(self.search_params.phrase)

        search_submit = self.driver.find_element(
            By.CLASS_NAME, 'SearchOverlay-search-submit'
        )
        search_submit.click()

    def select_sort_by_options(self):
        """Define sort by option that must be in ['Relevance, Newest, Oldest]"""
        
        log.info(f"sort by: {self.search_params.sort_by}")
        sort_by_dropdown_el = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, 'Select-input')
            )
        )

        select = Select(sort_by_dropdown_el)
        select.select_by_visible_text(self.search_params.sort_by)

    def get_results(self):
        """Get and format news results
        
        :return: a list of formatted news items
        :rtype: News"""

        log.info(f"Extracting News from search results page")

        items = WebDriverWait(
            self.driver, 
            10, 
            ignored_exceptions=IGNORED_EXCEPTIONS
        ).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 
                ('div.SearchResultsModule-results div.PageList-items '
                'div.PageList-items-item'))
        ))
        
        results = []
        for item in items:
            news_item = self.apnews_element_parser(item)
            period = get_period(self.search_params.months)
            if is_date_within_period(news_item.post_datetime, period):
                results.append(news_item)

                if news_item.have_image():
                    download_image(news_item.img_link, news_item.img_file_name)
                    
        return results

    def apnews_element_parser(self, base_item_element):
        """Format a single item result 
        
        :param base_item_element"""

        try:
            content = WebDriverWait(
                base_item_element, 
                20, 
                ignored_exceptions=IGNORED_EXCEPTIONS
            ).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 'div.PagePromo>div.PagePromo-content'
                    )
                )
            )

            apnews_item = News()

            apnews_item.title = self._parse_title(content)
            apnews_item.description = self._parse_description(content)
            apnews_item.post_datetime = self._parse_post_datetime(content)
            apnews_item.img_link = self._parse_img_link(base_item_element)

            if apnews_item.have_image():
                apnews_item.img_file_name =  f'{apnews_item.code}.webp' 
            else:
                apnews_item.img_file_name = "Image Not Found"

            apnews_item.have_money_values = check_money_values(
                " ".join([apnews_item.title, apnews_item.description])
            )

            apnews_item.count_of_search_phrase = count_occurrences(
                self.search_params.phrase,
                " ".join([apnews_item.title, apnews_item.description])
            )
            log.info(f"Item {apnews_item} extracted")
            return apnews_item
        except Exception as err:
            err_class = type(err).__name__
            log.exception("Error raised during CONTENT item parsing:", 
                          err_class)
            
            raise

    def _parse_title(self, item_content):
        try: 
            title = item_content.find_element(
                By.CSS_SELECTOR,
                "div.PagePromo-title span.PagePromoContentIcons-text"
            ).text
        except NoSuchElementException:
            log.warn("post without title")
            title = "Post without Title"
        except Exception as err:
            err_class = type(err).__name__
            log.exception("Error raised parsing TITLE:", 
                          err_class)
            
            raise

        return title

    def _parse_description(self, item_content):
        description = ""
        try: 
            description = item_content.find_element(
                By.CSS_SELECTOR,
                "div.PagePromo-description span.PagePromoContentIcons-text"
            ).text
        except NoSuchElementException:
            log.warn("Post without DESCRIPTION...")
            description = "Post without description"

        except Exception as err:
            err_class = type(err).__name__
            log.exception("Error raised parsing DESCRIPTION:",
                          err_class)

            raise

        return description

    def _parse_post_datetime(self, item_content):
        try:
            timestamp_str = item_content.find_element(
                By.CSS_SELECTOR,
                'div.PagePromo-date bsp-timestamp'
            ).get_dom_attribute('data-timestamp')

            return datetime.fromtimestamp(int(timestamp_str) / 1e3)
        except NoSuchElementException:
            log.warn("News without date field")
            return None

        except Exception as err:
            err_class = type(err).__name__
            log.exception("Error raised parsing POST DATE:",
                          err_class)

            raise

    def _parse_img_link(self, base_item_element):
        try:
            media = WebDriverWait(
                base_item_element, 
                5,
                ignored_exceptions=IGNORED_EXCEPTIONS).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'div.PagePromo>div.PagePromo-media')
            ))
            
            img_link = media.find_element(By.CSS_SELECTOR, 'img.Image')\
                .get_dom_attribute('src')
            
            return img_link
        except (NoSuchElementException, TimeoutException):
            log.warn("News without image")
            return None
