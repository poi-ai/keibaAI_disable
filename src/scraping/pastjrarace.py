import itertools
import pandas as pd
import package
import re
import json
import sys
import time
import traceback
from common import babacodechange, logger, jst, output, soup as sp, line
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
        hold_date = self.get_hold_date()

        logger.info(f'取得対象日数は{len(date_list)}日です')
        print(f'取得対象日数は{len(date_list)}日です')

        # レースのある日を1日ずつ遡って取得処理を行う
        for hold_date in tqdm(hold_date_list):

            logger.info(f'{jst.change_format(hold, "%Y%m%d", "%Y/%m/%d")}のレースデータの取得を開始します')

            # TODO ここまで

            # 指定日に行われる全レースのレースID取得
            try:
                race_id_list = self.get_race_id(hold_date)
            except Exception as e:
                self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                exit()

            # TODO 動作確認用
            print(race_id_list)

            # レースIDからレース情報を取得する
            for race_id in race_id_list:

                # TODO レース情報取得処理メソッド呼び出し
                pass

            time.sleep(3)

    def get_hold_date(self):
        '''取得対象範囲内でのレース開催日を取得

        Returns:
            date_list(list[str]): レース開催日をyyyyMMdd型で持つリスト

        '''

        # 取得対象の最古/最新日付の年と月を抽出
        target_year = self.latest_date[:4]
        target_month = self.latest_date[4:6]
        latest_year = self.latest_date[:4]
        latest_month = self.latest_date[4:6]
        oldest_year = self.oldest_date[:4]
        oldest_month = self.oldest_date[4:6]

        # 開催日を格納するリスト
        date_list = []

        for _ in tqdm(range((int(target_year) - int(oldest_year)) * 12  + int(target_month) - int(oldest_month) + 1)):
            # 開催月を取得
            hold_list = self.get_month_hold_date(target_year, target_month)

            # 開始日と同月の場合、開催日以前の日の切り落とし
            if target_year == latest_year and target_month == latest_month:
                hold_list.append(self.latest_date)
                hold_list.sort()
                hold_list = hold_list[hold_list.index(self.latest_date) + 1:]

            # 終了日と同月の場合、開催日以降の日の切り落とし
            if target_year == oldest_year and target_month == oldest_month:
                hold_list.append(self.oldest_date)
                hold_list.sort()
                if hold_list.count(self.oldest_date) == 2:
                    hold_list = hold_list[:hold_list.index(self.oldest_date) + 1]
                else:
                    hold_list = hold_list[:hold_list.index(self.oldest_date)]

            # 開催日を格納
            date_list.append(hold_list)

            # 前月へ
            if target_month == '1':
                target_year = str(int(target_year) - 1)
                target_month = '12'
            else:
                target_month = str(int(target_month) - 1)

        # TODO 要確認
        print(date_list)

        # 一元化して返す
        return list(itertools.chain.from_iterable(date_list))

    def get_month_hold_date(self, years, month):
        '''指定した年月の中央競馬の開催日を取得

        Args:
            years(str):取得する対象の年。yyyy
            month(str):取得する対象の月。MM

        Return:
            hold_list(list):対象年月の開催日。要素はyyyyMMdd形式のstr型。

        '''
        # 開催カレンダーのURL
        url = f'https://race.netkeiba.com/top/calendar.html?year={years}&month={month}'

        # ページ内の全リンクを取得
        soup = sp.get_soup(url)
        links = soup.find_all('a')
        hold_list = []
        for link in links:
            date_url = link.get('href')
            # カレンダー内にあるリンクだけ取得
            if 'kaisai_date' in date_url:
                hold_list.append(date_url[len(date_url) - 8:])
        return hold_list

    def get_race_id(hold_date):
        '''対象年月日のレース番号を取得

        Args:
            hold_date(list):中央競馬開催日の年月日(yyyyMMdd)

        Returns:
            race_id_list(list):対象年月日のレースIDを要素に持つリスト

        '''
        # 各開催日からレースIDをリストに代入
        race_id_list = []

        # ページ内の全URL取得
        cource_url = f'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date={hold_date}'

        soup = soup.get_soup(cource_url)
        links = soup.find_all('a')

        for link in links:
            race_url = link.get('href')
            # レース結果ページのみ取得しその中からレースIDを切り出す
            if 'result' in race_url:
                race_id_list.append(race_url[28:40])

        return race_id_list

    # TODO ここらへんにレース情報取得メソッド

    def record_odds(self, date, race_id, odds):
        '''オッズデータにレース情報を付加して出力する
            TODO 使えるなら流用、使えないなら削除
        '''

        # レース情報を頭数分用意する
        info = [[date, race_id[4:6], race_id[10:]] for _ in range(len(odds))]

        write_df = pd.concat([pd.DataFrame(info, index = odds.index), pd.DataFrame(odds.index, index = odds.index), odds], axis=1)

        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力
        if self.output_type == 'a':
            # 一つのファイルに出力
            output.csv(write_df, 'jra_resultodds')
        elif self.output_type == 'y':
            # 年ごとにファイルを分割
            output.csv(write_df, f'jra_resultodds_{date[:4]}')
        else:
            # 月ごとにファイルを分割
            output.csv(write_df, f'jra_resultodds_{date[:6]}')

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
    # 開催カレンダーページ
    CALENDAR_URL = 'https://race.netkeiba.com/top/calendar.html'
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
