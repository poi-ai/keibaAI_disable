import pandas as pd
import package
import re
import sys
import time
import traceback
from common import logger, jst, output, soup, babacodechange, line
from datetime import datetime
from tqdm import tqdm

class ResultOdds():
    '''楽天競馬のサイトから地方競馬の確定オッズを取得する

    Instance Parameter:
        latest_date(str) : 取得対象の最も新しい日付(yyyyMMdd)
                          デフォルト : システム稼働日前日
        oldest_date(str) : 取得対象の最も古い日付(yyyyMMdd)
                          デフォルト : 20100601(閲覧可能な最古の日付)
        date(str) : 取得対象の日付(yyyyMMdd)
        url(URL) : 楽天競馬サイト内のURL一覧
        output_type(str) : 出力ファイルを分割
                           m : 月ごと(デフォルト)、y : 年ごと、a : 全ファイルまとめて
    '''

    def __init__(self, oldest_date = '20100601', latest_date = jst.yesterday(), output_type = 'm'):
        logger.info('----------------------------')
        logger.info('地方競馬過去オッズ取得システム起動')
        line.send('地方競馬過去オッズ取得システム起動')
        logger.info('初期処理開始')
        self.__latest_date = latest_date
        self.__oldest_date = oldest_date
        self.validation_check()
        self.__date = self.latest_date
        self.__url = URL()
        self.__output_type = output_type
        logger.info(f'取得対象最古日:{jst.change_format(self.oldest_date, "%Y%m%d", "%Y/%m/%d")}')
        logger.info(f'取得対象最新日:{jst.change_format(self.latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')

    @property
    def latest_date(self): return self.__latest_date
    @property
    def oldest_date(self): return self.__oldest_date
    @property
    def date(self): return self.__date
    @property
    def url(self): return self.__url
    @property
    def output_type(self): return self.__output_type
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

    def main(self):
        '''主処理、各メソッドの呼び出し'''

        # 対象の日数計算
        days = self.days_calc()

        # 1日ずつ遡って取得処理を行う
        for _ in tqdm(range(days)):

            logger.info(f'{jst.change_format(self.date, "%Y%m%d", "%Y/%m/%d")}のオッズデータの取得を開始します')

            try:
                # 対象日に開催された競馬場URLの取得
                baba_urls = self.get_kaisai()
            except Exception as e:
                self.error_output('競馬場取得処理でエラー', e, traceback.format_exc())
                exit()

            for baba_url in baba_urls:
                logger.info(f'{babacodechange.rakuten(self.extract_info(baba_url)[1])}競馬場のオッズデータを取得します')
                try:
                    # 指定競馬場内での各レースURLの取得
                    race_urls = self.get_race_url(baba_url)
                    # レースURLが存在しなければスキップ
                    if race_urls == None: continue
                except Exception as e:
                    self.error_output('レースURL取得処理でエラー', e, traceback.format_exc())
                    exit()

                for race_url in race_urls:

                    logger.info(f'{self.extract_info(race_url)[3]}Rのオッズデータを取得します')
                    try:
                        # オッズテーブルの取得
                        odds_table = self.get_odds(race_url)
                    except Exception as e:
                        self.error_output('オッズテーブル取得処理でエラー', e, traceback.format_exc())
                        exit()

                    try:
                        # テーブルデータの加工/CSV出力
                        self.record_odds(race_url, odds_table)
                    except Exception as e:
                        self.error_output('テーブルデータの処理でエラー', e, traceback.format_exc())
                        exit()

                    time.sleep(3)

            # 1日前へ
            self.date = jst.yesterday(self.date)

    def days_calc(self):
        '''取得対象の日数を計算する'''
        target_date = self.latest_date
        counter = 0

        while True:
            if target_date < self.oldest_date:
                break
            counter += 1
            target_date = jst.yesterday(target_date)

        return counter

    def get_kaisai(self):
        '''指定した日に開催される競馬場のURLを取得する'''
        result = soup.get_soup(f'{self.url.RACE_CARD}{self.date}0000000000')
        if result == -1:
            logger.error(f'競馬場一覧情報の取得に失敗しました')
            raise

        race_track = result.find_all('ul', class_ = 'raceTrack')

        if len(race_track) == 0:
            return []

        # 競馬場一覧からボタンになっている(=開催のある)もののみ切り出し
        return [link.get('href') for link in race_track[0].find_all('a')]

    def get_race_url(self, baba_url):
        '''指定した競馬場(日付)に開催されるレースのURLを取得する'''
        result = soup.get_soup(baba_url)
        if result == -1:
            logger.error('レースURLの取得に失敗しました')
            raise

        race_number = result.find_all('ul', class_ = 'raceNumber')

        if race_number != []:
            return [link.get('href') for link in race_number[0].find_all('a')]
        else:
            logger.info('競馬場へのURLリンクはありますがレースが存在しません')
            return None

    def get_odds(self, race_url):
        '''レースURLから単勝・複勝オッズのテーブルデータを取得する'''
        table = pd.read_html(f'{self.url.TANFUKU}{race_url[-18:]}')
        if table == -1:
            logger.error(f'オッズテーブルの取得に失敗しました')
            raise
        return table

    def record_odds(self, race_url, odds_table):
        '''レース/オッズ情報を加工する'''

        # レースURLからレース情報を抽出する
        race_info = self.extract_info(race_url)

        # 複勝が存在する場合
        if '複勝オッズ' in odds_table[0].columns:
            # オッズテーブルから必要なカラムだけ抜き出す
            odds = odds_table[0][['馬番', '単勝オッズ', '複勝オッズ']]
            # 複勝オッズを下限と上限に分割
            fukusho = odds['複勝オッズ'].str.split(' - ', expand = True)
            # 元のカラムは削除
            odds = odds.drop('複勝オッズ', axis=1)
        # 複勝オッズが存在しない場合
        elif '単勝オッズ' in odds_table[0].columns:
            # オッズテーブルから必要なカラムだけ抜き出す
            odds = odds_table[0][['馬番', '単勝オッズ']]
            # 複勝オッズの箇所にNULLを挿入
            fukusho = pd.DataFrame([['', ''] for _ in range(len(odds))], index = odds.index)
        # 馬券販売前にレースが中止となった場合
        else:
            logger.info(f'{race_info[0]}の{babacodechange.rakuten(race_info[1])}{race_info[3]}Rのレースは中止になりました')
            return

        # 馬券販売後(直前で)レースが中止となった場合
        if odds['単勝オッズ'][0] == 0.0 and odds['単勝オッズ'][1] == 0.0:
            logger.info(f'{race_info[0]}の{babacodechange.rakuten(race_info[1])}{race_info[3]}Rのレースは中止になりました')
            return

        # レース情報を頭数分用意する
        info = [[race_info[0], race_info[1], race_info[3]] for _ in range(len(odds))]

        write_df = pd.concat([pd.DataFrame(info, index = odds.index), odds, fukusho], axis=1)

        write_df.columns = ['発走日', '競馬場コード', 'レース番号', '馬番', '単勝オッズ', '複勝オッズ下限', '複勝オッズ上限']

        # CSVに出力
        if self.output_type == 'a':
            # 一つのファイルに出力
            output.csv(write_df, f'nar_resultodds')
        elif self.output_type == 'y':
            # 年ごとにファイルを分割
            output.csv(write_df, f'nar_resultodds_{race_info[0][:4]}')
        else:
            # 月ごとにファイルを分割
            output.csv(write_df, f'nar_resultodds_{race_info[0][:6]}')

    def extract_info(self, race_url):
        '''レース関連URLの下18桁を分割して返す'''
        m = re.search(r'(\d{8})(\d{2})(\d{6})(\d{2})', race_url)
        # 順に開催年月日,競馬場コード,予備コード(未使用),レース番号
        return [m.group(i) for i in range(1, 5)]

    def extract_param(self, race_url):
        '''レース関連URLの下18桁を返す'''
        m = re.search(r'(\d{18}', race_url)
        return str(m.group(1))

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

    logger.info('地方競馬過去オッズ取得システム終了')
    line.send('地方競馬過去オッズ取得システム終了')