import os
import sys
sys.path.append(os.path.join(sys.path[0], '..', 'common'))
sys.path.append(os.path.join(sys.path[0], '..'))
from common import babacodechange
import time
import re
import requests
from bs4 import BeautifulSoup

def error_search(association):
    '''過去データ取得オッズのログから取得失敗したレースについての詳細をCSVへ残す

       中央の場合は、同階層にjra.logで保存
       地方の場合は、同階層にnar.logで保存されたログファイルを対象とする
       いずれ自動化する

    '''

    with open(f'{association}.log', 'r', encoding='utf-8') as f:
        for line in f:
            # エラーが起こった場合の出力形式は統一してあるので、正規表現で抜き出し
            match = re.search(r'\(race_id:(\d+)\)の(.+)', line)

            if match:
                # レースID
                race_id = match.group(1)
                # エラー種別
                error_message = match.group(2)
                # 中止事由の枠を取得
                cause = get_discontinued_message(race_id, association)

                # 楽天でレース結果データが取得できるかレース中止か判断する
                if association == 'nar':
                    rakuten = rakuten_check(race_id)
                else:
                    rakuten = ''

                # clustering.csvをUTF-8で開く
                with open(f'{association}_error.csv', 'a', encoding='utf-8') as g:
                    # clustering.csvに「race_id,error_massage」という形で出力する
                    g.write(f'{race_id},{error_message},{cause},{rakuten}\n')

def rakuten_check(netkeiba_id):
    '''同レースの情報を楽天から取得してレース実施/中止の判定を行う'''

    # netkeiba独自のレースIDを楽天競馬独自のレースIDに変更
    rakuten_id = f'{netkeiba_id[:4]}{netkeiba_id[6:10]}{babacodechange.netkeiba_to_rakuten(netkeiba_id[4:6])}000000{netkeiba_id[10:]}'
    url = f'https://keiba.rakuten.co.jp/race_performance/list/RACEID/{rakuten_id}'

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')
    time.sleep(1)

    if 'ご指定の条件に該当するレースはありませんでした。' in str(soup):
        return 'レースページ未存在'

    if '取止' in str(soup):
        return 'レース中止'

    if '不成' in str(soup):
        return 'レース不成立'

    return 'レース実施'

def get_discontinued_message(race_id, association):
    '''netkeibaのページ内にレース中止事由が記載されていた場合は取得'''

    if association == 'jra':
        url = f'https://race.netkeiba.com/race/result.html?race_id={race_id}&rf=race_list'
    else:
        url = f'https://nar.netkeiba.com/race/result.html?race_id={race_id}&rf=race_list'

    time.sleep(1)

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    cause = soup.find('div', 'Race_Infomation_Box')
    if cause != None:
        return cause.text
    else:
        return ''

error_search('jra')
#error_search('nar')