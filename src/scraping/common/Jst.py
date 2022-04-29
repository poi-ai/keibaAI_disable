import datetime

class JST():
    def jst(self):
        return datetime.datetime.utcnow() + datetime.timedelta(hours=9)

    def date(self):
        '''
        Returns:
            JST(datetime)[YYYYmmdd]

        '''
        return self.jst().strftime("%Y%m%d")

    def time(self):
        '''
        Returns:
            JST(datetime)[YYYYmmddHHMMSS]

        '''
        return self.jst().strftime("%Y%m%d%H%M%S")

    def year(self):
        '''
        Returns:
            JSTの年(int)

        '''
        return self.jst().year

    def month(self):
        '''
        Returns:
            JSTの月(int)

        '''
        return self.jst().month

    def day(self):
        '''
        Returns:
            JSTの日(int)

        '''
        return self.jst().day

    def hour(self):
        '''
        Returns:
            JSTの時間(int)

        '''
        return self.jst().hour

    def minute(self):
        '''
        Returns:
            JSTの分(int)

        '''
        return self.jst().minute

    def second(self):
        '''
        Returns:
            JSTの秒(int)

        '''
        return self.jst().second