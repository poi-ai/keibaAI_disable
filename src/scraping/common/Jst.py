import datetime

class Jst():
    def now(self):
        '''
        Returns:
            JST(datetime)

        '''
        return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

    def date(self):
        '''
        Returns:
            JST(str)[YYYYmmdd]

        '''
        return self.now().strftime("%Y%m%d")

    def time(self):
        '''
        Returns:
            JST(str)[YYYYmmddHHMMSS]

        '''
        return self.now().strftime("%Y%m%d%H%M%S")

    def year(self):
        '''
        Returns:
            JSTの年(int)

        '''
        return self.now().year

    def month(self):
        '''
        Returns:
            JSTの月(int)

        '''
        return self.now().month

    def day(self):
        '''
        Returns:
            JSTの日(int)

        '''
        return self.now().day

    def hour(self):
        '''
        Returns:
            JSTの時間(int)

        '''
        return self.now().hour

    def minute(self):
        '''
        Returns:
            JSTの分(int)

        '''
        return self.now().minute

    def second(self):
        '''
        Returns:
            JSTの秒(int)

        '''
        return self.now().second