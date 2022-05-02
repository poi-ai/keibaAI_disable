import datetime
import time
import pandas as pd
from common import Logger, Soup, Jst, WriteSheet as WS
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

        # debug
        logger.info(str(sleep_time))

        # 全レース記録済みならば処理終了
        if not 0 in record_flg:
            logger.info('本日のオッズ記録は終了しました')
            exit()
        
        # 直近のレース時刻まで処理停止
        time.sleep(sleep_time)

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
            get_odds(race_id_list[idx], race_time.strftime('%H%M'), 0)
        elif diff_time <= -1200:
            # レース20分後に最終オッズを取得
            get_odds(race_id_list[idx], race_time.strftime('%H%M'), 1)

            # 最終オッズまで記録したレースは記録済みにする
            record_flg[idx] = 1

def get_odds(race_id, race_time, complete_flg):
    '''レースのオッズ取得を行う

    Args:
        race_id(str):取得対象のレースID
        race_time(str,HHMM):取得対象レースの出走(予定)時刻
        complete_flg(int):取得対象が最終オッズか 1:最終 0:それ以外

    '''
    # レースIDからURLを指定しHTML情報の取得
    URL = 'https://race.netkeiba.com/odds/index.html?type=b1&race_id=' + race_id + '&rf=shutuba_submenu'
    
    # レンダリング、失敗したら10回までやり直し
    retry = 0
    while True:
        try:
            r = session.get(URL)
            r.html.render()
            break
        except:
            time.sleep(1)
            logger.error('レンダリングに失敗:' + race_id)
            retry += 1
            if retry >= 10:
                logger.error('レンダリングに10回失敗したため処理を終了します')
                exit()

    # 単勝TBLから馬番と単勝オッズの切り出し
    win_odds = pd.read_html(r.html.html)[0].iloc[:, [1, 5]]

    # 複勝TBLから複勝オッズの切り出し
    place_odds = pd.read_html(r.html.html)[1]['オッズ'].str.split(' - ', expand = True)

    # TODO あとでまとめる
    # 記録時刻を頭数分用意
    time_stump = [jst.time() for _ in range(len(win_odds))]
    
    # レースIDを頭数分用意
    race_id = [race_id for _ in range(len(win_odds))]

    # 発走(予定)時刻を取得
    race_time = [race_time for _ in range(len(win_odds))]

    # 最終オッズフラグを用意
    complete_flg = [complete_flg for _ in range(len(win_odds))]

    # 切り出したデータを結合
    odds = pd.concat([pd.DataFrame(race_id), pd.DataFrame(time_stump),pd.DataFrame(race_time), pd.DataFrame(complete_flg),  win_odds, place_odds], axis = 1)
    #odds.rename(columns={'オッズ': '単勝', 0: '複勝下限', 1: '複勝上限'}, inplace = True)

    # Googleスプレッドシートに記載を行う
    WS.write_spread_sheet(odds, int(time[0][:6]))

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
