import time
import requests
import pandas as pd
from common import Logger, Soup, Jst, WriteSheet, CourseCodeChange

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

        for place_num in place_nums:
            LIST_URL = 'https://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList'
            k_raceDate = f'{jst.year}%2f{jst.month}%2f{jst.day}'
            soup = Soup.get_soup(f'{LIST_URL}?k_raceDate={k_raceDate}&k_babaCode={place_num}')
            print(soup)


if __name__ == '__main__':
    jst = Jst.Jst()

    nrd = NarRecordOdds()
    nrd.get_race_list()