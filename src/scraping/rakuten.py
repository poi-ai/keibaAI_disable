import csv
import lxml
import pandas as pd
import package
import re
import requests
import traceback
from bs4 import BeautifulSoup
from common import logger, jst, soup, writecsv
from datetime import datetime, timedelta

class ResultOdds():
    '''楽天競馬のサイトから地方競馬の確定オッズを取得する

    Instance Parameter:
        start_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
          end_date(str) : 取得対象の最も古い日付
                          デフォルト : 20100601(閲覧可能な最古の日付)

        baba_url(list<str>) : 取得対象日の各競馬場のレース情報が記載されたURL

    '''

    def __init__(self, start_date = jst.yesterday(), end_date = '20100601'):
        self.main(start_date, end_date)

    def main(self, start_date, end_date):
        # TODO バリデーションチェック

        date = start_date

        if date < end_date or start_date < date:
             return

        self.get_kaisai(date)

    def get_kaisai(self, target_date):
        '''指定した日に開催される競馬場のURLを取得する'''
        result = soup.get_soup(f'{RACE_CARD}{URL_LIST}{URL_ID}{target_date}{baba_code}{URL_RESERVE}{race_number}')
        race_track = result.find_all('ul', class_ = 'raceTrack')

        if len(race_track) == 0:
            return []

        # TODO 発走時刻もいつか抜く
        # ul raceNumber内の span numがレース番号,span timeが発走時刻、レースないならtime=&nbsp
        # あるいは read_tableの'発走時刻'(こっちの方が楽)

        for baba_url in [link.get('href') for link in race_track[0].find_all('a')]:
            self.get_race_url(baba_url)

        return

    def get_race_url(self, baba_url):
        '''指定した競馬場(日付)に開催されるレースのURLを取得する'''
        result = soup.get_soup(baba_url)
        race_number = result.find_all('ul', class_ = 'raceNumber')

        for race_url in [link.get('href') for link in race_number[0].find_all('a')]:
            self.get_odds(race_url)

    def get_odds(self, race_url):
        '''レースURLから単勝・複勝オッズのデータを取得する'''

        self.record_odds(race_url, pd.read_html(f'{ODDS}{TANFUKU}{URL_ID}{race_url[-18:]}'))

    def record_odds(self, race_url, odds_table):
        '''レース/オッズ情報を加工する'''
        # オッズテーブルから必要なカラムだけ抜き出す
        odds = odds_table[0][['馬番', '単勝オッズ', '複勝オッズ']]
        # 複勝オッズを下限と上限に分割
        fukusho = odds['複勝オッズ'].str.split(' - ', expand = True)
        # 元のカラムは削除
        odds = odds.drop('複勝オッズ', axis=1)
        # レースURLからレース情報を抽出する
        race_info = self.extract_info(race_url)

        # レース情報を頭数分用意する
        info = [[race_info[0], race_info[1], race_info[3]] for _ in range(len(odds))]

        write_df = pd.concat([pd.DataFrame(info, index = odds.index), odds, fukusho], axis=1)

        print(write_df)
        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力する df
        writecsv.write_csv(write_df)

    def extract_info(self, url):
        '''レース関連URLの下18桁を分割して返す'''
        m = re.search(r'(\d{8})(\d{2})(\d{6})(\d{2})', url)
        return [m.group(i) for i in range(1, 5)]

if __name__ == '__main__':
    logger = logger.Logger()

    # TODO 後でクラス化
    RACE_CARD = 'https://keiba.rakuten.co.jp/race_card/'
    ODDS = 'https://keiba.rakuten.co.jp/odds/'
    URL_LIST = 'list/'
    TANFUKU = 'tanfuku/'
    URL_ID = 'RACEID/'
    URL_RESERVE = '000000'
    baba_code = '00'
    race_number= '00'

    try:
        ro = ResultOdds()
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())