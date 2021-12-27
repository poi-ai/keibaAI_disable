import csv
import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

def main():
    START_RACE_DATE, END_RACE_DATE = argv_check()
    get_years = START_RACE_DATE[:4]
    get_month = START_RACE_DATE[4:6]

    while True:
        hold_list = get_hold(get_years, get_month)


def get_hold(years, month):
    pass

    # hold_list = 

def argv_check():
    # 引数の数チェック
    if len(sys.argv) != 2:
        raise ValueError('入力した引数の数が間違っています')
    
    try:
        date_argv1 = datetime.datetime.strptime(sys.argv[0])
        date_argv2 = datetime.datetime.strptime(sys.argv[1])
    except:
        raise ValueError('入力した日付のフォーマットが間違っています')
    

    # 妥当性チェック
    if date_argv1 < date_argv2:
        raise ValueError('終了日が開始日より前の日付になっています')
    else:
        return sys.argv[0], sys.argv[1]

if __name__ == '__main__':
    main()