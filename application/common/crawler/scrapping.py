import os
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from requests.exceptions import SSLError
from selenium import webdriver
import urllib.parse
import re
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from application.common.crawler.proxies import list_proxies
from application.common.helpers import logger
from application.common.helpers.url import UrlFormatter
from selenium.webdriver.chrome.options import Options
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# pip3 install newspaper3k
import ssl
import random
# from newspaper import Article


# This restores the same behavior as before.
context = ssl._create_unverified_context()


class WebDriverWrapper:
    ignore_extension_regex = """.*(\.mng|\.pct|\.bmp|\.gif|\.jpg|\.jpeg|\.png|\.pst|\.psp|\.tif|\.tiff|\.ai|\.drw|\.dxf|\.eps|\.ps|\.svg|\.mp3|\.wma|\.ogg|\.wav|\.rar|\.aac|\.mid|\.au|\.aiff|\.3gp|\.asf|\.asx|\.avi|\.mov|\.mp4|\.mpg|\.qt|\.rm|\.swf|\.wmv|\.m4a|\.css|\.js|\.pdf|\.doc(x)?|\.xls(x)?|\.ppt(x)?|\.exe|\.bin|\.rss|\.zip|\.ra|\.txt)"""

    def __init__(self, executable_path=None):
        """

        :param executable_path:
        :param method:
        """
        prefs = {"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096}
        options = Options()
        options.binary_location = '/usr/bin/google-chrome'
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        #options.add_experimental_option("detach", True)
        options.add_experimental_option("prefs", prefs)

        # add execute path and option into driver
        self.executable_path = executable_path
        self.options = options

        if executable_path is not None:
            self.driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
            self.selenium = True
        else:
            # create driver but not use
            self.driver = None
            self.selenium = False

        # self.driver.implicitly_wait(60)
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
            logger.info_log.info("Close driver")
            # delete all cookies
            self.driver.close()
            self.driver.quit()
        except WebDriverException as ex:
            logger.error_log.exception("Cannot close browser {}".format(ex))
        finally:
            self.driver = None
            self.selenium = True
            os.system('killall chrome')

    def open_browser(self):
        """
        reopen browser
        :return:
        """
        if self.driver is None:
            try:
                logger.info_log.info("Open driver")

                self.driver = webdriver.Chrome(executable_path=self.executable_path,
                                               chrome_options=self.options)

                # restart wait
                self.wait = WebDriverWait(self.driver, 10)
            except WebDriverException as ex:
                logger.error_log.exception("Cannot open browser {}".format(ex))
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

        logger.info_log.info(url)

        url_formatter = UrlFormatter(url)
        self.domain = url_formatter.get_domain()
        self.page = url
        text = ""
        if self.selenium:

            self.open_browser()

            try:
                self.driver.get(url)
                self.wait.until(EC.visibility_of_element_located((By.TAG_NAME, 'h1')))
                time.sleep(wait)
                text = self.driver.page_source
            except TimeoutException as ex:
                logger.error_log.error("Time out exception: {}".format(ex))
                self.close_browser()
            except Exception as ex:
                logger.error_log.error("Page load exception {}".format(ex))
                self.close_browser()
        else:
            text = ''
            try:
                # article = Article(url)
                # article.download()
                # text = article.html
                r = requests.get(url, proxies=proxy)
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
                    #
                    text = urlopen(req, context=context).read().decode('utf-8')
                except Exception as ex:
                    logger.error_log.exception("Pageload exception {}".format(ex))
            except Exception as ex:
                logger.error_log.exception("Pageload exception {}".format(ex))
                logger.error_log.error(str(proxy))
                # self.response_html = BeautifulSoup(re.sub('<br\s*[\/]?>', '\n', text), "lxml")

        self.set_html(text)

    def set_html(self, html):
        self.response_html = BeautifulSoup(re.sub('<br\s*[\/]?>', '\n', html), "lxml")

    def get_elements(self, query, sep='\n'):
        try:
            rs_text = ''
            results = self.response_html.select(query)
            for result in results:
                rs_text = rs_text + sep + str(result)
            return rs_text.strip()
        except Exception as ex:
            logger.error_log.exception(str(ex))
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

            if self.domain in abs_url and \
                re.match(allow_pattern, abs_url) \
                and not re.match(WebDriverWrapper.ignore_extension_regex, abs_url):

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
                #print(rule['domain'])
                #print(value)
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
            except Exception as ex:
                results[key] = None

        return results

    def execute_script(self, script):
        if self.selenium:
            self.driver.execute_script(script)
            self.response_html = BeautifulSoup(re.sub('<br\s*[\/]?>', '\n', self.driver.page_source), "lxml")
