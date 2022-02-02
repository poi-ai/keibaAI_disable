import datetime
import pandas as pd
from common import Soup

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
    rec_flag.fillna(0, inplace = True)

    while True:
        rec_flag = target_check(rec_flag)

        # 開催終了チェック
        if not 0 in rec_flag and not 1 in rec_flag:
            print('本日のレースは終了しました')
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
        race_time = datetime.datetime.strptime(TODAY + time_schedule[idx], '%Y%m%d%H:%M')
        before_schedule_time = datetime.datetime.strptime(TODAY + rec_flag['schedule_time'][idx], '%Y%m%d%H:%M')
        remaining_time = (race_time - NOW).seconds
        # timedeltaにminutesはない？
        diff_time = (race_time - before_schedule_time).minutes
        
        for clm in rec_flag:
            if rec_flag[clm][idx] == 0:
                target_clm = clm
                break
                
        if target_clm == 'confirm':
            if remaining_time <= -300:
                rec_flag[clm][idx], success_flag = get_odds()
                # TODO CSV書き込み、レコード削除
        else:
            if target_clm != 'comfirm':
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
        
        # 記録したらレース予定時刻を更新
        if success_flag:
            rec_flag['schedule_time'][idx] = NOW.strftime('%H:%M')
        
    return rec_flag

def get_odds(rec_flag, race_id):
    # TODO soup = Soup.get_soup('' + race_id + '')
    pass

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
    # 時間取得。日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.now().strftime('%Y%m%d')

    # 時間取得herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')
    
    # 実装確認用に中央開催日の日付を代入
    TODAY = '20220123'
    
    # メイン処理
    main()
