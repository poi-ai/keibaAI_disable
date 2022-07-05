import os
import requests

def send(message):
    """ LINEにメッセージを送信する
        同階層にLINE NoticeのAPIトークンコードが記載されている
        「line_token.txt」が必要

    Args:
        message(str) : LINE送信するメッセージ内容

    """
    filepath = os.path.dirname(__file__) + '\\line_token.txt'

    # トークンファイルが存在するなら
    if os.path.isfile(filepath):
        # トークンコード取得
        with open(filepath) as f:
            TOKEN = f.read()
        # ファイルが空なら何もしない
        if TOKEN == '':
            return
    else:
        # トークンファイルが存在しないなら何もしない
        return

    # トークンを設定
    headers = {'Authorization': f'Bearer {TOKEN}'}
    data = {'message': f'{message}'}

    # メッセージ送信
    requests.post('https://notify-api.line.me/api/notify', headers = headers, data = data)