import datetime
import pandas as pd
import package
import time
import traceback
import requests
from bs4 import BeautifulSoup
from common import babacodechange, jst, logger, writecsv, pd_read

class Jra():
    '''中央競馬オッズ取得クラス

    Class Parameter:
       RACE_DATE(str):keiba.goのGETリクエストの日付パラメータ

    Instance Parameter:
       baba_parameter(list<str>) : 各競馬場のレース一覧ページのPOSTパラメータ
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_get_time(datetime) : 次回オッズ取得時刻
       write_data(DataFrame) : 書き込み用データ
    '''
    # オッズ関連ページのURL
    ODDS_URL = 'https://www.jra.go.jp/JRADB/accessO.html'

    def __init__(self):
        logger.info('----------------------------')
        logger.info('中央競馬オッズ記録システム起動')
        logger.info('初期処理開始')
        self.__baba_parameter = []
        self.__race_info = []
        self.__next_get_time = 0
        self.__write_data = pd.DataFrame(columns = ['レースID','馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ', '記録時刻', 'JRAフラグ'])
        self.get_url()

    @property
    def baba_parameter(self):
        return self.__baba_parameter

    @property
    def next_get_time(self):
        return self.__next_get_time

    @property
    def race_info(self):
        return self.__race_info

    @property
    def write_data(self):
        return self.__write_data

    @next_get_time.setter
    def next_get_time(self, next_get_time):
        self.__next_get_time = next_get_time

    @write_data.setter
    def write_data(self, write_data):
        self.__write_data = write_data

    def do_action(self, cname):
        '''POSTリクエストを送り、HTML情報を受け取る

        Args:
            cname(str):POSTパラメータ

        Returns:
            soup(bs4.BeautifulSoup):受け取ったHTML
        '''

        r = requests.post(self.ODDS_URL, data = {'cname':cname})
        r.encoding = r.apparent_encoding
        return BeautifulSoup(r.text, 'lxml')

    def get_url(self):
        '''稼働日の各競馬場のレースリストページのパラメータを取得する'''

        # 今週の開催リストを取得
        soup = self.do_action('pw15oli00/6D')
        thisweek = soup.find('div', class_='thisweek')

        # 稼働日と合致する日付の枠番号(上から何番目か)を取得
        soup = BeautifulSoup(str(thisweek), 'lxml')
        kaisai_dates = soup.find_all('h3')

        today_position = -1

        for i, kaisai_date in enumerate(kaisai_dates):
            # TODO 平日に動作確認のためコメントアウト
            # if jst.month() == word_cut(str(kaisai_date), '>', '月') and jst.day() == word_cut(str(kaisai_date), '月', '日'):
                today_position = i
                break

        # 合致した枠内のリンクを取得
        kaisai_lists = BeautifulSoup(str(soup.find_all('div', class_='link_list multi div3 center')[i]), 'lxml')
        for kaisai_list in kaisai_lists:
            # TODO
            pass
        exit()
        time.sleep(3)

# TODO common行き
def word_cut(word, start_letter, end_letter):
    '''特定の文字から特定の文字までの間を切り出す'''
    return word[word.find(start_letter) + 1: word.find(end_letter)]

# 動作確認用
if __name__ == '__main__':

    # ログ用インスタンス作成
    logger = logger.Logger()

    # 中央競馬用インスタンス作成
    try:
        jra = Jra()
    except Exception as e:
        logger.error('初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        exit()