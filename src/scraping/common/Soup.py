import requests
import time
from bs4 import BeautifulSoup

def get_soup(URL):
    '''指定したURLからHTMLタグをスクレイピングするメソッド。
       GETの際にsleepを忘れると大変なことになるので、
       必ずこのメソッドを呼び出す形でGETを行う。

    Args:
        URL(str):抽出対象のURL
    
    Retuens:
        soup(bs4.BeautifulSoup):抽出したHTMLタグ
    
    '''
    time.sleep(2)
    r = requests.get(URL)
    return BeautifulSoup(r.content, 'lxml')