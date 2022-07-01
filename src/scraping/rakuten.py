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
        latest_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
        oldest_date(str) : 取得対象の最も古い日付
                          デフォルト : 20100601(閲覧可能な最古の日付)

        baba_url(list<str>) : 取得対象日の各競馬場のレース情報が記載されたURL

    '''

    def __init__(self, oldest_date = '20100601' latest_date = jst.yesterday()):
        self.validation_check()
        self.main(latest_date, oldest_date)

    def validation_check(latest_date, oldest_date):
        '''日付の妥当性チェックを行う'''
        logger.info('日付のバリデーションチェック開始')

        # 日付フォーマットチェック
        try:
            temp = datetime.strptime(latest_date, %Y%m%d)
        except:
            logger.warning('取得対象最新日の値が不正です')
            logger.warning(f'取得対象最新日:{datetime.strptime(jst.yesterday(), %Y/%m/%d)} として処理を行います')
            latest_date = jst.yesterday()

        try:
            temp = datetime.strptime(oldest_date, %Y%m%d)
        except:
            logger.warning('取得対象最古日の値が不正です')
            logger.warning(f'取得対象最古日:2010/06/01 として処理を行います')
            oldest_date = '20100601'

        # 日付妥当性チェック
        if latest_date == jst.date():
            logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
            logger.warning(f'取得対象最新日:{datetime.strptime(jst.yesterday(), %Y/%m/%d)} として処理を行います')
            latest_date = jst.yesterday()
        else latest_date < jst.date():
            logger.warning('取得対象最新日の値が未来になっています')
            logger.warning(f'取得対象最新日:{datetime.strptime(jst.yesterday(), %Y/%m/%d)} として処理を行います')
            latest_date = jst.yesterday()

        if oldest_date > jst.date():
            logger.warning('取得対象最古日の値が2010/06/01より前になっています')
            logger.warning('2010/6/1以前のオッズデータは楽天競馬サイト内に存在しないため取得できません')
            logger.warning(f'取得対象最古日:2010/06/01 として処理を行います')
            latest_date = jst.yesterday()

        if latest_date < oldest_date:
            logger.warning('取得対象最古日と最新日の記載順かま逆です')
            logger.warning(f'取得対象最新日:{datetime.strptime(oldest_date, %Y/%m/%d)}')
            logger.warning(f'取得対象最古日:{datetime.strptime(latest_date, %Y/%m/%d)} として処理を行います')
            tmp = latest_date
            latest_date = oldest_date
            oldest_date = tmp

        logger.info('日付のバリデーションチェック終了')

    def main(self, latest_date, oldest_date):
        '''主処理、各メソッドの呼び出し'''

        date = latest_date

        while self.date_check(date):

            # 競馬場URLの取得
            for baba_url in self.get_kaisai(date):
                # レースURLの取得
                race_url = self.get_race_url(baba_url)
                # オッズテーブルの取得
                odds_table = self.get_odds(race_url)
                # テーブルデータの加工/CSV出力
                self.record_odds(race_url, odds_table)

            date = jst.yesterday(date)

    def date_check(date):
        '''対象日付内かのチェックを行う'''
        if self.oldest_date <= date <= self.latest_date:
            return True
        return False

    def get_kaisai(self, target_date):
        '''指定した日に開催される競馬場のURLを取得する'''
        result = soup.get_soup(f'{RACE_CARD}{URL_LIST}{URL_ID}{target_date}{baba_code}{URL_RESERVE}{race_number}')
        race_track = result.find_all('ul', class_ = 'raceTrack')

        if len(race_track) == 0:
            return []

        return [link.get('href') for link in race_track[0].find_all('a')]:

    def get_race_url(self, baba_url):
        '''指定した競馬場(日付)に開催されるレースのURLを取得する'''
        result = soup.get_soup(baba_url)
        race_number = result.find_all('ul', class_ = 'raceNumber')

        for race_url in [link.get('href') for link in race_number[0].find_all('a')]:
            self.get_odds(race_url)

    def get_odds(self, race_url):
        '''レースURLから単勝・複勝オッズのテーブルデータを取得する'''

        return race_url, pd.read_html(f'{ODDS}{TANFUKU}{URL_ID}{race_url[-18:]}'))

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

        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力する
        writecsv.write_csv(write_df)

    def extract_info(self, url):
        '''レース関連URLの下18桁を分割して返す'''
        m = re.search(r'(\d{8})(\d{2})(\d{6})(\d{2})', url)
        # 順に開催年月日,競馬場コード,予備コード(未使用),レース番号
        return [m.group(i) for i in range(1, 5)]

    def extract_param(self, url):
        '''レース関連URLの下18桁を返す'''
        m = re.search(r'(\d{18}')
        return str(m.group(i))

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