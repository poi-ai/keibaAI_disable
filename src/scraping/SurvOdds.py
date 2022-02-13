import datetime
import time
import pandas as pd
from common import Soup
from requests_html import HTMLSession

def main():    
    # HTML取得
    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)
    
    # 稼働日のレースIDを格納するリスト
    race_id = []
    
    # aタグ取得
    links = soup.find_all('a')

    # 空(= 開催なし)の場合 
    if links == []:
        print('本日は中央開催はありません')
        exit()
    
    # レースURLからIDのみ抽出
    for link in links:
        a_url = link.get('href')
        # 出走前のレースは「shutuba.html」、
        # 出走後のレースは「result.html」がリンクされている
        if 'shutuba.html' in a_url:
            race_id.append(a_url[29:41])
        elif 'result.html' in a_url:
            race_id.append(a_url[28:40])

    # レース記録フラグ(0:未、1:済)
    rec_flag = pd.DataFrame(index = race_id, 
                            columns = ['10', '9', '8', '7', '6', '5', '4',
                                       '3', '2', '1', 'confirm', 'schedule_time'])
    # 0埋め
    rec_flag.fillna(0, inplace = True)

    # 全レース記録終了までループ
    while True:
        rec_flag = target_check(rec_flag)

        # 終了チェック
        if not 0 in rec_flag:
            exit()

def target_check(rec_flag):
    # レース時刻取得
    time_schedule = get_race_time()

    # レース記録フラグを探索
    for idx in rec_flag.index:

        # 現在時刻取得(JST環境)
        NOW = datetime.datetime.now()

        # 現在時刻取得(UTC環境)
        # NOW = datetime.datetime.now() + datetime.timedelta(hours = 9)

        target_clm = ''

        # 今スクレイピングした予定時刻を設定
        race_time = datetime.datetime.strptime(TODAY + time_schedule[idx], '%Y%m%d%H:%M')
        
        # 前ループでスクレイピングした予定時刻を設定
        before_schedule_time = datetime.datetime.strptime(TODAY + rec_flag['schedule_time'][idx], '%Y%m%d%H:%M')
        
        # レースまでの秒数(レース予定時刻 - 現在の時刻)を設定
        remaining_time = (race_time - NOW).seconds

        # 前回スクレイピングからの予定時刻のズレを設定
        diff_time = (race_time - before_schedule_time).minutes
        
        # 記録フラグの一番左の0のカラムを設定
        for clm in rec_flag:
            if rec_flag[clm][idx] == 0:
                target_clm = clm
                break
        
        # 最終オッズのみ未記録の場合
        if target_clm == 'confirm':
            # レース時間5分後に最終オッズを記録
            if remaining_time <= -300:
                rec_flag[clm][idx], success_flag = get_odds()
                
                # 書き込み、レコード削除

        else:
            if diff_time < -60:
                # TODO レース時間が前倒しになった場合(ない？)
                pass
            elif diff_time > 60:
                # TODO レース時間が後ろ倒しになった場合
                pass
                
            if (int(clm) - 1) * 60 < remaining_time <= int(clm) * 60:
                # TODO オッズ取得
                rec_flag[clm][idx], success_flag = get_odds(rec_flag, idx)
                pass
        
        # レース予定時刻を更新
        if success_flag:
            rec_flag['schedule_time'][idx] = NOW.strftime('%H:%M')
        
    return rec_flag

def get_odds(rec_flag, race_id):
    URL = 'https://race.netkeiba.com/odds/index.html?type=b1&race_id=' + race_id + '&rf=shutuba_submenu'
    r = session.get(URL)
    r.html.render()

    win = pd.read_html(r.html.html)[0].iloc[:, [1, 5]]
    place = pd.read_html(r.html.html)[1]['オッズ'].str.split(' - ', expand = True)

    odds = pd.concat([win, place], axis = 1)
    odds.rename(columns={'オッズ': '単勝', 0: '複勝下限', 1: '複勝上限'}, inplace = True)
    print(odds)
    # return rec_flag, True

def get_race_time():
    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)

    race_time = []

    # レース時間用のクラス名を抽出
    times = soup.find_all('span', class_='RaceList_Itemtime')
    
    # タグと空白を削除
    for time in times:
        race_time.append(time.get_text(strip = False)[:5])

    return race_time

if __name__ == '__main__':
    df_record = pd.DataFrame(columns = ['race_id', 'horse_num', '10win', '10place_min', '10place_max', 
                                        '09win', '09place_min', '09place_max', '08win', '08place_min', '08place_max', 
                                        '07win', '07place_min', '07place_max', '06win', '06place_min', '06place_max',
                                        '05win', '05place_min', '05place_max', '03win', '03place_min', '03place_max',
                                        '02win', '02place_min', '02place_max', '01win', '01place_min', '01place_max', 
                                        'confirm_win', 'confirm_place_min', 'confirm_place_max',
                                        ])

    session = HTMLSession()
    get_odds(0, '202205010201')

    exit()
    # 時間取得。日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.now().strftime('%Y%m%d')

    # 時間取得herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')
    
    # HTMLSessionのインスタンス作成
    session = HTMLSession()

    # 実装確認用に中央開催日の日付を代入
    TODAY = '20220123'
    
    # メイン処理
    main()
