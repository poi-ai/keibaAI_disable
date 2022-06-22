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
        self.get_race_info(True)
        logger.info(f'初期処理終了 開催場数：{len(self.baba_url)} 記録対象レース数：{len(self.race_info)}')

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

    def extract_info(self, param):
        '''doActionの第二引数からレース情報を抽出する

        Args:
            param(str) : doActionの第二引数(POSTパラメータ)

        Returns:
            baba_code(str) : JRA独自の競馬場コード
            race_num(str) : レース番号(xxRのxx)

        '''
        #return param[], param TODO
        pass

    def get_param(self, page_type):
        '''稼働日の各競馬場のレースリストページのパラメータを取得する

        Args:
            page_type(str):サイトの種類
                           odds:オッズ関連ページ,info:出馬表関連ページ

        '''
        # 今週の開催一覧ページのHTMLを取得
        if page_type == 'odds':
            soup = self.do_action('pw15oli00/6D')
        else:
            soup = self.do_action('pw01dli00/F3')

        # 開催情報のリンクがある場所を切り出し
        kaisai_frame = soup.find('div', id = 'main')

        # HTML内から日付を取得
        soup = BeautifulSoup(str(kaisai_frame), 'lxml')
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
        else:
            self.info_param = self.extract_param(links)
        time.sleep(3)

    def get_race_info(self, init_flg = False):
        '''レース情報を取得

        Args:
            init_flg(bool) : 初期処理(インスタンス作成)か主処理(インスタンス更新)か
                             T:初期処理,F:主処理

        '''
        race_time = []

        # 発走時刻の切り出し
        for param in self.info_param:
            soup = self.do_action(param)
            info_table = pd.read_html(str(soup))[0]
            time_table = [i.replace('時', '').replace('分', '') for i in info_table['発走時刻']]
            race_time.append(time_table)

        for kaisai_num, list_param in enumerate(self.odds_param):
            soup = self.do_action(list_param)

            # 単勝・複勝オッズページのパラメータを取得
            tanpuku = [self.extract_param(str(i))[0] for i in soup.find_all('div', class_='tanpuku')]

            ######## MEMO #######
            # find_allの第二引数を↓に書き換えれば、別の馬券のパラメータも取得できる
            # wakuren,umaren,wide,umatan,trio,tierce
            #####################

            # TODO
            for race_num, param in enumerate(tanpuku):
                self.race_info.append(RaceInfo(param, param[9:11], param[19:21], race_time[kaisai_num][race_num]))

                print(f'{param} {param[9:11]} {param[19:21]} {race_time[kaisai_num][race_num]}')

            time.sleep(2)
            exit()


class RaceInfo():
    '''各レースの情報を保持を行う
    Instance Parameter:
       race_param(str) : オッズページのPOSTパラメータ
       baba_code(str) : 競馬場コード
       race_no(str) : レース番号,xxRのxxの部分
       race_time(datetime) : 発走時刻
       record_flg(str) : 0,記録時刻待ち
                         1,暫定オッズ取得待ち
                         2,最終オッズ取得待ち
                         3,暫定オッズ出力待ち
                         4,最終オッズ出力待ち
                         -1,最終オッズ出力済
       jra_flg(str) : 1,中央 0,地方
    '''

    def __init__(self, race_param, baba_code, race_no, race_time):
        self.__race_param = race_param
        self.__baba_code = baba_code
        self.__race_no = race_no
        self.__race_time = race_time
        self.__record_flg = '0'
        self.__jra_flg = '1'

    @property
    def race_param(self):
        return self.race_param

    @property
    def baba_code(self):
        return self.__baba_code

    @property
    def race_no(self):
        return self.__race_no

    @property
    def race_time(self):
        return self.__race_time

    @property
    def record_flg(self):
        return self.__record_flg

    @property
    def jra_flg(self):
        return self.__jra_flg

    @race_time.setter
    def race_time(self, race_time):
        self.__race_time = race_time

    @record_flg.setter
    def record_flg(self, record_flg):
        self.__record_flg = record_flg

    @jra_flg.setter
    def jra_flg(self, jra_flg):
        self.__jra_flg = jra_flg


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