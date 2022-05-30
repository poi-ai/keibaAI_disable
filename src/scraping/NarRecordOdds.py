from datetime import datetime
import pandas as pd
from common import Jst, Soup, CourseCodeChange

class Nar():
    '''地方競馬オッズ取得クラス

    Args:
       baba_race_url(list<str>) : 各競馬場のレース情報が記載されたURL一覧
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_time(int) : 次回オッズ取得までの秒数
    '''

    def __init__(self):
        self.__baba_race_url = []
        self.__race_info = []
        self.__next_time = -1

    def parameter_set(self):
        '''稼働日のレース情報をセットする'''

        # keiba.go.jpから稼働日に開催のある競馬場名を取得する
        baba_names = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')[0][0].values.tolist()

        # 競馬場名をkeiba.goのパラメータで使われている競馬場番号へ変換する
        baba_codes = [CourseCodeChange.keibago(place_name) for place_name in baba_names]

        # 各競馬場ごとにレース数と発走時刻を取得する
        for baba_code in baba_codes:
            # 日付パラメータ
            k_raceDate = f'{jst.year()}%2f{jst.month().zfill(2)}%2f{jst.day().zfill(2)}'
            # レースリスト一覧が載っているページのURLを保存
            self.__baba_race_url.append(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate={k_raceDate}&k_babaCode={baba_code}')

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
                race_time = datetime(int(jst.year()), int(jst.month()), int(jst.day()), int(race[1][:2]), int(race[1][3:]), 0)
                # クラス化して保存(競馬場コード,レース番号,発走時刻)
                self.__race_info.append(RaceInfo(baba_code, race[0].replace('R', ''), race_time))

    def time_check(self):
        '''次のオッズ記録時間までの秒数を計算する'''
        # 現在時刻取得
        NOW = jst.now()
        # 秒数をリセット
        self.__next_time == 9999999

        # 各レース毎に次のx分00秒が記録対象かチェック
        for race in self.__race_info:
            # 次のx分00秒からレース発走までの時間
            # TODO 発走時間過ぎの挙動を要チェック
            time_left = race.race_time - NOW - int(jst.second()) + 60
            # レース1分前から12分以内なら記録
            if 60 <= time_left <= 720:
                self.record_odds(race)
            # レース20分以後かつ未記録フラグか立っているなら最終オッズを記録
            if race.record_flg == '0' and time_left <= -1200:
                self.record_odds(race)
                race.record_flg = '1'

    def record_odds(self, race):
        '''単複オッズの取得・記録を行う'''
        # オッズのテーブルを取得
        df = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/OddsTanFuku?k_raceDate=2022%2f05%2f30&k_raceNo=1&k_babaCode=11')[0]
        # 馬番・単勝オッズ・複勝オッズの列のみ抽出
        df2 = df.loc[:, ['馬番', '単勝オッズ', df.columns[4], df.columns[5]]]
        # TODO 書き込み用dfに追記

class RaceInfo():
    '''各レースの情報を保持を行う

    Args:
       baba_code(str) : 競馬場コード
       race_num(str) : レース番号,xxRのxxの部分
       race_time(datetime) : 発走時刻[HH:MM]
       record_flg(bool) : T,記録済 F,未記録・記録中
       TODO jra_flg(bool) : T,中央 F,地方
    '''

    def __init__(self, baba_code, race_num, race_time):
        self.__baba_code = baba_code
        self.__race_num = race_num
        self.__race_time = race_time
        self.__record_flg = False

    @property
    def baba_code(self):
        return self.__baba_code

    @property
    def race_num(self):
        return self.__race_num

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
    jst = Jst.Jst()

    nar = Nar()
    nar.record_odds(1)