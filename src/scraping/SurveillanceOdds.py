import datetime
from common import Soup

def main():
    # 日本時間(JST)の環境で実行する場合はこっち
    TODAY = datetime.datetime.today().strftime('%Y%m%d')
    # herokuなど協定世界時(UTC)の環境で日本時間に合わせる場合は↓を使用
    # TODAY = (datetime.datetime.now() + datetime.timedelta(hours = 9)).strftime('%Y%m%d')

    get_table(TODAY)


def get_table(date):
    URL = 'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=' + date
    soup = Soup.get_soup(URL)
    race_data = soup.find_all('li', class_='RaceList_DataItem')

    # 本日の開催チェック
    if race_data == []:
        return 

if __name__ == '__main__':
    main()