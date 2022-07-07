import jst
import os

def odds(df, kind):
    '''CSVにデータファイルを出力する

    Args:
        df(pandas.DataFrame) : 書き込むデータ
        kind(str) : 出力するオッズのタイプ。CSVファイル名の末尾に付ける
    '''

    # リポジトリのルートフォルダを指定
    repos_root = os.path.join(os.path.dirname(__file__), '../../../')
    data_folder = os.path.join(repos_root, 'data')
    csv_folder = os.path.join(data_folder, 'csv')
    csv_file = os.path.join(csv_folder, f'{jst.year()}{jst.month().zfill(2)}_{kind}odds.csv')

    # dataフォルダチェック。無ければ作成
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # CSVフォルダチェック。無ければ作成
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    # CSVチェック。なければカラム名付きで出力
    if not os.path.exists(csv_file):
        df.to_csv(csv_file, index = None)
    else:
        df.to_csv(csv_file, mode = 'a', header = None, index = None)