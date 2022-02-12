import gspread
import gspread_dataframe as gd
import pandas as pd
from google.oauth2.service_account import Credentials

def write_spread_sheet(df, month):
    '''スプレッドシートにデータを書き込む。
       実行にはGoogle DriveとスプレッドシートのAPIを
       使用できる資格情報を書いたkeibaAI.jsonと、
       スプレッドシートIDを記載したSheetID.csvが必要。

    Args:
        df(pandas.DataFrame):スプレッドシートに書き込むデータ
        month(int):レース年月をyyyymmのint型で書き込むシートを指定
        
    '''
    # スプレッドシートID保管CSVの取得 
    df_id = pd.read_csv('SheetID.csv')

    # スプレッドシートIDの設定。
    SPREADSHEET_KEY = df_id[df_id['month'] == month]['id'][0]

    # スコープの設定
    SCOPE = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

    # JSONファイルから資格情報の取得
    credentials = Credentials.from_service_account_file("keibaAI.json", scopes=SCOPE)
    gc = gspread.authorize(credentials)

    # スプレッドシート情報の取得
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('シート1')
    
    # 最終行の取得
    last_index = len(worksheet.col_values(1))

    # 最終行の次の行から書き込み
    gd.set_with_dataframe(worksheet, df, row = last_index + 1)