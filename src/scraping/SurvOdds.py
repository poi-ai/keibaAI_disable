import datetime
import pandas as pd
from common import Soup

def main():
    # 日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.now().strftime('%Y%m%d')
    TODAY = '20220123'

    # herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')
    
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

    # レース記録フラグ(0:未、1：済)
    rec_flag = pd.DataFrame(index = race_id, 
                            columns = ['10min', '9min', '8min', '7min', '6min'
                                       '5min', '4min', '3min', '2min', '1min', 'confirm'])
    rec_flag.fillna(0, inplace = True)

    while True:
        rec_flag = target_check(rec_flag, get_race_time(TODAY), TODAY)

        exit()
        # 開催終了チェック
        if not 0 in rec_flag and not 1 in rec_flag:
            print('本日のレースは終了しました')
            exit()

def target_check(rec_flag, time_schedule, TODAY):
    # 現在時刻取得(JST環境)
    NOW = datetime.datetime.now()

    # 現在時刻取得(UTC環境)
    # NOW = datetime.datetime.now() + datetime.timedelta(hours = 9)

    # レース記録フラグを探索
    for i in rec_flag:

        print(i)
        exit()
        # 記録前の場合
        if rec_flag[i] == 0:
            print(time_schedule[i])
            race_time = datetime.datetime.strptime(TODAY + time_schedule[i], '%Y%m%d%H:%M')
            remaining_time = (race_time - NOW).seconds
            if remaining_time < -300:
                rec_flag[i] = -1
            exit()
        # 記録中の場合
        elif rec_flag[i] == 1:
            pass
    # get_odds()
    return rec_flag

def get_odds():
    pass

def get_race_time(TODAY):
    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)

    race_time = []

    # レース時間用のクラス名を抽出
    times = soup.find_all('span', class_='RaceList_Itemtime')
    
    # タグと空白を削除
    for time in times:
        race_time.append(time.get_text(strip = False)[:5])

    return race_time

if __name__ == '__main__':
    main()
