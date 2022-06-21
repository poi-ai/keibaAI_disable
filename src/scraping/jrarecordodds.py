import datetime
import itertools
import pandas as pd
import package
import time
import traceback
import re
import requests
from bs4 import BeautifulSoup
from common import babacodechange, jst, logger, writecsv, pd_read

class Jra():
    '''中央競馬オッズ取得クラス

    Class Parameter:
       ODDS_URL(str) : JRAのオッズ関連ページの共通URL
       RACE_CARD_URL(str) : JRAの出馬表関連ページの共通URL

    Instance Parameter:
       odds_param(list<str>) : 各競馬場のレース一覧ページ(オッズ)のPOSTパラメータ
       info_param(list<str>) : 各競馬場のレース一覧ページ(出馬表)のPOSTパラメータ
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_get_time(datetime) : 次回オッズ取得時刻
       write_data(DataFrame) : 出力まで一時保存するオッズデータ
    '''
    # オッズ関連ページのURL
    ODDS_URL = 'https://www.jra.go.jp/JRADB/accessO.html'
    # 出馬表関連ページのURL
    RACE_CARD_URL = 'https://www.jra.go.jp/JRADB/accessD.html'

    def __init__(self):
        logger.info('----------------------------')
        logger.info('中央競馬オッズ記録システム起動')
        logger.info('初期処理開始')
        self.__odds_param = []
        self.__info_param = []
        self.__race_info = []
        self.__next_get_time = 0
        self.__write_data = pd.DataFrame(columns = ['レースID','馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ', '記録時刻', 'JRAフラグ'])
        self.get_param('odds')
        self.get_param('info')

    @property
    def odds_param(self):
        return self.__odds_param

    @property
    def info_param(self):
        return self.__info_param

    @property
    def next_get_time(self):
        return self.__next_get_time

    @property
    def race_info(self):
        return self.__race_info

    @property
    def write_data(self):
        return self.__write_data

    @odds_param.setter
    def odds_param(self, odds_param):
        self.__odds_param = odds_param

    @info_param.setter
    def info_param(self, info_param):
        self.__info_param = info_param

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

    def extract_param(self, html):
        '''HTMLからdoActionの第二引数を抽出する

        Args:
            html(strに変換可能な型):抽出元のHTMLコード

        Returns:
            param(list<str>):抽出した第二引数のリスト
        '''
        param = [m.group(1) for m in re.finditer('access.\.html\', \'(\w+/\w+)', str(html))]

        return param
        # 一次元化して返す(後々必要？)
        # return list(itertools.chain.from_iterable(param))

    def get_param(self, page_type):
        '''稼働日の各競馬場のレースリストページのパラメータを取得する

        Args:
            page_type(str):サイトの種類
                           odds:オッズ関連ページ,info:出馬表関連ページ

        '''
        # 今週の開催一覧ページのHTMLを取得
        # TODO 出馬表ページ(info)にはthisweekタグがないため要検討
        if page_type == 'odds':
            soup = self.do_action('pw15oli00/6D')
            thisweek = soup.find('div', class_ = 'thisweek')
        else:
            soup = self.do_action('pw01dli00/F3')
            # TODO
            exit()

        # HTML内から日付を取得
        soup = BeautifulSoup(str(thisweek), 'lxml')
        kaisai_dates = soup.find_all('h3')

        today_position = -1

        for i, kaisai_date in enumerate(kaisai_dates):
            '''TODO 平日に動作確認のためコメントアウト
            # レース日と稼働日が一致する枠の番号を取得
            m = re.search('(\d+)月(\d+)日', kaisai_date)
            if jst.month() == m.group(1) and jst.day() == m.group(2):
                today_position = i
                break
            '''
            today_position = i
            break

        # 合致した枠内のHTMLを取得
        links = BeautifulSoup(str(soup.find_all('div', class_='link_list multi div3 center')[today_position]), 'lxml')
        # パラメータを抽出しインスタンス変数に格納
        if page_type == 'odds':
            self.odds_param = self.extract_param(links)
            print(self.odds_param)
        else:
            self.info_param = self.extract_param(links)
            print(self.info_param)
        time.sleep(3)

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