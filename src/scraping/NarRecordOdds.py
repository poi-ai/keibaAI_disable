import pandas as pd
from common import Jst, Soup, CourseCodeChange

class NarRecordOdds():
    def __init__(self):
        pass

    def get_race_list(self):
        '''稼働日のレースIDを取得する

        Returns:
            race_list(list):レースIDを持つリスト

        '''

        # keiba.go.jpから稼働日に開催のある競馬場名を取得する
        place_names = pd.read_html('https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')[0][0].values.tolist()

        # 競馬場名をkeiba.goのパラメータで使われている競馬場番号へ変換する
        place_nums = [CourseCodeChange.keibago(place_name) for place_name in place_names]

        # 各競馬場ごとにレース数と発走時刻を取得する
        for place_num in place_nums:
            # 日付パラメータ
            k_raceDate = f'{jst.year()}%2f{jst.month().zfill(2)}%2f{jst.day().zfill(2)}'
            # レース情報をDataFrame型で取得
            race_info = pd.read_html(f'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList?k_raceDate={k_raceDate}&k_babaCode={place_num}')[0]

            # TODO 各レース情報をdic型だか自作型で記録
            exit()

# 実装確認用
if __name__ == '__main__':
    jst = Jst.Jst()

    nrd = NarRecordOdds()
    nrd.get_race_list()