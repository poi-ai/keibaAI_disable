import requests
import time
from bs4 import BeautifulSoup

def get_soup(URL):
    time.sleep(2)
    r = requests.get(URL)
    return BeautifulSoup(r.content, 'lxml')

def del_tag(soup):
    text = soup.get_text(strip = False)
    return text