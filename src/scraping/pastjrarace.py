import pandas as pd
import package
import re
import json
import sys
import time
import traceback
from common import babacodechange, logger, jst, output, soup, line
from datetime import datetime, timedelta
from tqdm import tqdm

class RaceData():
    '''netkeibaのサイトから中央競馬の過去レースデータを取得する
    Instance Parameter:
        latest_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
        oldest_date(str) : 取得対象の最も古い日付(yyyyMMdd)
                          デフォルト : 20070728(閲覧可能な最古の日付)
        date(list<str>) : 取得対象の日付(yyyyMMdd)
        url(URL) : netkeibaサイト内のURL一覧
        output_type(str) : 出力ファイルを分割
                           m : 月ごと(デフォルト)、y : 年ごと、a : 全ファイルまとめて
    '''

    def __init__(self, oldest_date = '20070728', latest_date = jst.yesterday(), output_type = 'm'):
        logger.info('----------------------------')
        logger.info('中央競馬過去レースデータ取得システム起動')
        logger.info('初期処理開始')
        self.__latest_date = latest_date
        self.__oldest_date = oldest_date
        self.validation_check()
        self.__url = URL()
        self.__output_type = output_type
        logger.info(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        logger.info(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')
        print(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        print(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')

    @property
    def latest_date(self): return self.__latest_date
    @property
    def oldest_date(self): return self.__oldest_date
    @property
    def url(self): return self.__url
    @property
    def output_type(self): return self.__output_type
    @latest_date.setter
    def latest_date(self, latest_date): self.__latest_date = latest_date
    @oldest_date.setter
    def oldest_date(self, oldest_date): self.__oldest_date = oldest_date

    def validation_check(self):
        '''日付の妥当性チェックを行う'''
        logger.info('日付のバリデーションチェック開始')

        # 日付フォーマットチェック
        try:
            tmp = datetime.strptime(self.oldest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最古日の値が不正です')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2007/07/28 に変更します')
            self.oldest_date = '20070728'

        try:
            tmp = datetime.strptime(self.latest_date, '%Y%m%d')
        except:
            logger.warning('取得対象最新日の値が不正です')
            logger.warning(f'取得対象最新日:{self.latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
            self.latest_date = jst.yesterday()

        # 日付妥当性チェック
        if self.oldest_date < '20070728':
            logger.warning('取得対象最古日の値が2007/07/28より前になっています')
            logger.warning('2007/07/28以前のレースデータはnetkeibaサイト内に存在しないため取得できません')
            logger.warning(f'取得対象最古日:{self.oldest_date}→2007/07/28に変更します')
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

    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 対象の日付リストの取得
        dates = self.get_dates()

        logger.info(f'指定間日数は{len(dates)}日です')
        print(f'指定間日数は{len(dates)}日です')

        # レースのある日を1日ずつ遡って取得処理を行う
        for date in tqdm(dates):

            logger.info(f'{jst.change_format(date, "%Y%m%d", "%Y/%m/%d")}のレースデータの取得を開始します')

            try:
                # 指定日に行われる全レースのレースIDの取得
                race_ids = self.get_race_url(date)
            except Exception as e:
                self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                exit()

            for race_id in race_ids:

                # TODO レース情報取得処理メソッド呼び出し

                time.sleep(3)

    def get_dates(self):
        '''取得対象日の取得を行う(レース未開催日も含む)'''

        # 対象日格納用
        target_dates = []
        
        date = datetime.strptime(self.latest_date, '%Y%m%d')
        oldest = datetime.strptime(self.oldest_date, '%Y%m%d')

        while True:
            if date < self.oldest_date:
                return target_dates
            target_append(date)
            date = datetime.strptime(self.latest_date, '%Y%m%d') - timedelta(days = 1)

        return target_dates

    def get_race_url(self, date):
        '''指定した日に開催される競馬場のURLを取得する'''
        # HTMLタグ取得
        html = soup.get_soup(f'{self.url.RESULT_LIST_URL}/?kaisai_date={date}')
        
        # TODO ここまで

        # レース一覧記載枠の箇所を抽出
        race_frame = html.find('div', class_ = 'race_kaisai_info')

        # レースへのリンクをすべて取得
        races = re.finditer(r'/race/(\d+)/', str(race_frame))

        # リストに変換して返す
        return [m.groups()[0] for m in races]
    
    # TODO ここらへんにレース情報取得メソッド


    def error_output(self, message, e, stacktrace):
        '''エラー時のログ出力/LINE通知を行う
        Args:
            message(str) : エラーメッセージ
            e(str) : エラー名
            stacktrace(str) : スタックトレース
        '''
        logger.error(message)
        logger.error(e)
        logger.error(stacktrace)
        line.send(message)
        line.send(e)
        line.send(stacktrace)

class URL():
    '''netkeibaの各ページのURL'''
    # レースリンク一覧
    RESULTS = 'https://db.netkeiba.com/race/list/'
    # レース情報
    RACE = 'https://db.netkeiba.com/race/'
    # 日別レース一覧ページ
    RACE_LIST_URL = 'https://race.netkeiba.com/top/race_list_sub.html'


if __name__ == '__main__':
    # ログ用インスタンス作成
    # プログレスバーを出すためコンソールには出力しない
    logger = logger.Logger(0)

    # 初期処理
    try:
        if len(sys.argv) >= 3:
            rd = RaceData(sys.argv[1], sys.argv[2])
        elif len(sys.argv) == 2:
            rd = RaceData(sys.argv[1])
        else:
            rd = RaceData()
    except Exception as e:
        logger.error('初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        line.send('初期処理でエラー')
        line.send(e)
        line.send(traceback.format_exc())
        raise

    # 主処理
    rd.main()

    logger.info('中央競馬過去レースデータ取得システム終了')
    line.send('中央競馬過去レースデータ取得システム終了')