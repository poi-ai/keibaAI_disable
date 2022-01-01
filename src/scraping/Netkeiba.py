import csv
import sys
import time
from common import Soup
import datetime

def main():
    START_RACE_DATE, END_RACE_DATE = argv_check()
    get_years = START_RACE_DATE[:4]
    get_month = START_RACE_DATE[4:6]

    while True: # TODO 終了条件(終了月 < 対象月)追加
        hold_list = get_hold(get_years, get_month)
        race_list = get_race(hold_list)
        exit()

def get_race(hold_list):
    print(hold_list)
    for hold_date in hold_list:
        exit()
        soup = Soup.get_soup(hold_date)
        # TODO 特定の日付一覧から各レース取得

def get_hold(years, month):
    URL = 'https://race.netkeiba.com/top/calendar.html?year='\
          + years\
          + '&month='\
          + month

    soup = Soup.get_soup(URL)
    links = soup.find_all('a')
    hold_list = []
    for link in links:
        if 'kaisai_date' in link.get('href') :
            hold_list.append(link.get('href'))
    return hold_list

def argv_check():
    # 引数の数チェック
    if len(sys.argv) != 3:
        raise ValueError('入力した引数の数が間違っています')
    
    try:
        date_argv1 = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        date_argv2 = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')
    except:
        raise ValueError('入力した日付のフォーマットが間違っています')

    # 妥当性チェック
    if date_argv1 > date_argv2:
        raise ValueError('終了日が開始日より前の日付になっています')
    else:
        return sys.argv[1], sys.argv[2]

if __name__ == '__main__':
    main()