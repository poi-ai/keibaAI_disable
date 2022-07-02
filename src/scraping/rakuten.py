import csv
import lxml
import pandas as pd
import package
import re
import requests
import sys
import traceback
from bs4 import BeautifulSoup
from common import logger, jst, soup, writecsv
from datetime import datetime, timedelta

class ResultOdds():
    '''楽天競馬のサイトから地方競馬の確定オッズを取得する

    Instance Parameter:
        latest_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
        oldest_date(str) : 取得対象の最も古い日付(yyyyMMdd)
                          デフォルト : 20100601(閲覧可能な最古の日付)
        date(str) : 取得対象の日付(yyyyMMdd)
    '''

    def __init__(self, oldest_date = '20100601', latest_date = jst.yesterday()):
        logger.info('----------------------------')
        logger.info('地方競馬過去レースオッズシステム起動')
        self.__latest_date = latest_date
        self.__oldest_date = oldest_date
        self.validation_check()
        self.__date = self.latest_date
        self.__url = URL()
        self.main()
        logger.info('地方競馬過去レースオッズシステム終了')

    @property
    def latest_date(self): return self.__latest_date
    @property
    def oldest_date(self): return self.__oldest_date
    @property
    def date(self): return self.__date
    @property
    def url(self): return self.__url
    @latest_date.setter
    def latest_date(self, latest_date): self.__latest_date = latest_date
    @oldest_date.setter
    def oldest_date(self, oldest_date): self.__oldest_date = oldest_date
    @date.setter
    def date(self, date): self.__date = date

    def validation_check(self):
        '''日付の妥当性チェックを行う'''
        logger.info('日付のバリデーションチェック開始')

        # 日付フォーマットチェック
        try:
            tmp = datetime.strptime(self.oldest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最古日の値が不正です')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2010/06/01 に変更します')
            self.oldest_date = '20100601'

        try:
            tmp = datetime.strptime(self.latest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最新日の値が不正です')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()

        # 日付妥当性チェック
        if self.oldest_date < '20100601':
            logger.warning('取得対象最古日の値が2010/06/01より前になっています')
            logger.warning('2010/06/01以前のオッズデータは楽天競馬サイト内に存在しないため取得できません')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2010/06/01に変更します')
            self.oldest_date = jst.yesterday()
        elif self.oldest_date == jst.date():
            logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
            logger.warning(f'取得対象最古日:{self.oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.oldest_date = jst.yesterday()
        elif self.oldest_date > jst.date():
            logger.warning('取得対象最古日の値が未来になっています')
            logger.warning(f'取得対象最古日:{self.oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.oldest_date = jst.yesterday()

        if self.latest_date == jst.date():
            logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()
        elif self.latest_date > jst.date():
            logger.warning('取得対象最新日の値が未来になっています')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()

        if self.latest_date < self.oldest_date:
            logger.warning('取得対象最古日と最新日の記載順が逆のため入れ替えて処理を行います')
            tmp = self.latest_date
            self.latest_date = self.oldest_date
            self.oldest_date = tmp

        logger.info('日付のバリデーションチェック終了')
        logger.info(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        logger.info(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')

    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 1日ずつ遡って取得処理を行う
        while True:
            # 日付チェック
            if not self.date_check():
                break

            # 競馬場URLの取得
            for baba_url in self.get_kaisai():
                # レースURLの取得
                race_url = self.get_race_url(baba_url)
                # オッズテーブルの取得
                odds_table = self.get_odds(race_url)
                # テーブルデータの加工/CSV出力
                self.record_odds(race_url, odds_table)

            # 1日前へ
            self.date = jst.yesterday(self.date)

    def date_check(self):
        '''対象日付内かのチェックを行う'''
        if self.oldest_date <= self.date <= self.latest_date:
            return True
        return False

    def get_kaisai(self):
        '''指定した日に開催される競馬場のURLを取得する'''
        result = soup.get_soup(f'{self.url.RACE_CARD}{self.date}0000000000')
        race_track = result.find_all('ul', class_ = 'raceTrack')

        if len(race_track) == 0:
            return []

        # 競馬場一覧からボタンになっている(=開催のある)もののみ切り出し
        return [link.get('href') for link in race_track[0].find_all('a')]

    def get_race_url(self, baba_url):
        '''指定した競馬場(日付)に開催されるレースのURLを取得する'''
        result = soup.get_soup(baba_url)
        race_number = result.find_all('ul', class_ = 'raceNumber')

        for race_url in [link.get('href') for link in race_number[0].find_all('a')]:
            self.get_odds(race_url)

    def get_odds(self, race_url):
        '''レースURLから単勝・複勝オッズのテーブルデータを取得する'''
        print(race_url)
        return pd.read_html(f'{self.url.TANFUKU}{race_url[-18:]}')

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

    def extract_info(self, race_url):
        '''レース関連URLの下18桁を分割して返す'''
        m = re.search(r'(\d{8})(\d{2})(\d{6})(\d{2})', race_url)
        # 順に開催年月日,競馬場コード,予備コード(未使用),レース番号
        return [m.group(i) for i in range(1, 5)]

    def extract_param(self, race_url):
        '''レース関連URLの下18桁を返す'''
        m = re.search(r'(\d{18}', race_url)
        return str(m.group(1))

class URL():
    '''楽天競馬の各ページのURL'''
    # トップページ
    TOP = 'https://keiba.rakuten.co.jp/'
    # 投票ページ(要ログイン)
    BET = 'https://bet.keiba.rakuten.co.jp/bet/normal'
    # レース一覧/出走表
    RACE_CARD = 'https://keiba.rakuten.co.jp/race_card/list/RACEID/'
    # オッズ(単勝/複勝)
    TANFUKU = 'https://keiba.rakuten.co.jp/odds/tanfuku/RACEID/'
    # オッズ(枠複)
    WAKUFUKU = 'https://keiba.rakuten.co.jp/odds/wakufuku/RACEID/'
    # オッズ(枠単)
    WAKUTAN = 'https://keiba.rakuten.co.jp/odds/wakutan/RACEID/'
    # オッズ(馬複)
    UMAFUKU = 'https://keiba.rakuten.co.jp/odds/umafuku/RACEID/'
    # オッズ(馬単)
    UMATAN = 'https://keiba.rakuten.co.jp/odds/umatan/RACEID/'
    # オッズ(ワイド)
    WIDE = 'https://keiba.rakuten.co.jp/odds/wide/RACEID/'
    # オッズ(三連複)
    SANRENFUKU = 'https://keiba.rakuten.co.jp/odds/sanrenfuku/RACEID/'
    # オッズ(三連単)
    SANRENTAN = 'https://keiba.rakuten.co.jp/odds/sanrentan/RACEID/'
    # レース結果
    RESULT = 'https://keiba.rakuten.co.jp/race_performance/list/RACEID/'

if __name__ == '__main__':
    # ログ用インスタンス作成
    logger = logger.Logger()

    # オッズ取得用クラス呼び出し
    try:
        ro = ResultOdds(sys.argv[1], sys.argv[2])
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())