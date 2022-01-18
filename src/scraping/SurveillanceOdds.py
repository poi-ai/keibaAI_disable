import datetime
from common import Soup

def main():
    # 日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.today().strftime('%Y%m%d')

    # herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合はこっち
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')

    TODAY = '20220115'
    TODAY = '20220122'

    soup = get_soup(TODAY)
    race_id = []
    
    # aタグ取得
    links = soup.find_all('a')

    # 空(= 開催なし)の場合 
    if links == []:
        exit()
    
    # レースURLからIDのみ抽出
    for link in links:
        a_url = link.get('href')
        if 'shutuba.html' in a_url:
            race_id.append(a_url[29:41])

    # レース終了フラグ(0:未、1:監視中、-1：済)
    rec_flag = [0 for _ in range(len(race_id))]

    # TODO フラグ、レース時間から監視するレースを選ぶ 

def get_soup(TODAY):
    return Soup.get_soup('https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + TODAY)

def get_race_time(TODAY):
    soup = get_soup(TODAY)

    race_time = []

    # レース時間用のクラス名を抽出
    times = soup.find_all('span', class_='RaceList_Itemtime')
    
    # タグと空白を削除
    for time in times:
        race_time.append(time.get_text(strip = False)[:5])

    print(race_time)
    exit()

if __name__ == '__main__':
    main()