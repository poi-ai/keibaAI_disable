import requests

def send(message):
    """ LINEにメッセージを送信する
        同階層にLINE NoticeのAPIトークンコードが記載されている
        「line_token.txt」が必要
    
    Args:
        message(str):LINE送信するメッセージ内容

    """
    # トークンコード取得
    with open('./line_token.txt') as f:
        TOKEN = f.read()
    
    # トークンを設定
    headers = {'Authorization': f'Bearer { TOKEN }'}

    # メッセージ送信
    requests.post('https://notify-api.line.me/api/notify', headers = headers, data = message)
