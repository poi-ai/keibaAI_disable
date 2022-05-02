import requests
import time
from bs4 import BeautifulSoup

def get_soup(URL):
    '''指定したURLからHTMLタグをスクレイピングするメソッド。
       間隔をあけずに高頻度でアクセスしてしまうのを防ぐために
       必ずこのメソッドを経由してアクセスを行う

    Args:
        URL(str):抽出対象のURL
    
    Retuens:
        soup(bs4.BeautifulSoup):抽出したHTMLタグ
    
    '''
    time.sleep(2)
    r = requests.get(URL)
    return BeautifulSoup(r.content, 'lxml')