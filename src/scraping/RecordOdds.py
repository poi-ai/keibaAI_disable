import datetime
import json
import time
import pandas as pd
import requests
from common import Logger, Soup, Jst, WriteSheet, CourseCodeChange
from requests_html import HTMLSession

def main():
    '''メイン処理'''

    # 全レース記録終了までループ
    while True:
        # 記録開始前の時刻を取得
        NOW = jst.now()

        # オッズの記録処理
        time_check()

        #次の記録時間
        sleep_time = get_recent_time(NOW) - 3

        # TODO debug
        logger.info(str(sleep_time))

        # 全レース記録済みならば処理終了
        if not 0 in record_flg:
            logger.info('本日のオッズ記録は終了しました')
            exit()

        # 直近のレース時刻まで処理停止
        time.sleep(sleep_time)

def get_race_id(jra_flg):
    '''稼働日のレースIDを取得

    Args:
        jra_flg(int):1[中央(JRA)],0[地方(NAR)]

    Returns:
        race_id_list(list):稼働日のレースID

    '''

    # 稼働日のレースIDを格納
    race_id_list = []

    # 稼働日にレースが行われる競馬場のリストページを格納
    soups = []

    # HTML取得
    if jra_flg == 1:
        # 中央の場合は1つのGETで全てのレースID(URL)を取得できる
        soups.append(Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY))
    elif jra_flg == 0:
        # 地方の場合は各競馬場ごとにGETリクエストする必要がある
        # 稼働日の開催情報の取得
        course_soup = Soup.get_soup('https://nar.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)
        course_links = course_soup.find('ul', class_='RaceList_ProvinceSelect')

        # 開催なしの場合
        if course_links == []:
            return []

        # 稼働日の各競馬場のレース一覧URLを取得
        links = course_links.find_all('a')
        for link in links:
            soups.append(Soup.get_soup('https://nar.netkeiba.com/top/race_list_sub.html' + link.get('href') + '&kaisai_date=' + TODAY))

    # レースIDを取得
    for soup in soups:
        # 各レースへのリンクを取得
        links = soup.find_all('a')

        # リンクがない(= 開催なし)の場合
        if links == []:
            return []

        # レースURLからレースIDを抽出
        for link in links:
            a_url = link.get('href')
            # 出走前のレースは「shutuba.html」
            # 出走後のレースは「result.html」がリンクされている
            if 'shutuba.html' in a_url:
                race_id_list.append(a_url[29:41])
            elif 'result.html' in a_url:
                race_id_list.append(a_url[28:40])

    return race_id_list

def time_check():
    '''レースの時刻チェックを行い記録対象かの判断を行う'''

    # 各レース時刻の取得
    time_schedule = get_race_time()

    # 現在時刻とレース時刻を比較
    for idx in range(len(time_schedule)):

        # 既に記録が終了しているレースはチェックを行わない
        if record_flg[idx] == 1:
            continue

        # 現在時刻取得
        NOW = jst.now()

        # 取得したレース予定時刻をdatetime型に変換
        race_time = datetime.datetime.strptime(TODAY + time_schedule[idx], '%Y%m%d%H:%M')

        # レースまでの秒数(レース予定時刻 - 現在の時刻)を設定
        diff_time = int((race_time - NOW).total_seconds())

        # レースまでの残り時間によって記録を行う
        if 50 <= diff_time <= 790:
            # レース13分10秒前から50秒前まで暫定オッズを取得
            get_odds(jra_race_id_list[idx], race_time.strftime('%H%M'), 0)
            logger.info('{}{}Rの{}分前オッズを記録しました'.format(CourseCodeChange.netkeiba(jra_race_id_list[idx][4:6]), jra_race_id_list[idx][10:], int(diff_time / 60)))
        elif diff_time <= -1200:
            # レース20分後に最終オッズを取得
            get_odds(jra_race_id_list[idx], race_time.strftime('%H%M'), 1)
            logger.info('{}{}Rの最終オッズを記録しました'.format(CourseCodeChange.netkeiba(jra_race_id_list[idx][4:6]), jra_race_id_list[idx][10:]))

            # 最終オッズまで記録したレースは記録済みにする
            record_flg[idx] = 1

def get_odds_jra(race_id,  race_time, complete_flg):
    '''中央競馬のレースのオッズ取得を行う

    Args:
        race_id(str):取得対象のレースID
        race_time(str,HHMM):取得対象レースの出走(予定)時刻
        complete_flg(int):取得対象が最終オッズか 1:最終 0:それ以外

    '''
    # レースIDからURLとパラメータを設定し、JSONを受け取る
    r = requests.get('https://race.netkeiba.com/api/api_get_jra_odds.html?race_id=' + race_id + '&type=1&action=init&sort=odds&compress=0')
    data = r.json()

    # 受け取ったJSONをDataFrameに成形する
    race_odds = pd.concat([pd.DataFrame.from_dict(data['data']['odds']['1']).T[0], pd.DataFrame.from_dict(data['data']['odds']['2']).T[[0, 1]]], axis = 1)

    # レース情報(レースID, 記録時刻, 発走(予定)時刻, 最終オッズフラグ)を頭数分設定
    race_info = [[race_id, jst.time(), race_time, complete_flg] for _ in range(len(race_odds))]

    # 切り出したデータを結合
    df = pd.concat([pd.DataFrame(race_info),  race_odds], axis = 1)

    # 各データのカラム名を設定
    df_header = ['レースID', '記録時刻', '発走時刻', '最終オッズフラグ', '馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ']

    # TODO


def get_odds_nar(race_id, race_time, complete_flg):
    '''地方競馬のレースのオッズ取得を行う

    Args:
        race_id(str):取得対象のレースID
        race_time(str,HHMM):取得対象レースの出走(予定)時刻
        complete_flg(int):取得対象が最終オッズか 1:最終 0:それ以外

    '''
    # レースIDからURLを指定しHTML情報の取得
    URL = 'https://nar.netkeiba.com/odds/odds_get_form.html?type=b1&race_id=' + race_id + '&rf=shutuba_submenu'

    # TBL情報の取得&エンコーディング
    odds = pd.read_html(URL, encoding='utf-8')

    race_odds = pd.concat([odds[0][['馬番','オッズ']], odds[1]['オッズ'].str.split(' - ', expand = True)], axis = 1)

    # レース情報(レースID, 記録時刻, 発走(予定)時刻, 最終オッズフラグ)を頭数分設定
    race_info = [[race_id, jst.time(), race_time, complete_flg] for _ in range(len(race_odds))]

    # 切り出したデータを結合
    df = pd.concat([pd.DataFrame(race_info), race_odds], axis = 1)

    # 各データのカラム名を設定
    df_header = ['レースID', '記録時刻', '発走時刻', '最終オッズフラグ', '馬番', '単勝オッズ', '複勝下限オッズ', '複勝上限オッズ']

    # TODO 
    
    # Googleスプレッドシートに記載を行う
    WriteSheet.write_spread_sheet(df, int(jst.time()[:6]), df_header)

def get_race_time():
    '''レース時刻の取得を行う

    Returns:
        race_time(list):稼働日のレース発走時刻を持つリスト

    '''
    # 稼働日の開催情報サイトのHTMLを取得
    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)

    # レース時刻を格納するリスト
    race_time = []

    # HTMLからレース時間記録用のクラス名を抽出
    times = soup.find_all('span', class_='RaceList_Itemtime')

    # タグと空白を削除しリストに追加
    for time in times:
        race_time.append(time.get_text(strip = False)[:5])

    # レース時間を記録したリストを返す
    return race_time

def get_recent_time(NOW):
    '''次の記録時間を取得する

    Args:
        NOW(datetime):前ループでの記録開始時刻

    Returns:
        recent_time(int):前ループから60秒後以降で直近の記録までの時間

    '''

    # 次の取得までの最短時間
    recent_time = 99999

    # 各レース時刻の取得
    time_schedule = get_race_time()

    # 現在時刻とレース時刻を比較
    for idx in range(len(time_schedule)):

        # 取得したレース予定時刻をdatetime型に変換
        race_time = datetime.datetime.strptime(TODAY + time_schedule[idx], '%Y%m%d%H:%M')

        # レースまでの秒数(レース予定時刻 - 現在の時刻)を設定
        diff_time = (race_time - NOW).seconds

        # 記録が終了していない
        if record_flg[idx] == 0:
            # 60秒後に記録対象となる場合
            if 50 <= diff_time - 60 <= 790 or -1260 <= diff_time - 60 <= -1200:
                return 60
            # 60秒後にレース締め切り時間を越す場合
            elif diff_time - 60 <= 50:
                recent_time = min(recent_time, diff_time - 60 + 1200)
            # 60秒後はまだ一度も記録していない場合
            elif 790 <= diff_time - 60:
                recent_time = min(recent_time, diff_time - 60 - 790)

    return recent_time

if __name__ == '__main__':
    # 日本時間取得クラスのインスタンス作成
    jst = Jst.Jst()

    # 簡易型ロギングクラスのインスタンス作成
    logger = Logger.Logger()

    # HTMLSessionのインスタンス作成
    session = HTMLSession()

    # 稼働日の日付を取得
    TODAY = jst.date()

    # 稼働日のレースIDを取得
    jra_race_id_list = get_race_id(1)
    nar_race_id_list = get_race_id(0)

    # TODO
    print(jra_race_id_list)
    print(nar_race_id_list)
    
    exit()

    # 稼働日にレースがない場合
    if jra_race_id_list == []:
        logger.info('本日の中央開催はありません')

    logger.info('記録対象レース数：{0}'.format(len(jra_race_id_list)))

    # 記録済みフラグを設定
    record_flg = [0 for _ in range(len(jra_race_id_list))]

    # メイン処理
    main()
