import datetime
from common import Soup

def main():
    # 日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.now().strftime('%Y%m%d')

    # herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')

    soup = Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)
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
        if 'shutuba.html' in a_url:
            race_id.append(a_url[29:41])
        elif 'result.html' in a_url:
            race_id.append(a_url[28:40])

    # レース終了フラグ(0:未、1:監視中、-1：済)
    rec_flag = [0 for _ in range(len(race_id))]

    while True:
        rec_flag = target_check(rec_flag, get_race_time(TODAY), race_id, TODAY)

        # 開催終了チェック
        if not 0 in rec_flag and not 1 in rec_flag:
            print('本日のレースは終了しました')
            break

        print(rec_flag)
        print(get_race_time(TODAY))
        print(race_id)


def target_check(rec_flag, time_schedule, race_id, TODAY):
    NOW = datetime.datetime.now()

    for i in range(len(rec_flag)):
        if rec_flag[i] == 0:
            print(time_schedule[i])
            race_time = datetime.datetime.strptime(TODAY + time_schedule[i], '%Y%m%d%H:%M')
            remaining_time = (race_time - NOW).seconds
            if remaining_time < -300:
                rec_flag[i] = -1
            

            exit()
        elif rec_flag[i] == 1:
            pass
    # get_odds()
    return rec_flag

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
