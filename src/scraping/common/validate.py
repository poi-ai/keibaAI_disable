import datetime
import logger as lg
from common import jst

# エラー回避用ログインスタンス作成
logger = lg.Logger()

def check(possible_oldest_date, oldest_date, latest_date):
    '''日付の妥当性チェックを行う

    Args:
        possible_oldest_date(str):取得可能な最古の日付(yyyyMMdd)
        oldest_date(str):取得しようとしている最古の日付(yyyyMMdd)
        latest_date(str):取得しようとしている最新の日付(yyyyMMdd)

    Return:
        oldest_date(str):指定した日付の中で取得可能な最古の日付(yyyyMMdd)
        latest_date(str):指定した日付の中で取得可能な最新の日付(yyyyMMdd)
    '''

    logger.info('日付のバリデーションチェック開始')

    slash_possible_oldest_date = jst.change_format(possible_oldest_date, "%Y%m%d", "%Y/%m/%d")

    # 日付フォーマットチェック
    try:
        tmp = datetime.strptime(oldest_date, '%Y%m%d')
    except:
        logger.warning('取得対象最古日の値が不正です')
        logger.warning(f'取得対象最古日:{oldest_date}→{slash_possible_oldest_date} に変更します')
        oldest_date = possible_oldest_date

    try:
        tmp = datetime.strptime(latest_date, '%Y%m%d')
    except:
        logger.warning('取得対象最新日の値が不正です')
        logger.warning(f'取得対象最新日:{latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
        latest_date = jst.yesterday()

    # 日付妥当性チェック
    if oldest_date < possible_oldest_date:
        logger.warning(f'取得対象最古日の値が{slash_possible_oldest_date}より前になっています')
        logger.warning(f'{slash_possible_oldest_date}以前のオッズデータはnetkeibaサイト内に存在しないため取得できません')
        logger.warning(f'取得対象最古日:{oldest_date}→{slash_possible_oldest_date}に変更します')
        oldest_date = jst.yesterday()
    elif oldest_date == jst.date():
        logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
        logger.warning(f'取得対象最古日:{oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
        oldest_date = jst.yesterday()
    elif oldest_date > jst.date():
        logger.warning('取得対象最古日の値が未来になっています')
        logger.warning(f'取得対象最古日:{oldest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
        oldest_date = jst.yesterday()

    if latest_date == jst.date():
        logger.warning('エラーを起こす可能性が高いため本日のレースは取得できません')
        logger.warning(f'取得対象最新日:{latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
        latest_date = jst.yesterday()
    elif latest_date > jst.date():
        logger.warning('取得対象最新日の値が未来になっています')
        logger.warning(f'取得対象最新日:{latest_date}→{jst.change_format(jst.yesterday(), "%Y%m%d", "%Y/%m/%d")}に変更します')
        latest_date = jst.yesterday()

    if latest_date < oldest_date:
        logger.warning('取得対象最古日と最新日の記載順が逆のため入れ替えて処理を行います')
        tmp = latest_date
        latest_date = oldest_date
        oldest_date = tmp

    logger.info(f'取得対象最古日:{jst.change_format(oldest_date, "%Y%m%d", "%Y/%m/%d")}')
    logger.info(f'取得対象最新日:{jst.change_format(latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')
    print(f'取得対象最古日:{jst.change_format(oldest_date, "%Y%m%d", "%Y/%m/%d")}')
    print(f'取得対象最新日:{jst.change_format(latest_date, "%Y%m%d", "%Y/%m/%d")} で処理を行います')

    return oldest_date, latest_date
