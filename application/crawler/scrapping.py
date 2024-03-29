import os
import re
import ssl
import time
import random
import requests
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from requests.exceptions import SSLError
from urllib.request import Request, urlopen
from selenium.webdriver.common.by import By
from application.helpers.url import UrlFormatter
from application.helpers.logger import get_logger
from application.crawler.configs import list_proxies
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, WebDriverException

# This restores the same behavior as before.
context = ssl._create_unverified_context()
logger = get_logger('Scraping', logger_name=__name__)


# def get_list_proxy():
#     return [
#         [
#             'http://kinnt93:147828@{}'.format(line.strip()),
#             'https://kinnt93:147828@{}'.format(line.strip())
#         ]
#         for line in
#         open('proxies.txt', mode='r').readlines()
#     ]


class WebDriverWrapper:
    ignore_extension_regex = r""".*(\.mng|\.pct|\.bmp|\.gif|\.jpg|\.jpeg|\.png|\.pst|\.psp|\.tif|\.tiff|\.ai|\.drw
    |\.dxf|\.eps|\.ps|\.svg|\.mp3|\.wma|\.ogg|\.wav|\.rar|\.aac|\.mid|\.au|\.aiff|\.3gp|\.asf|\.asx|\.avi|\.mov|\.mp4
    |\.mpg|\.qt|\.rm|\.swf|\.wmv|\.m4a|\.css|\.js|\.pdf|\.doc(x)?|\.xls(x)?|\.ppt(
    x)?|\.exe|\.bin|\.rss|\.zip|\.ra|\.txt)"""

    def __init__(self,
                 executable_path=None,
                 headless=True,
                 # binary_location='/usr/bin/google-chrome',
                 disable_gpu=True,
                 timeout=15):

        prefs = {"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096}
        options = Options()
        # options.binary_location = binary_location
        if headless:
            options.add_argument('--headless')

        if disable_gpu:
            options.add_argument('--disable-gpu')
        # list_proxy = random.choice(get_list_proxy())
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-dev-shm-usage')
        # options.add_experimental_option("detach", True)
        options.add_experimental_option("prefs", prefs)
        # selenium_wire_option = {
        #     'proxy': {
        #         'http': list_proxy[0],
        #         'https': list_proxy[1],
        #     },
        # }
        # add execute path and option into driver
        self.executable_path = executable_path
        self.options = options
        self.html = None
        if executable_path is not None:
            self.driver = webdriver.Chrome(
                executable_path=executable_path,
                chrome_options=options,
                # seleniumwire_options=selenium_wire_option,
            )
            self.selenium = True
        else:
            # create driver but not use
            self.driver = None
            self.selenium = False

        # self.driver.implicitly_wait(60)
        self.driver.set_page_load_timeout(timeout)
        self.wait = WebDriverWait(self.driver, 10)
        self.response_html = None
        self.all_links = []
        self.page = None
        self.domain = None

    def use_selenium(self, selenium):
        self.selenium = selenium

    def close_browser(self):
        """
        Close selenium driver when exception
        :return:
        """
        try:
            logger.info("Close driver")
            # delete all cookies
            if self.driver is not None:
                self.driver.close()
                self.driver.quit()
        except Exception as ex:
            logger.exception("Cannot close browser {}".format(ex))
        finally:
            self.driver = None
            self.selenium = True
            os.system('killall chrome')
            os.system('killall chromedriver')

    def open_browser(self):
        """
        reopen browser
        :return:
        """
        if self.driver is None:
            try:
                logger.info("Open driver")

                self.driver = webdriver.Chrome(executable_path=self.executable_path,
                                               chrome_options=self.options)

                # restart wait
                self.wait = WebDriverWait(self.driver, 10)
            except WebDriverException as ex:
                logger.exception("Cannot open browser {}".format(ex))
                self.close_browser()

    def get(self, url, wait=0):
        """
        Get html from web url
        :param url:
        :param wait:
        :return:
        """

        # random proxy
        proxy = random.choice(list_proxies)

        url_formatter = UrlFormatter(url)
        self.domain = url_formatter.get_domain()
        if self.domain is None:
            self.driver = None
            return
        self.page = url
        text = ""
        if self.selenium:

            self.open_browser()

            try:
                self.driver.get(url)
                self.wait.until(expected_conditions.visibility_of_element_located((By.TAG_NAME, 'h1')))
                time.sleep(wait)
                text = self.driver.page_source
            except TimeoutException as ex:
                logger.error("Time out exception: {}".format(ex))
                self.close_browser()
            except Exception as ex:
                logger.error("Page load exception {}".format(ex))
                self.close_browser()
        else:
            text = ''

            try:
                # article = Article(url)
                # article.download()
                # text = article.html
                r = requests.get(url)
                text = r.content.decode()
                if text.strip() == '':
                    r = requests.get(url, headers={"User-Agent": "Requests"}, proxies=proxy)
                    text = r.content.decode()

                    # if can not find, try another method
                    if text.strip() == '':
                        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        req.set_proxy(proxy["http"], "http")
                        req.set_proxy(proxy["https"], "https")
                        text = urlopen(req, context=context).read().decode('utf-8')
            except SSLError:
                try:
                    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    # # set proxy
                    # req.set_proxy(proxy["http"], "http")
                    # req.set_proxy(proxy["https"], "https")

                    text = urlopen(req, context=context).read().decode('utf-8')
                except Exception as ex:
                    logger.error_log.exception("Pageload exception {}".format(ex))
            except Exception as ex:
                logger.exception("Pageload exception {}".format(ex))
                logger.error(str(proxy))
                # self.response_html = BeautifulSoup(re.sub('<br\s*[\/]?>', '\n', text), "lxml")

        self.set_html(text)

    def set_html(self, html):
        html = re.sub(r'<br\s*[/]?>', '\n', html)
        html = re.sub(r'<\s*/p>', '\n</p>', html)
        self.response_html = BeautifulSoup(html, "lxml")

    def get_elements(self, query, sep='\n'):
        try:
            rs_text = ''
            results = self.response_html.select(query)
            for result in results:
                rs_text = rs_text + sep + str(result)
            return rs_text.strip()
        except Exception as ex:
            logger.exception(str(ex))
            return None

    def select_text(self, query, sep=' '):
        """
        Select text from query
        :param query:
        :param sep:
        :return:
        """
        try:
            rs_text = ''
            results = self.response_html.select(query)
            for result in results:
                rs_text = rs_text + sep + result.getText()
            return rs_text.strip()
        except Exception:
            return None

    def test_select(self, query):
        return self.response_html.select(query)

    def select_first(self, query):
        """
        Get first element from query
        :param query:
        :return:
        """
        try:
            return self.response_html.select(query)[0].getText()
        except Exception:
            return None

    def get_links(self, allow_pattern='.*'):
        """
        Get all links from current page
        All links not matched regex will be removed
        :param allow_pattern:
        :return:
        """
        self.all_links = self.response_html.find_all("a", href=True)
        selected_links = set()
        for link in self.all_links:
            # get absolute url
            abs_url = urllib.parse.urljoin(self.page, link.get('href'))

            if not (not (self.domain in abs_url) or not re.match(allow_pattern, abs_url) or re.match(
                    WebDriverWrapper.ignore_extension_regex, abs_url)):
                selected_links.add(UrlFormatter(abs_url).normalize())

        return list(selected_links)

    def scrape(self, rule: dict):
        """
        Scrape data from given html by using selector (input dictionary)
        Return a dictionary of selected elements
        :param rule: rule as dictionary. ex: {title: h1, content: div}
        :return: dictionary of scraped data {title: this is title of page, content: this is a content page}
        """
        results = dict()
        for key, value in rule.items():
            try:
                text = self.select_text(value)
                if text == '':
                    results[key] = None
                else:
                    results[key] = self.select_text(value)
            except Exception:
                results[key] = None

        return results

    def scrape_elements(self, rule: dict):
        """
        Scrape data from given html by using selector (input dictionary)
        Return a dictionary of selected elements
        :param rule: rule as dictionary. ex: {title: h1, content: div}
        :return: dictionary of scraped data {title: this is title of page, content: this is a content page}
        """
        results = dict()
        for key, query in rule.items():
            try:
                if key.startswith('pre'):
                    if query is None or query == 'null':
                        results[key] = None
                    else:
                        results[key] = query
                else:
                    if query is None or query == 'null':
                        results[key] = None
                    else:
                        attr_matcher = re.match(".*(attr:(.+))$", query)

                        # element = None
                        if attr_matcher:
                            query = query.replace(attr_matcher.group(1), '').strip()
                            attr_key = attr_matcher.group(2)
                            elements = self.response_html.select(query)
                            selected_elements = []
                            for element in elements:
                                selected_elements.append(element.get(attr_key))
                        else:
                            elements = self.response_html.select(query)
                            selected_elements = []
                            for element in elements:
                                selected_elements.append(element.getText().strip())

                            if key == 'title' and len(selected_elements) == 0:
                                selected_elements.append(self.response_html.title.string)

                        # check selected element is null or not
                        # if null, assign null to dictionary, then
                        if len(selected_elements) == 0:
                            results[key] = None
                        else:
                            results[key] = selected_elements
            except:
                results[key] = None

        return results

    def execute_script(self, script):
        if self.selenium:
            self.driver.execute_script(script)
            self.response_html = BeautifulSoup(re.sub(r'<br\s*[/]?>', '\n', self.driver.page_source), "lxml")

    def get_html(self, url):
        try:
            self.driver.get(url)
            page_source = self.driver.page_source
            page_source = re.sub(r'<br\s*[/]?>', '\n', page_source)
            page_source = re.sub(r'<\s*/p>', '</p>\n', page_source)

            self.html = BeautifulSoup(page_source, "lxml")
            time.sleep(0.5)
        except TimeoutException as toe:
            print(toe)
            self.driver.refresh()
            print(url)
        except Exception as ex:
            print(ex)
