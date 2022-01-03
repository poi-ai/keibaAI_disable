import requests
import time
from bs4 import BeautifulSoup

def get_soup(URL):
    time.sleep(5)
    r = requests.get(URL)
    return BeautifulSoup(r.text, 'lxml')