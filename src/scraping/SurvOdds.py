import datetime
import time
import pandas as pd
import WriteSheet as WS
from common import Logger, Soup
from requests_html import HTMLSession

def main():
    '''メイン処理'''

    # 全レース記録終了までループ
    while True:
        # 記録開始前の時刻を取得(JST環境)
        NOW = datetime.datetime.now()

        # 記録開始前の時刻を取得(UTC環境)
        #NOW = datetime.datetime.now() + datetime.timedelta(hours = 9)

        # オッズの記録処理
        time_check()

        #次の記録時間
        sleep_time = get_recent_time(NOW) - 3
        
        # 直近のレース時刻まで処理停止(JST)
        time.sleep(sleep_time)

        # 直近のレース時刻まで処理停止(UTC)
        #time.sleep(sleep_time)

        # 全レース記録済みならば処理終了
        if not 0 in record_flg:
            logger.info('本日のオッズ記録は終了しました')
            exit()

def get_race_id():
    '''稼働日のレースIDを取得

    Returns:
        race_id_list(list):稼働日のレースID
    
    '''

    # 稼働日のレースIDを格納
    race_id_list = []
       
    # HTML取得
    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)
    
    # リンクのついているaタグの取得
    links = soup.find_all('a')

    # aタグがない(= 開催なし)の場合 
    if links == []:
        return []
    
    # レースURLからレースIDを抽出
    for link in links:
        a_url = link.get('href')
        # 出走前のレースは「shutuba.html」、
        # 出走後のレースは「result.html」がリンクされている
        if 'shutuba.html' in a_url:
            race_id_list.append(a_url[29:41])
        elif 'result.html' in a_url:
            race_id_list.append(a_url[28:40])
    
    return race_id_list

def time_check():
    '''取得対象レースの時刻チェックを行う'''
    
    # 各レース時刻の取得
    time_schedule = get_race_time()

    # 現在時刻とレース時刻を比較
    for idx in range(len(time_schedule)):

        # 現在時刻取得(JST環境)
        NOW = datetime.datetime.now()

        # 現在時刻取得(UTC環境)
        # NOW = datetime.datetime.now() + datetime.timedelta(hours = 9)

        # 取得したレース予定時刻をdatetime型に変換
        race_time = datetime.datetime.strptime(TODAY + time_schedule[idx], '%Y%m%d%H:%M')

        # レースまでの秒数(レース予定時刻 - 現在の時刻)を設定
        diff_time = int((race_time - NOW).total_seconds())

        # レースまでの残り時間によって記録を行う
        if 50 <= diff_time <= 790:
            # レース13分10秒前から50秒前まで暫定オッズを取得
            get_odds(race_id_list[idx])
        elif diff_time <= -1200:
            # レース20分後に最終オッズを取得
            get_odds(race_id_list[idx])

            # 最終オッズまで記録したレースは記録済みにする
            record_flg[idx] = 1

    return record_flg

def get_odds(race_id):
    '''レースのオッズ取得を行う

    Args:
        race_id(str):取得対象のレースID

    '''
    # レースIDからURLを指定しHTML情報の取得
    URL = 'https://race.netkeiba.com/odds/index.html?type=b1&race_id=' + race_id + '&rf=shutuba_submenu'
    r = session.get(URL)
    r.html.render()

    # 単勝TBLから馬番と単勝オッズの切り出し
    win_odds = pd.read_html(r.html.html)[0].iloc[:, [1, 5]]

    # 複勝TBLから複勝オッズの切り出し
    place_odds = pd.read_html(r.html.html)[1]['オッズ'].str.split(' - ', expand = True)

    # 記録時刻を頭数分用意
    time_copy = [datetime.datetime.now().strftime('%Y%m%d%H%M%S') for _ in range(len(win_odds))]
    
    # レースIDを頭数分用意
    race_id_copy = [race_id for _ in range(len(win_odds))]

    # 切り出したデータを結合
    odds = pd.concat([pd.DataFrame(race_id_copy), pd.DataFrame(time_copy), win_odds, place_odds], axis = 1)
    #odds.rename(columns={'オッズ': '単勝', 0: '複勝下限', 1: '複勝上限'}, inplace = True)

    # Googleスプレッドシートに記載を行う
    WS.write_spread_sheet(odds, time_copy[0][:6])

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

    # 時間取得。日本時間(JST)の実行環境で実行する場合はこっち
    TODAY = datetime.datetime.now().strftime('%Y%m%d')

    # 時間取得。herokuなど協定世界時(UTC)の実行環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')

    # ロギングの設定
    logger = Logger.Logger()
    
    # HTMLSessionのインスタンス作成
    session = HTMLSession()

    # 動作確認用に中央開催日の日付を設定
    TODAY = '20220424'
    
    # 稼働日のレースIDを取得
    race_id_list = get_race_id()

    # 稼働日にレースがない場合
    if race_id_list == []:
        logger.info('本日の中央開催はありません')
        exit()
    else:
        logger.info('記録対象レース数：{0}'.format(len(race_id_list)))

    # 記録済みフラグを設定
    record_flg = [0 for _ in range(len(race_id_list))]

    # メイン処理
    main()
