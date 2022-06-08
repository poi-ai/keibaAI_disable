import csv
import jst
import os
import pandas as pd

def write_csv(df,):
    '''CSVにデータファイルを出力する

    Args:
        df(pandas.DataFrame):書き込むデータ
    '''

    # dataフォルダチェック。無ければ作成
    if not os.path.exists('../../data'):
        os.makedirs('../../data')

    # CSVフォルダチェック。無ければ作成
    if not os.path.exists('../../data/csv'):
        os.makedirs('../../data/csv')

    # CSVチェック。なければカラム名付きで出力
    if not os.path.exists(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}.csv'):
        df.to_csv(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}.csv', index = None)
    else:
        df.to_csv(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}.csv', mode = 'a', header = None, index = None)
