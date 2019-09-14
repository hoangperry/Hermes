from lxml.html import fromstring
import requests
from newspaper import Article

HTTP_PROXIES = [
    '5.202.158.3:80',
    '5.202.158.157:80'
]

HTTPS_PROXIES = [
    '182.52.51.47:45440',
    '5.202.149.198:80'
]

proxies = {
  'http': 'http://182.52.51.47:45440',
  'https': 'http://5.202.149.198:80',
}

url = 'https://www.chotot.com/quan-tan-phu/mua-ban-laptop/52356828.htm'
