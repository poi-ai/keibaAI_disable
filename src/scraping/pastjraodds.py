import pandas as pd
import package
import re
import json
import sys
import time
import traceback
from common import babacodechange, logger, jst, output, soup, line, validate
from datetime import datetime
from tqdm import tqdm

class ResultOdds():
    '''netkeibaのサイトから中央競馬の確定オッズを取得する
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
        logger.info('中央競馬過去オッズ取得システム起動')
        line.send('中央競馬過去オッズ取得システム起動')
        logger.info('初期処理開始')
        self.__oldest_date, self.__latest_date = validate.check('20070728', oldest_date, latest_date)
        logger.info('日付のバリデーションチェック終了')
        self.__url = URL()
        self.__output_type = output_type

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

    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 対象の日付リストの取得
        dates = self.get_dates()

        logger.info(f'取得対象日数は{len(dates)}日です')
        print(f'取得対象日数は{len(dates)}日です')

        # レースのある日を1日ずつ遡って取得処理を行う
        for date in tqdm(dates):

            logger.info(f'{jst.change_format(date, "%Y%m%d", "%Y/%m/%d")}のオッズデータの取得を開始します')

            try:
                # 指定日に行われる全レースのレースIDの取得
                race_ids = self.get_race_url(date)
            except Exception as e:
                self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                exit()

            for race_id in race_ids:

                try:
                    # オッズテーブルの取得
                    odds_table = self.get_odds(race_id)

                    # DataFrame型(=正常レスポンス)でない場合は何もしない
                    if type(odds_table) == bool:
                        continue

                except Exception as e:
                    self.error_output('オッズテーブル取得処理でエラー', e, traceback.format_exc())
                    exit()

                try:
                    # テーブルデータの加工/CSV出力
                    self.record_odds(date, race_id, odds_table)
                except Exception as e:
                    self.error_output('テーブルデータの処理でエラー', e, traceback.format_exc())
                    exit()

                time.sleep(3)

    def get_dates(self):
        '''取得対象日の取得を行う'''

        # 対象日格納用
        target_dates = []

        # 対象最新日の月から順に検索していく
        month = self.latest_date[:6]

        # 対象最古日より前の月になるまでループ
        while month >= self.oldest_date[:6]:
            logger.info(f'{jst.change_format(month, "%Y%m", "%Y/%m")}のレース開催日を取得します')
            print(f'{jst.change_format(month, "%Y%m", "%Y/%m")}のレース開催日を取得します')

            # HTMLタグ取得
            html = soup.get_soup(f'{self.url.RESULTS}{month}01')

            # 開催カレンダーの取得
            calendar = html.find('table')

            # 開催日のリンクがある日付を抽出
            dates = re.finditer(r'/race/list/(\d+)/', str(calendar))

            # 降順にするためリストに変換
            date_list = [m.groups()[0] for m in dates]
            date_list.reverse()

            # 期間内だったらリストに追加
            for date in date_list:
                if self.oldest_date <= date <= self.latest_date:
                    target_dates.append(date)

            # 月をひとつ前に戻す
            if month[4:] == '01':
                month = str(int(month) - 89)
            else:
                month = str(int(month) - 1)

        return target_dates

    def get_race_url(self, date):
        '''指定した日に開催される競馬場のURLを取得する'''
        # HTMLタグ取得
        html = soup.get_soup(f'{self.url.RESULTS}{date}')

        # レース一覧記載枠の箇所を抽出
        race_frame = html.find('div', class_ = 'race_kaisai_info')

        # レースへのリンクをすべて取得
        races = re.finditer(r'/race/(\d+)/', str(race_frame))

        # リストに変換して返す
        return [m.groups()[0] for m in races]

    def get_odds(self, race_id):
        '''APIから単勝・複勝オッズのデータ(JSON)を取得する'''

        logger.info(f'{babacodechange.netkeiba(race_id[4:6])}{race_id[10:]}Rのオッズデータを取得します')

        # APIからJSON取得
        html = soup.get_soup(f'{self.url.TANPUKU}{race_id}')
        json_data = json.loads(html.text)

        # レスポンスが正しく返ってきたかのチェック
        if json_data['reason'] == '':
            try:
                # JSONから必要なカラムを切り出し
                df = pd.concat([pd.DataFrame(json_data['data']['odds']['1']).T, pd.DataFrame(json_data['data']['odds']['2']).T], axis = 1)
            except:
                # netkeiba側のJSONがおかしい場合があるのでそれのリカバリ処理
                logger.warning('オッズ取得処理にて正常でないJSONのレスポンスを取得')
                return False
            df = df.iloc[:,[0, 3, 4]]
            df.columns = ['単勝', '複勝下限', '複勝上限']

            return df
        elif json_data['reason'] == 'result odds empty':
            logger.warning('オッズ取得処理にて空のレスポンスを取得')
            return False
        else:
            logger.warning('オッズ取得処理にて空レスポンス以外のエラー')
            return False

    def record_odds(self, date, race_id, odds):
        '''オッズデータにレース情報を付加して出力する'''

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
    # 単複オッズAPI
    TANPUKU = 'https://race.netkeiba.com/api/api_get_jra_odds.html?type=1&race_id='

if __name__ == '__main__':
    # ログ用インスタンス作成
    # プログレスバーを出すためコンソールには出力しない
    logger = logger.Logger(0)

    # 初期処理
    try:
        if len(sys.argv) >= 3:
            ro = ResultOdds(sys.argv[1], sys.argv[2])
        elif len(sys.argv) == 2:
            ro = ResultOdds(sys.argv[1])
        else:
            ro = ResultOdds()
    except Exception as e:
        logger.error('初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        line.send('初期処理でエラー')
        line.send(e)
        line.send(traceback.format_exc())
        raise

    # 主処理
    ro.main()

    logger.info('中央競馬過去オッズ取得システム終了')
    line.send('中央競馬過去オッズ取得システム終了')