import csv
import sys
import time

import requests
from common import Soup
import datetime

def main():
    # 引数の妥当性チェック
    START_RACE_DATE, END_RACE_DATE = argv_check()

    # 開始日の年と月を抽出
    get_years = START_RACE_DATE[:4]
    get_month = START_RACE_DATE[4:6]

    while get_years < END_RACE_DATE[:4] or (get_years == END_RACE_DATE[:4] and get_month <= END_RACE_DATE[4:6]):
        # 開催月を取得
        hold_list = get_date(get_years, get_month)

        # 開始日以前の開催日の切り落とし
        if get_years == START_RACE_DATE[:4] or get_month == START_RACE_DATE[4:6]:
            hold_list.append(START_RACE_DATE)
            hold_list.sort()
            hold_list = hold_list[hold_list.index(START_RACE_DATE) + 1:]

        # 終了日以降の開催日の切り落とし
        if get_years == END_RACE_DATE[:4] or get_month == END_RACE_DATE[4:6]:
            hold_list.append(END_RACE_DATE)
            hold_list.sort()
            if hold_list.count(END_RACE_DATE) == 2:
                hold_list = hold_list[:hold_list.index(END_RACE_DATE) + 1]
            else:
                hold_list = hold_list[:hold_list.index(END_RACE_DATE)]
        
        # 開催日の各レース番号を取得
        race_list = get_race(hold_list)
        scrapring_race(race_list)
        exit()

def scraping_race(race_list):
    
    // TODO レース情報から特徴量をスクレイピング
    // TODO レース結果から正解ラベルをスクレイピング
    exit()

def get_race(hold_list):
    for hold_date in hold_list:
        cource_url = 'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date='\
                   + hold_date

        soup = Soup.get_soup(cource_url)
        links = soup.find_all('a')
        race_list = []
        for link in links:
            race_url = link.get('href')
            if 'result' in race_url:
                race_list.append(race_url[28:40])
        return race_list

def get_date(years, month):
    '''中央競馬の開催日を取得するメソッド

    Args:
        years(str):取得する対象の年。yyyy
        month(str):取得する対象の月。MM

    Return:
        hold_list(list):対象年月の開催日をlist型を返す。要素はyyyyMMdd形式。

    '''
    url = 'https://race.netkeiba.com/top/calendar.html?year='\
          + years\
          + '&month='\
          + month

    soup = Soup.get_soup(url)
    links = soup.find_all('a')
    hold_list = []
    for link in links:
        date_url = link.get('href')
        if 'kaisai_date' in date_url:
            hold_list.append(date_url[len(date_url) - 8:])
    return hold_list

def argv_check():
    # 引数の数チェック
    if len(sys.argv) != 3:
        raise ValueError('入力した引数の数が間違っています')
    
    # フォーマットチェック
    try:
        date_argv1 = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        date_argv2 = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')
    except:
        raise ValueError('入力した日付のフォーマットが間違っています')

    # 開始日 < 終了日チェック
    if date_argv1 > date_argv2:
        raise ValueError('終了日が開始日より前の日付になっています')
    else:
        return sys.argv[1], sys.argv[2]

if __name__ == '__main__':
    main()
