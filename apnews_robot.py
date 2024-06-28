from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
TimeoutException, StaleElementReferenceException)
from robocorp import log


import utils
from models import News

IGNORED_EXCEPTIONS = (StaleElementReferenceException)

class APNewsRobot:
    """Associated Press crawler"""
    def __init__(self):
        self.driver = None
        self.url = "https://apnews.com/"
        self.MAX_ATTEMPTS = 5

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

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'SearchResultsModule-results')
            )
        )

    def get_results(self):
        """Get and format news results
        
        :return: a list of formatted news items
        :rtype: News"""

        log.info(f"Extracting News from search results page")
        items = self.load_search_result_items()
        
        all_results = []
        attempts = 0
        while attempts <= self.MAX_ATTEMPTS:
            try: 
                for item in items:
                    news_item = self.apnews_element_parser(item)
                    all_results.append(news_item)
                    
                break
            except StaleElementReferenceException:
                log.warn(f"the attempt number {attempts} fail trying get items")
                all_results = []
                items = self.load_search_result_items()
                
                if attempts == self.MAX_ATTEMPTS:
                    raise 
                attempts += 1
                    
        return all_results


    def load_search_result_items(self):
        items = WebDriverWait(
            self.driver, 
            10, 
            ignored_exceptions=IGNORED_EXCEPTIONS
        ).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                ('.SearchResultsModule-results div.PageList-items-item'))
        ))

        return items

    def generate_news_files(self, news_list, excel_name, search_params):
        period = utils.get_period(search_params.months)
        results = []
        for news in news_list:
            if utils.is_date_within_period(news.post_datetime, period):
                results.append(news)

                if news.have_image():
                    utils.download_image(news.img_link, news.img_file_name)
        
        if len(results) > 0:
            utils.save_dict_in_excel(
                [result.get_dict() for result in results], 
                excel_name
            )
        else:
            utils.save_dict_in_excel(
                [{'results': 'not found'}], 'news_not_found')

    def apnews_element_parser(self, base_item_element):
        """Format a single item result 
        
        :param base_item_element"""
    
        apnews_item = News()

        apnews_item.title = self._parse_title(base_item_element)
        apnews_item.description = self._parse_description(base_item_element)
        apnews_item.post_datetime = self._parse_post_datetime(base_item_element)
        apnews_item.img_link = self._parse_img_link(base_item_element)

        if apnews_item.have_image():
            apnews_item.img_file_name =  f'{apnews_item.code}.webp' 
        else:
            apnews_item.img_file_name = "Image Not Found"

        apnews_item.have_money_values = utils.check_money_values(
            " ".join([apnews_item.title, apnews_item.description])
        )

        apnews_item.count_of_search_phrase = utils.count_occurrences(
            self.search_params.phrase,
            " ".join([apnews_item.title, apnews_item.description])
        )
        log.info(f"Item {apnews_item} extracted")
        return apnews_item
        

    def _parse_title(self, item_content):
        try:
            title = item_content.find_element(By.CLASS_NAME, 'PagePromoContentIcons-text').text
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
            description = item_content.find_element(By.CLASS_NAME, 'PagePromo-description').text
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
            timestamp_str = item_content\
                .find_element(By.TAG_NAME, 'bsp-timestamp')\
                    .get_attribute('data-timestamp')

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
            img_link = base_item_element.find_element(By.CLASS_NAME, 'Image').get_attribute('src')
            return img_link
        except (NoSuchElementException, TimeoutException):
            log.warn("News without image")
            return None
