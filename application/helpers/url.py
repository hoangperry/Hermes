import hashlib
import re
import urllib.parse
from urllib.parse import urlparse
from urllib.parse import urlsplit


class UrlFormatter(object):

    def __init__(self, url):
        """
        Init url parse
        Document: https://docs.python.org/3/library/urllib.parse.html#url-parsing
        :param url:
        """

        self.url = url
        self.parsed_url = urllib.parse.urlparse(url)
        self.base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url))

    def get_homepage(self):
        return self.base_url

    def get_host(self):
        """
        Get host from url
        ex: https://en.wikipedia.org/wiki/Levenshtein_distance
        return: en.wikipedia.org
        :return:
        """

        if self.url is None or urlparse(self.url.__str__()).hostname == '':
            return None
        return urlparse(self.url.__str__()).hostname

    def get_domain(self):
        """
        Get domain from given url
        ex: https://en.wikipedia.org/wiki/Levenshtein_distance
        return: wikipedia.org
        :return:
        """
        host_self = self.get_host()
        if host_self is None:
            return host_self
        if '.' not in host_self[:4]:
            return host_self
        else:
            return re.compile(r'^\w+\.').split(host_self)[1]

    def get_subdomain(self):
        """
        Get subdomain
        ex: https://en.wikipedia.org/wiki/Levenshtein_distance
        return: en
        :return:
        """
        if '.' in self.get_host()[:4]:
            return re.compile(r'\.').split(self.get_host())[0]
        else:
            return None

    def get_protocol(self):
        """
        Get protocol
        ex: https://en.wikipedia.org/wiki/Levenshtein_distance
        return: https
        :return:
        """

        if urlparse(self.url.__str__()).scheme == '':
            return 'http'
        else:
            return urlparse(self.url.__str__()).scheme

    def get_path(self):
        """
        Get path from url
        ex: https://en.wikipedia.org/wiki/Levenshtein_distance#Approximation
        return: Approximation
        :return:
        """
        if self.url is None or '#' not in self.url.__str__():
            return None
        return urlparse(self.url.__str__()).path

    def get_port(self):
        """
        Get port from url
        Default port: 8000
        ex: https://en.wikipedia.org:8888/wiki/Levenshtein_distance#Approximation
        return: 8888
        :return:
        """
        if re.compile(r':\d{1,4}/').findall(self.url.__str__()) is None:
            return '8000'
        else:
            return re.compile(r':\d{1,4}/').findall(self.url.__str__())[0][1:-1]

    def get_query(self):

        if self.url is None or '#' not in self.url.__str__():
            return None
        return urlparse(self.url.__str__()).query

    def normalize(self):
        """
        Normalize url
        1. Remove default port: web:80.com => web.com
        2. Add slash: web.com => web.com/
        3. Remove fragment: web.com/content.html#link => web.com/content.html
        4. Remove default name: web.com/index.html => web.com
        5. Decode: web.com/%7Ekim => web.com/~kim
        6. Encode space: web.com/tan kim => web.com/tan%20kim
        7. Remove www.
        To lower: WEB.COM => web.com
        :return: normalized url as string
        """
        normurl = self.url.__str__()
        # return urllib.urlunparse(urlparse(normurl))
        # 1. Remove default port
        # if re.compile(r'\:\d{1,4}\/').search(normurl):
        normurl = re.sub(r':\d{1,4}', '', normurl)

        # 3. Remove fragment
        normurl = re.sub(r'#.+', '', normurl)

        # 4. Remove default name
        normurl = re.sub(r'/index\.html', '', normurl)

        # 5. Decode: %xx
        normurl = urllib.parse.unquote(normurl)

        # 6. Encode spaces
        if ' ' in self.url.__str__():
            # normurl = urllib.parse.quote(normurl, safe= "_.-~/:@")
            normurl = re.sub(r'\s', '%20', normurl)

        # 2. Add slash
        # if normurl[-1] != '/':
        #    normurl += '/'

        # if "www\." in normurl:
        #     normurl = re.sub(r'www\.', '', normurl)

        return normurl
