import itertools
import csv
import datetime
import pandas as pd
import re
import sys
import time
import tqdm
from common import Soup, WordChange as wc

def main():
    # 引数の妥当性チェック
    START_RACE_DATE, END_RACE_DATE = argv_check()

    # 開始日の年と月を抽出
    years = START_RACE_DATE[:4]
    month = START_RACE_DATE[4:6]

    print('レースIDを取得します。\n')
    # レースIDを格納するリスト
    race_id_list = []

    for _ in tqdm.tqdm(range((int(END_RACE_DATE[:4]) - int(years)) * 12  + int(END_RACE_DATE[4:6]) - int(month) + 1 )):
        # 開催月を取得
        hold_list = get_date(years, month)

        # 開始日以前の開催日の切り落とし
        if years == START_RACE_DATE[:4] or month == START_RACE_DATE[4:6]:
            hold_list.append(START_RACE_DATE)
            hold_list.sort()
            hold_list = hold_list[hold_list.index(START_RACE_DATE) + 1:]

        # 終了日以降の開催日の切り落とし
        if years == END_RACE_DATE[:4] or month == END_RACE_DATE[4:6]:
            hold_list.append(END_RACE_DATE)
            hold_list.sort()
            if hold_list.count(END_RACE_DATE) == 2:
                hold_list = hold_list[:hold_list.index(END_RACE_DATE) + 1]
            else:
                hold_list = hold_list[:hold_list.index(END_RACE_DATE)]
        
        # 開催日の各レース番号を取得
        race_id_list.append(get_race(hold_list))

        # 翌月へ
        if month == '12':
            years = str(int(years) + 1)
            month = '1'
        else:
            month = str(int(month) + 1)
    
    # 一元化
    race_id_list = list(itertools.chain.from_iterable(race_id_list))

    print('\n取得対象のレース数は' + str(len(race_id_list)) + 'です。\nレースデータの取得を開始します。')

    for race_id in tqdm.tqdm(race_id_list):
        scraping_race(race_id)

    exit()

def get_info(soup):
    '''HTMLデータから共通で使えるレース情報を抽出

    Args:
        soup(bs4.BeautifulSoup): レース情報全てを含むHTMLデータ

    Returns:
        race_info(list[str]): レース情報を持つリスト
    
    '''
    race_info = []
    states_info = Soup.del_tag(soup.find('div', class_='RaceData01')).split('/')
    del_letter = r'[\n発走天候馬場(): ]'

    # 発走時刻
    race_info.append(states_info[0][1:6])
    # 馬場情報切り出し
    baba_info = re.sub(del_letter, '', states_info[1])
    # ダート or 芝
    race_info.append(baba_info[0])
    # 距離と周りを分けるための要素番号
    border = baba_info.find('m')
    # 距離
    race_info.append(baba_info[1:border])
    # 回り(内回り、外回り、右回り、左回り、直線)
    if len(baba_info[border+1:]) == 1:
        race_info.append([baba_info[border+1:], ''])
    else:
        race_info.append(list(baba_info[border+1:], ''))
    # 天候
    race_info.append(re.sub(del_letter, '', states_info[2]))
    # 馬場状態
    race_info.append(re.sub(del_letter, '', states_info[3]))
    
    # リストの1次元化
    # race_info = list(itertools.chain.from_iterable(race_info))
    #print(race_info)

    race_kind = Soup.del_tag(soup.find('div', class_='RaceData02')).split()
    del_letter = r'[回日目頭本賞金:万円 ]'
    # 開催回
    race_info.append(re.sub(del_letter, '', race_kind[0]))
    # 競馬場
    race_info.append(race_kind[1])
    # 開催o日目
    race_info.append(re.sub(del_letter, '', race_kind[2]))
    # 出走条件
    race_info.append(wc.full_to_half(race_kind[3]))
    # グレード
    race_info.append(wc.full_to_half(race_kind[4]))
    
    if len(race_kind) == 8:
        pass
    elif len(race_kind) == 9:
        pass
    else:
        raise ValueError('レース情報の取得に失敗')
    print(race_info)
    exit()
    return []
    

def scraping_race(race_id):
    '''レース番号からレース情報・結果をスクレイピング

    Args:
        race_id(str):レース番号。10桁(西暦+開催回+開催日+競馬場コード)

    Returns:
        df(pandas.DataFrame):レース情報と各馬の情報・結果をもったデータ
    
    '''
    # レース結果のURLからHTMLデータをスクレイピング
    result_url = 'https://db.netkeiba.com/race/' + race_id

    df = pd.read_html(result_url)[0]
    
    soup = Soup.get_soup(result_url)

    # TODO データ加工

    # return df

def get_race(hold_list):
    '''対象年月日のレース番号を取得

    Args:
        hold_list(list):中央開催日の年月日(yyyyMMdd)を要素に持つリスト

    Returns:
        race_id_list(list):対象年月日のレースIDを要素に持つリスト
        
    '''
    # 各開催日からレースIDをリストに代入
    race_id_list = []
    for hold_date in hold_list:
        cource_url = 'https://race.netkeiba.com/top/race_list_sub.html?kaisai_date='\
                   + hold_date

        soup = Soup.get_soup(cource_url)
        links = soup.find_all('a')

        for link in links:
            race_url = link.get('href')
            if 'result' in race_url:
                race_id_list.append(race_url[28:40])

    return race_id_list

def get_date(years, month):
    '''中央競馬の開催日を取得

    Args:
        years(str):取得する対象の年。yyyy
        month(str):取得する対象の月。MM

    Return:
        hold_list(list):対象年月の開催日。要素はyyyyMMdd形式のstr型。

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
    '''スクレイピングの開始日と終了日をチェック

    Return:
       sys.args[1](str):スクレイピング対象の最初の日。yyyyMMdd形式
       sys.args[2](str):スクレイピング対象の最後の日。yyyyMMdd形式

    '''
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
