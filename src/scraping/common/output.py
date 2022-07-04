import jst
import os

def odds(df, kind):
    '''CSVにデータファイルを出力する

    Args:
        df(pandas.DataFrame) : 書き込むデータ
        kind(str) : 出力するオッズのタイプ。CSV名に付ける
    '''

    # dataフォルダチェック。無ければ作成
    if not os.path.exists('../../data'):
        os.makedirs('../../data')

    # CSVフォルダチェック。無ければ作成
    if not os.path.exists('../../data/csv'):
        os.makedirs('../../data/csv')

    # CSVチェック。なければカラム名付きで出力
    if not os.path.exists(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}_{kind}odds.csv'):
        df.to_csv(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}_{kind}odds.csv', index = None)
    else:
        df.to_csv(f'../../data/csv/{jst.year()}{jst.month().zfill(2)}_{kind}odds.csv', mode = 'a', header = None, index = None)
