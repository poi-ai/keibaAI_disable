import inspect
import logging
import os
import sys
from pathlib import Path

class Logger():
    '''loggerの設定を簡略化したクラス
       Logger():ログと標準出力両方
       Logger(1):ログのみ
       Logger(0):標準出力のみ
    
    '''
    def __init__(self, output=None):
        self.logger = logging.getLogger()
        self.output = output
        self.set()

    def set(self):
        # フォーマットの設定
        formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
        
        # 出力レベルの設定、全部出るように
        self.logger.setLevel(logging.DEBUG)

        if self.output != 0:
            # ログフォルダチェック。無ければ作成
            if not os.path.exists('log'):
                os.makedirs('log')
            # 出力先を設定
            handler = logging.FileHandler('log/' + Path(inspect.stack()[1].filename).stem +'.log')
            # 出力レベルを設定
            handler.setLevel(logging.DEBUG)
            # フォーマットの設定
            handler.setFormatter(formatter)
            # ハンドラの適用
            self.logger.addHandler(handler)

        if self.output != 1:
            # ハンドラの設定
            handler = logging.StreamHandler(sys.stdout)
            # 出力レベルを設定
            handler.setLevel(logging.DEBUG)
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

