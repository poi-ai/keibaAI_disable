import jrarecordodds
import narrecordodds
import package
import time
import traceback
from common import logger, jst

def main():
    '''主処理'''
    while True:
        # 全レース記録済みかのチェック
        jra_flg, nar_flg = end_check()

        # 中央・地方ともに記録済みなら処理終了
        if not (jra_flg or nar_flg):
            exit()

        while True:
            # 発走時刻更新処理
            get_race_info()

            # 時間チェック/待機処理
            if time_check():
                break

        # オッズ取得処理
        get_select()


def create_instance():
    '''インスタンスの生成を行う'''

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

    return jra, nar

def end_check():
    '''レースが記録済みかのチェックを行う'''
    jra_end_flg = False
    nar_end_flg = False

    try:
        # 中央が全レース記録済かチェック
        if not jra.end_check():
            jra_end_flg = True
    except Exception as e:
        logger.error('中央_発走時刻更新処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        exit()

    try:
        # 地方が全レース記録済かチェック
        if not nar.end_check():
            nar_end_flg = True
    except Exception as e:
        logger.error('地方_発走時刻更新処理でエラー')
        logger.error(e)
        logger.error(traceback.format_exc())
        exit()

    return jra_end_flg, nar_end_flg

def get_race_info():
    '''発走時刻に変更があった場合に更新を行う'''
    if jra_flg:
        try:
            # 中央発走時刻更新
            jra.get_race_info()
        except Exception as e:
            logger.error('中央_発走時刻更新処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

    if nar_flg:
        try:
            # 地方発走時刻更新
            nar.get_race_info()
        except Exception as e:
            logger.error('地方_発走時刻更新処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

def time_check():
    '''記録時間までの時間を取得し、待機する'''
    jra_wait_time = 99999999
    nar_wait_time = 99999999

    if jra_flg:
        try:
            # 中央の発走までの時間チェック
            jra_wait_time =  jra.time_check(True)
            logger.info(f'中央：次の記録時間まで{jra_wait_time}秒')
        except Exception as e:
            logger.error('中央_待機時間チェック処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()
    else:
        logger.info(f'中央の取得対象レースはありません')

    if nar_flg:
        try:
            # 地方の発走までの時間チェック
            nar_wait_time = nar.time_check(True)
            logger.info(f'地方：次の記録時間まで{nar_wait_time}秒')
        except Exception as e:
            logger.error('地方_時刻までの待機時間チェック処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()
    else:
        logger.info(f'地方の取得対象レースはありません')

    # より近い方の待機時間に合わせる
    time_left = min(jra_wait_time, nar_wait_time)

    # どちらも更新されなかった場合(リカバリ処理)
    if time_left == 99999999:
        logger.warning('取得処理がどこかおかしいかも')
        logger.warning('とりあえず10分待機します')
        time_left = 661

    logger.info(f'次の記録時間まで{time_left}秒')

    # 11分以上なら10分後に発走時刻再チェック
    if time_left > 660:
        time.sleep(600)
        return False
    elif time_left > 1:
        time.sleep(time_left + 1)
        return True
    else:
        return True

def get_select():
    '''取得対象レースを抽出し、オッズ取得を行う'''
    if jra_flg:
        try:
            # オッズ取得処理
            jra.get_select()
        except Exception as e:
            logger.error('中央_オッズ取得処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

    if nar_flg:
        try:
            # オッズ取得処理
            nar.get_select()
        except Exception as e:
            logger.error('地方_オッズ取得処理でエラー')
            logger.error(e)
            logger.error(traceback.format_exc())
            exit()

def record_check():
    '''取得したオッズデータをCSVに書き出す'''
    # 記録データが格納されていてx分40秒を過ぎていなければCSV出力
    if int(jst.second()) <= 40 and len(jra.write_data) != 0:
        if jra_flg:
            try:
                jra.record_odds()
            except Exception as e:
                logger.error('中央_オッズ出力処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

        if nar_flg:
            try:
                nar.record_odds()
            except Exception as e:
                logger.error('地方_オッズ出力処理でエラー')
                logger.error(e)
                logger.error(traceback.format_exc())
                exit()

if __name__ == '__main__':

    # ログ用インスタンス作成
    logger = logger.Logger()

    # 中央・地方のインスタンスを作成する
    jra, nar = create_instance()

    # 中央・地方の取得処理継続フラグ(全レース記録済みでないか)を作成
    jra_flg, nar_flg = True

    # 主処理実行
    main()