import jrarecordodds
import narrecordodds
import package
import traceback
from common import logger as lg, jst

if __name__ == '__main__':

    # ログ用インスタンス作成
    logger = lg.Logger()

    # 中央競馬用インスタンス作成
    try:
        jra = jrarecordodds.Jra()
    except Exception as e:
        logger.error('中央_初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        exit()

    # 地方競馬用インスタンス作成
    try:
        nar = narrecordodds.Nar()
    except Exception as e:
        logger.error('地方_初期処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        exit()

    # 全レース記録済かチェック
    while jra.end_check() or nar.end_check():
        while True:
            try:
                # 中央発走時刻更新
                jra.get_race_info()
            except Exception as e:
                logger.error('中央_発走時刻更新処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

            try:
                # 地方発走時刻更新
                nar.get_race_info()
            except Exception as e:
                logger.error('地方_発走時刻更新処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

            try:
                # 中央の発走までの時間チェック待機
                if jra.time_check():
                    break
            except Exception as e:
                logger.error('中央_待機時間チェック処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

            try:
                # 地方の発走までの時間チェック待機
                if nar.time_check():
                    break
            except Exception as e:
                logger.error('地方_時刻までの待機時間チェック処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

        try:
            # オッズ取得処理
            jra.get_select()
        except Exception as e:
            logger.error('中央_オッズ取得処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

        try:
            # オッズ取得処理
            nar.get_select()
        except Exception as e:
            logger.error('地方_オッズ取得処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

        # 記録データが格納されていてx分40秒を過ぎていなければCSV出力
        if int(jst.second()) <= 40 and len(jra.write_data) != 0:

            try:
                jra.record_odds()
            except Exception as e:
                logger.error('中央_オッズ出力処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

            try:
                nar.record_odds()
            except Exception as e:
                logger.error('地方_オッズ出力処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()