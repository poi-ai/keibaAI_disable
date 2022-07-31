import logger as lg
import pandas as pd
import time
import traceback

# エラー回避用ログインスタンス作成
logger = lg.Logger()

def html(URL, sleep_time = 0, retry_count = 3):
    '''テーブル取得のリトライ処理

         Args:
             URL(str):取得対象のURL
             sleep_time(int):リトライまでのアイドルタイム
             retry_count(int):最大リトライ回数

         Returns:
             table(pandas.DataFrame):取得したHTML情報
    '''

    for _ in range(retry_count):
        try:
            table = pd.read_html(URL)
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            if sleep_time != 0:
                time.sleep(sleep_time)
        else:
            return table
    else:
        return -1