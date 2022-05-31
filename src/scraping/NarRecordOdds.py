from datetime import datetime
import pandas as pd
from common import Jst, Soup, CourseCodeChange

class Nar(Jst):
    '''地方競馬オッズ取得クラス

    Args:
       baba_race_url(list<str>) : 各競馬場のレース情報が記載されたURL一覧
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_time(int) : 次回オッズ取得までの秒数
       write_data(DataFrame) : 書き込み用データ
    '''
    # 日付のGETパラメータ
    RACE_DATE = f'{Jst.year()}%2f{Jst.month().zfill(2)}%2f{Jst.day().zfill(2)}'

    def __init__(self):
        self.__baba_race_url = []
        self.__race_info = []
        self.__next_time = -1
        self.__write_data = pd.DataFrame(columns = ['馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ'])

    def parameter_set(self):
        '''稼働日のレース情報をセットする'''

        # keiba.go.jpから稼働日に開催のある競馬場名を取得する
        baba_names = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')[0][0].values.tolist()

        # 競馬場名をkeiba.goのパラメータで使われている競馬場番号へ変換する
        baba_codes = [CourseCodeChange.keibago(place_name) for place_name in baba_names]

        # 各競馬場ごとにレース数と発走時刻を取得する
        for baba_code in baba_codes:
            # レースリスト一覧が載っているページのURLを保存
            self.__baba_race_url.append(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate={Nar.RACE_DATE}&k_babaCode={baba_code}')

    def get_race_info(self):
        '''レース情報を取得'''
        for race_url in self.__baba_race_url:
            # レース情報をDataFrame型で取得
            race_list = pd.read_html(race_url)[0]

            # 1レースごとの情報取得
            for idx in race_list.index:
                # 1レース切り出し
                race = race_list.loc[idx]
                # 時間をdatetime型に変換
                race_time = datetime(int(Jst.year()), int(Jst.month()), int(Jst.day()), int(race[1][:2]), int(race[1][3:]), 0)
                # クラス化して保存(競馬場コード,レース番号,発走時刻)
                self.__race_info.append(RaceInfo(race_url[-2:], race[0].replace('R', ''), race_time))

    def time_check(self):
        '''次のオッズ記録時間までの秒数を計算する'''
        # 現在時刻取得
        NOW = Jst.now()
        # 秒数をリセット
        self.__next_time == 9999999

        # 各レース毎に次のx分00秒が記録対象かチェック
        for race in self.__race_info:
            # 次のx分00秒からレース発走までの時間
            # TODO 発走時間過ぎの挙動を要チェック
            time_left = race.race_time - NOW - int(Jst.second()) + 60
            # レース1分前から12分以内なら記録
            if 60 <= time_left <= 720:
                self.get_odds(race)
            # レース20分以後かつ未記録フラグか立っているなら最終オッズを記録
            if race.record_flg == '0' and time_left <= -1200:
                self.get_odds(race)
                race.record_flg = '1'

    def get_odds(self, race):
        '''(単勝・複勝)オッズの取得・記録を行う'''
        # オッズのテーブルを取得
        odds_table = pd.read_html(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/OddsTanFuku?k_raceDate={Nar.RACE_DATE}&k_raceNo={race.race_no}&k_babaCode={race.baba_code}')[0]
        # 馬番・単勝オッズ・複勝オッズの列のみ抽出
        odds_data = odds_table.loc[:, ['馬番', '単勝オッズ', odds_table.columns[4], odds_table.columns[5]]].rename(columns = self.write_data.columns)
        self.__write_data = pd.Concat([odds_data, self.__write_data])

    def record_odds(self):
        '''取得したオッズをooに書き込む'''
        # TODO WriteCsv.write_csv()
        # TODO WriteSheet.write_spread_sheet(Jst.month(), self.__write_data, odds_columns)

        # 最終オッズ出力待ちのデータを記録済にする
        for race in self.get_race_info:
            if race.record_flg == '1':
                race.record_flg = '-1'

class RaceInfo():
    '''各レースの情報を保持を行う

    Args:
       baba_code(str) : 競馬場コード
       race_no(str) : レース番号,xxRのxxの部分
       race_time(datetime) : 発走時刻
       record_flg(str) : 0,未記録・記録中 1,最終オッズ出力待ち -1,記録済
       TODO jra_flg(bool) : T,中央 F,地方
    '''

    def __init__(self, baba_code, race_no, race_time):
        self.__baba_code = baba_code
        self.__race_no = race_no
        self.__race_time = race_time
        self.__record_flg = 0

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
    nar = Nar()
    nar.parameter_set()