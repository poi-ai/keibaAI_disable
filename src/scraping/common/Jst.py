import datetime

class Jst():
    '''日本時間を取得するクラス'''

    def now(self):
        '''現在の時刻(JST)をdatetime型で返す'''
        return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

    def date(self):
        '''現在の日付(JST)をstr型[YYYYmmdd]で返す'''
        return self.now().strftime("%Y%m%d")

    def time(self):
        '''現在の時刻(JST)をstr型[YYYYmmddHHMMSS]で返す'''
        return self.now().strftime("%Y%m%d%H%M%S")

    def year(self):
        '''現在の年(JST)をstr型[YYYY]で返す'''
        return self.now().year

    def month(self):
        '''現在の月(JST)をstr型[m(0埋めなし)]で返す'''
        return self.now().month

    def day(self):
        '''現在の日(JST)をstr型[d(0埋めなし)]で返す'''
        return self.now().day

    def hour(self):
        '''現在の時間(JST)をstr型[H(0埋めなし)]で返す'''
        return self.now().hour

    def minute(self):
        '''現在の分(JST)をstr型[M(0埋めなし)]で返す'''
        return self.now().minute

    def second(self):
        '''現在の秒(JST)をstr型[S(0埋めなし)]で返す'''
        return self.now().second