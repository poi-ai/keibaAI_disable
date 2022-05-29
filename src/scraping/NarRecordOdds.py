import pandas as pd
from common import Jst, Soup, CourseCodeChange

class Nar():
    '''地方競馬オッズ取得クラス

    Args:
       race_list_url(list<str>) : 各競馬場のレース情報が記載されたURL一覧
       race_info(list<RaceInfo>) : 各レース情報を持つリスト
       next_time(int) : 次回オッズ取得までの秒数
    '''

    def __init__(self):
        self.__race_list_url = []
        self.__race_info = []
        self.__next_time = -1

    def get_race_info(self):
        '''稼働日のレース情報を取得する'''

        # keiba.go.jpから稼働日に開催のある競馬場名を取得する
        baba_names = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')[0][0].values.tolist()

        # 競馬場名をkeiba.goのパラメータで使われている競馬場番号へ変換する
        baba_codes = [CourseCodeChange.keibago(place_name) for place_name in baba_names]

        # 各競馬場ごとにレース数と発走時刻を取得する
        for baba_code in baba_codes:
            # 日付パラメータ
            k_raceDate = f'{jst.year()}%2f{jst.month().zfill(2)}%2f{jst.day().zfill(2)}'
            # レースリストの記載のあるURLの取得
            race_list_url = f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate={k_raceDate}&k_babaCode={baba_code}'
            # URLを保存
            self.__race_list_url.append(race_list_url)
            # レース情報をDataFrame型で取得
            race_list = pd.read_html(race_list_url)[0]

            # 1レースごとの情報取得
            for idx in race_list.index:
                # 1レース切り出し
                race = race_list.loc[idx]
                # クラス化して保存(競馬場コード,レース番号,発走時刻)
                self.__race_info.append(RaceInfo(baba_code, race[0].replace('R', ''), race[1]))

    def time_check():
        '''次の記録時間を取得する'''
        pass

    def record_odds():
        '''単複オッズの取得・記録を行う'''
        pass

class RaceInfo():
    '''各レースの情報を保持を行う

    Args:
       baba_code(str) : 競馬場コード
       race_num(str) : レース番号,xxRのxxの部分
       race_time(str) : 発走時刻[HH:MM]
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

    nrd = Nar()
    nrd.get_race_info()