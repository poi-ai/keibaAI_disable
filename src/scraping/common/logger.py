import inspect
import logging
import os
import sys
from pathlib import Path

class Logger():
    '''loggerの設定を簡略化
        ログファイル名は呼び出し元のファイル名
        出力はINFO以上のメッセージのみ

    Args:
        output(int):出力タイプを指定
                    0:ログ出力、1:標準出力、空:両方出力

    '''
    def __init__(self, output=None):
        self.logger = logging.getLogger()
        self.output = output
        self.set()

    def set(self):
        # フォーマットの設定
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')

        # 出力レベルの設定
        self.logger.setLevel(logging.INFO)

        # ログ出力設定
        if self.output != 0:
            # ログフォルダチェック。無ければ作成
            if not os.path.exists('../../log'):
                os.makedirs('../../log')
            # 出力先を設定
            handler = logging.FileHandler('../../log/' + Path(inspect.stack()[1].filename).stem +'.log')
            # 出力レベルを設定
            handler.setLevel(logging.INFO)
            # フォーマットの設定
            handler.setFormatter(formatter)
            # ハンドラの適用
            self.logger.addHandler(handler)

        # コンソール出力設定
        if self.output != 1:
            # ハンドラの設定
            handler = logging.StreamHandler(sys.stdout)
            # 出力レベルを設定
            handler.setLevel(logging.INFO)
            # フォーマットの設定
            handler.setFormatter(formatter)
            # ハンドラの適用
            self.logger.addHandler(handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

