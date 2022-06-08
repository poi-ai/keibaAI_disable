import pandas as pd
import package
import time
import datetime
from common import babacodechange, jst, logger, writecsv

class Nar():
    '''地方競馬オッズ取得クラス

    Class Parameter:
       RACE_DATE(str):keiba.goのGETリクエストの日付パラメータ

    Instance Parameter:
       baba_url(list<str>) : 各競馬場のレース情報が記載されたURLのリスト
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_get_time(datetime) : 次回オッズ取得時刻
       write_data(DataFrame) : 書き込み用データ
    '''
    # 日付のGETパラメータ
    RACE_DATE = f'{jst.year()}%2f{jst.month().zfill(2)}%2f{jst.day().zfill(2)}'

    def __init__(self):
        logger.info('初期処理開始')
        self.__baba_url = []
        self.__race_info = []
        self.__next_get_time = 0
        self.__write_data = pd.DataFrame(columns = ['馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ', '記録時刻'])
        self.get_url()
        self.get_race_info(True)

    @property
    def baba_url(self):
        return self.__baba_url

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

    def get_url(self):
        '''稼働日の各競馬場のレースリストURLを取得する'''

        # keiba.go.jpから稼働日に開催のある競馬場名を取得する
        baba_names = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')[0][0].values.tolist()
        logger.info('開催テーブル取得')
        # 競馬場名をkeiba.goのパラメータで使われている競馬場番号へ変換する
        baba_codes = [babacodechange.keibago(place_name) for place_name in baba_names]

        # 各競馬場ごとにレース数と発走時刻を取得する
        for baba_code in baba_codes:
            # レースリスト一覧が載っているページのURLを保存
            self.baba_url.append(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate={Nar.RACE_DATE}&k_babaCode={baba_code}')

        time.sleep(3)

    def get_race_info(self, init_flg = False):
        '''レース情報を取得'''
        for race_url in self.baba_url:
            # レース情報をDataFrame型で取得
            race_list = pd.read_html(race_url)[0]
            logger.info(f'{babacodechange.keibago(race_url[-2:].replace("=", ""))}競馬場のレーステーブル取得')

            # 1レースごとの情報取得
            for idx in race_list.index:
                # 1レース切り出し
                race = race_list.loc[idx]
                # 時間をdatetime型に変換
                race_time = datetime.datetime(int(jst.year()), int(jst.month()), int(jst.day()), int(race[1][:2]), int(race[1][3:]), 0)

                # 最初の処理だけ作成、それ以降は発走時刻のみ更新
                if init_flg:
                    # クラス化して保存(競馬場コード,レース番号,発走時刻)
                    self.__race_info.append(RaceInfo(race_url[-2:].replace('=', ''), race[0].replace('R', ''), race_time))
                else:
                    # 保存済のレース情報の発走時刻と比較
                    for race_info in self.race_info:
                        if race_info.baba_code == race_url[-2:].replace('=', '') and race_info.race_no == race[0].replace('R', ''):
                            # 発走時刻が変更となっていたら設定し直し
                            if race_info.race_time != race_time:
                                logger.info(f'レース時間変更 {babacodechange.keibago(race_info.baba_code)}{race_info.race_no}R {race_info.race_time}→{race_time}')
                                race_info.race_time = race_time
            # 2秒待機
            time.sleep(2)

        # 初期処理の場合のみログ出力
        if init_flg:
            logger.info(f'初期処理終了 開催場数：{len(self.baba_url)} 記録対象レース数：{len(self.race_info)}')

    def time_check(self):
        '''次のオッズ記録時間までの秒数を計算する'''
        logger.info('オッズ記録時間チェック処理開始')
        # 現在時刻取得
        NOW = jst.now()
        # 次のx時x分00秒
        NEXT_MINITURES = NOW + datetime.timedelta(seconds = 60 - int(jst.second()))

        # 次の取得時間をリセット
        self.next_get_time = NOW + datetime.timedelta(days = 1)

        # 各レース毎に次のx分00秒が記録対象かチェック
        for race in self.__race_info:

            # 記録待ちの場合
            if race.record_flg == '0':
                # 次のx分00秒からレース発走までの時間
                time_left = int((race.race_time - NEXT_MINITURES).total_seconds())

                # 発走12分よりも前の場合
                if time_left > 720:
                    self.next_get_time = jst.time_min(self.next_get_time, race.race_time - datetime.timedelta(seconds = 720))
                # 発走12分前から1分以内の場合
                elif time_left >= 60:
                    race.record_flg = '1'
                    self.next_get_time = NEXT_MINITURES
                # 発走1分前から発走後20分以内の場合
                elif time_left > -1200:
                    self.next_get_time = jst.time_min(self.next_get_time, race.race_time + datetime.timedelta(seconds = 1200))
                # 発走後20分以降の場合
                else:
                    race.record_flg = '2'
                    self.next_get_time = NEXT_MINITURES

        logger.info(f'次の記録時間まで{(self.next_get_time - jst.now()).total_seconds()}秒')

    def get_odds(self, race):
        '''(単勝・複勝)オッズの取得・記録を行う'''
        # オッズのテーブルを取得
        odds_table = pd.read_html(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/OddsTanFuku?k_raceDate={Nar.RACE_DATE}&k_raceNo={race.race_no}&k_babaCode={race.baba_code}')[0]
        logger.info(f'{babacodechange.keibago(race.baba_code)}{race.race_no}Rの{"暫定" if race.record_flg == "1" else "最終"}オッズテーブル取得')
        # 馬番・単勝オッズ・複勝オッズの列のみ抽出
        odds_data = odds_table.loc[:, ['馬番', '単勝オッズ', odds_table.columns[4], odds_table.columns[5]]]
        # 現在時刻(yyyyMMddHHMMSS)カラムの追加
        odds_data['time'] = [jst.time() for _ in range(len(odds_data))]
        # 結合用にカラム名振り直し
        odds_data.set_axis(self.write_data.columns, axis = 1, inplace = True)
        # 一時保存用変数に格納
        self.write_data = pd.concat([odds_data, self.write_data])

    def record_odds(self):
        '''取得したオッズをooに書き込む'''
        writecsv.write_csv()

        # 出力待ちのフラグを変更する
        for race in self.race_info:
            # 暫定オッズフラグの変更
            if race.record_flg == '3':
                race.record_flg = '0'
            # 最終オッズフラグの変更
            if race.record_flg == '4':
                race.record_flg = '-1'

    def end_check(self):
        '''全レース記録済みかのチェックを行う'''
        for race in self.race_info:
            if race.record_flg != '-1':
                return True
        return False

class RaceInfo():
    '''各レースの情報を保持を行う

    Instance Parameter:
       baba_code(str) : 競馬場コード
       race_no(str) : レース番号,xxRのxxの部分
       race_time(datetime) : 発走時刻
       record_flg(str) : 0,記録時刻待ち
                         1,暫定オッズ取得待ち
                         2,最終オッズ取得待ち
                         3,暫定オッズ出力待ち
                         4,最終オッズ出力待ち
                         -1,最終オッズ出力済
       TODO 統合時に導入 jra_flg(bool) : T,中央 F,地方
    '''

    def __init__(self, baba_code, race_no, race_time):
        self.__baba_code = baba_code
        self.__race_no = race_no
        self.__race_time = race_time
        self.__record_flg = '0'

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

    @race_time.setter
    def race_time(self, race_time):
        self.__race_time = race_time

    @record_flg.setter
    def record_flg(self, record_flg):
        self.__record_flg = record_flg

# 動作確認用
if __name__ == '__main__':

    # ログ用インスタンス作成
    logger = logger.Logger()

    logger.info('地方競馬オッズ記録システム起動')

    # 地方競馬用インスタンス作成
    nar = Nar()

    # 全レース記録済かチェック
    while nar.end_check():

        while True:
            # 発走時間更新
            nar.get_race_info()

            # 発走までの時間チェック
            nar.time_check()

            # 次の記録時間までの時間(秒)
            time_left = int((nar.next_get_time - jst.now()).total_seconds())

            # 11分以上なら10分後に発走時刻再チェック
            if time_left > 660:
                time.sleep(600)
            elif time_left > 1:
                time.sleep(time_left)
                break
            else:
                break

        # 暫定オッズを先に取得
        for count, race in enumerate(nar.race_info):
            if race.record_flg == '1':
                nar.get_odds(race)
                race.record_flg = '3'

            # 5レースごとに1秒待機
            if count % 5 == 0 and count != 0:
                time.sleep(1)

        # 暫定オッズ取得後に最終オッズを取得
        for race in nar.race_info:
            if race.record_flg == '2':
                nar.get_odds(race)
                race.record_flg = '4'

            # x分50秒になるまで3秒間隔で取得
            if int(jst.second()) <= 50:
                time.sleep(3)
            else:
                break

        # 記録データが格納されていてx分50秒を過ぎていなければ記録
        if int(jst.second()) <= 50 and len(nar.race_data) != 0:
            nar.record_odds()