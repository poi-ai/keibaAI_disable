import datetime

'''日本時間を取得'''
def now():
    '''現在の時刻(JST)をdatetime型で返す'''
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

def date():
    '''現在の日付(JST)をstr型[YYYYmmdd]で返す'''
    return now().strftime("%Y%m%d")

def time():
    '''現在の時刻(JST)をstr型[YYYYmmddHHMMSS]で返す'''
    return now().strftime("%Y%m%d%H%M%S")

def year():
    '''現在の年(JST)をstr型[YYYY]で返す'''
    return str(now().year)

def month():
    '''現在の月(JST)をstr型[m(0埋めなし)]で返す'''
    return str(now().month)

def day():
    '''現在の日(JST)をstr型[d(0埋めなし)]で返す'''
    return str(now().day)

def hour():
    '''現在の時間(JST)をstr型[H(0埋めなし)]で返す'''
    return str(now().hour)

def minute():
    '''現在の分(JST)をstr型[M(0埋めなし)]で返す'''
    return str(now().minute)

def second():
    '''現在の秒(JST)をstr型[S(0埋めなし)]で返す'''
    return str(now().second)

# TODO ここでいいかは要検討
def time_min(time1, time2):
    '''datetime型の値を比較し、古い(小さい)方をdatetime型で返す'''
    return datetime.datetime.strptime(min(time1.strftime("%Y%m%d%H%M%S"), time2.strftime("%Y%m%d%H%M%S")), "%Y%m%d%H%M%S")