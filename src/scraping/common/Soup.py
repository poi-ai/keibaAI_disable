import requests
from bs4 import BeautifulSoup

def get_soup(URL):
    r = requests.get(URL)
    return BeautifulSoup(r.text, 'lxml')