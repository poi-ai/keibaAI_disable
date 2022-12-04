import package
import pandas as pd
import re
import traceback
from common import soup as Soup, output, wordchange, logger as lg, line, babacodechange

class GetRaceData():
    '''netkeibaのサイトから地方競馬の過去レースデータを取得する

    Instance Parameter:
        race_id(str) : 取得対象レースのnetkeiba独自ID
        baba_id(str) : レースが行われる競馬場のnetkeiba独自ID
        race_date(str) : レース開催日(yyyyMMdd型)
        race_no(str) : レース番号(0埋め2桁)
        race_info(RaceInfo) : 発走前のレースデータ
        horse_race_info_dict(dict{horse_no(str): HorseRaceInfo, ...}) : 各馬のレースのデータ
        horse_char_info_dict(dict{horse_no(str): HorseCharInfo, ...}) : 各馬固有のデータ
        race_progress_info(RaceProgressInfo): レース全体のデータ
        horse_result_dict(dict{horse_no(str): HorseResult, ...}) : 各馬のレース結果データ
        output_type(str) : 出力ファイルを分割
                           m : 月ごと(デフォルト)、y : 年ごと、a : 全ファイルまとめて
    '''

    #DB_RESULT_URL = 'https://db.netkeiba.com/race/' + RACE_ID

    def __init__(self, race_id, output_type = 'm'):
        self.logger = lg.Logger(0)
        self.race_info = RaceInfo()
        self.horse_race_info_dict = {}
        self.horse_char_info_dict = {}
        self.race_progress_info = RaceProgressInfo()
        self.horse_result_dict = {}
        self.race_id = self.race_info.race_id = self.race_progress_info.race_id = race_id
        self.baba_id = self.race_info.baba_id = race_id[4:6]
        self.race_date = self.race_info.race_date = race_id[:4] + race_id[6:10]
        self.race_no = self.race_info.race_no = race_id[10:]
        self.output_type = output_type
        self.race_flg = True

    # getter
    @property
    def race_id(self): return self.__race_id
    @property
    def baba_id(self): return self.__baba_id
    @property
    def race_date(self): return self.__race_date
    @property
    def race_no(self): return self.__race_no
    @property
    def race_info(self): return self.__race_info
    @property
    def horse_race_info_dict(self): return self.__horse_race_info_dict
    @property
    def horse_char_info_dict(self): return self.__horse_char_info_dict
    @property
    def race_progress_info(self): return self.__race_progress_info
    @property
    def horse_result_dict(self): return self.__horse_result_dict
    @property
    def output_type(self): return self.__output_type

    # setter
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @baba_id.setter
    def baba_id(self, baba_id): self.__baba_id = baba_id
    @race_date.setter
    def race_date(self, race_date): self.__race_date = race_date
    @race_no.setter
    def race_no(self, race_no): self.__race_no = race_no
    @race_info.setter
    def race_info(self, race_info): self.__race_info = race_info
    @horse_race_info_dict.setter
    def horse_race_info_dict(self, horse_race_info_dict): self.__horse_race_info_dict = horse_race_info_dict
    @horse_char_info_dict.setter
    def horse_char_info_dict(self, horse_char_info_dict): self.__horse_char_info_dict = horse_char_info_dict
    @race_progress_info.setter
    def race_progress_info(self, race_progress_info): self.__race_progress_info = race_progress_info
    @horse_result_dict.setter
    def horse_result_dict(self, horse_result_dict): self.__horse_result_dict = horse_result_dict
    @output_type.setter
    def output_type(self, output_type): self.__output_type = output_type

    '''
    TODO
    * レース前に実際に取れるのは馬柱のみなので、レース情報などは馬柱から取得する
    * 騎手減量がリアルタイム レース結果からしか取得できないので要検討
    '''
    def main(self):

        # ばんえいとそれ以外で取得ロジックを変える
        if self.baba_id == '65':
            # TODO 後で消す
            return

            # 馬柱からデータ取得
            try:
                self.get_bannei_umabashira()
            except Exception as e:
                self.error_output(f'ばんえい{self.race_no}R(race_id:{self.race_id})の馬柱取得処理でエラー', e, traceback.format_exc())
                return

            # レース結果からデータ取得
            try:
                self.get_bannei_result()
            except Exception as e:
                self.error_output(f'ばんえい{self.race_no}R(race_id:{self.race_id})のレース結果取得処理でエラー', e, traceback.format_exc())
                return
        else:
            # 馬柱からデータ取得
            try:
                self.get_umabashira()
            except Exception as e:
                self.error_output(f'{babacodechange.netkeiba(self.baba_id)}{self.race_no}R(race_id:{self.race_id})の馬柱取得処理でエラー', e, traceback.format_exc())
                return

            # レース中止フラグチェック
            if not self.race_flg:
                return

            # レース結果からデータ取得
            try:
                self.get_result()
            except Exception as e:
                self.error_output(f'{babacodechange.netkeiba(self.baba_id)}{self.race_no}R(race_id:{self.race_id})のレース結果取得処理でエラー', e, traceback.format_exc())
                return

            # レース中止フラグチェック
            if not self.race_flg:
                return

        # TODO 楽天から残りの要素取得

        # インスタンス変数確認用
        #for index in self.horse_race_info_dict:
        #    horse_race_info = vars(self.horse_race_info_dict[index])
        #    df = pd.DataFrame.from_dict(horse_race_info, orient='index').T
        #    output.csv(df, 'horse_race_info')
        #for index in horse_result_dict:
        #    horse_result = vars(horse_result_dict[index])
        #    df = pd.DataFrame.from_dict(horse_result, orient='index').T
        #    output.csv(df, 'horse_result')

        # 取得したデータをCSV出力
        try:
            self.output_csv()
        except Exception as e:
            self.error_output(f'{babacodechange.netkeiba(self.baba_id)}{self.race_no}R(race_id:{self.race_id})のCSV出力処理でエラー', e, traceback.format_exc())
            return

    def get_umabashira(self):
        '''馬柱から発走前のデータを取得する'''
        soup = Soup.get_soup('https://nar.netkeiba.com/race/shutuba_past.html?race_id=' + self.race_id)

        # コース情報や馬場状態の枠
        race_data_01 = soup.find('div', class_ = 'RaceData01')
        race_data_list = wordchange.rm(race_data_01.text).split('/')

        # 発走時刻取得
        self.race_info.race_time = race_data_list[0].replace('発走', '')

        # 馬場(芝/ダ)、馬場状態
        course = re.search('([芝|ダ])(\d+)m\((.*)\)', race_data_list[1])
        baba = course.groups()[0]

        # 当日公表データが少ない(=レース中止)の場合弾く
        if len(race_data_list) < 4:
            self.logger.info(f'{babacodechange.netkeiba(self.baba_id)}{self.race_no}R(race_id:{self.race_id})のレースデータが不足しているため記録を行いません')
            self.race_flg = False
            return

        self.race_info.baba = baba
        if baba == '芝':
            self.race_info.glass_condition = race_data_list[3].replace('馬場:', '')
        elif baba == 'ダ':
            self.race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

        # 距離
        self.race_info.distance = course.groups()[1]

        # 回り(右/左)
        self.race_info.around = course.groups()[2]

        # 天候
        self.race_info.weather = race_data_list[2].replace('天候:', '')

        # 出走条件等の枠
        race_data_02 = soup.find('div', class_ = 'RaceData02')

        # 開催回/日
        race_data_list = race_data_02.text.split('\n')
        self.race_info.hold_no = race_data_list[1].replace('回', '')
        self.race_info.hold_date = race_data_list[3].replace('日目', '')

        # 出走条件(馬齢/クラス)
        require_split = race_data_list[4].find(' ')
        self.race_info.require_age = wordchange.full_to_half(race_data_list[4][:require_split]).replace('サラ系', '')
        self.race_info.race_class = wordchange.full_to_half(race_data_list[4][require_split + 1:])

        # レース名
        race_name = soup.find('div', class_ = 'RaceName')
        self.race_info.race_name = race_name.text.replace('\n', '')

        # CSSからグレードチェック、13はWIN5
        if 'Icon_GradeType1"' in str(race_name):
            self.race_info.grade = 'GI'
        elif 'Icon_GradeType2' in str(race_name):
            self.race_info.grade = 'GII'
        elif 'Icon_GradeType3' in str(race_name):
            self.race_info.grade = 'GIII'
        elif 'Icon_GradeType4' in str(race_name):
            self.race_info.grade = '重賞'
        elif 'Icon_GradeType5' in str(race_name):
            self.race_info.grade = 'OP'
        elif 'Icon_GradeType6' in str(race_name):
            self.race_info.grade = '1600万下'
        elif 'Icon_GradeType7' in str(race_name):
            self.race_info.grade = '1000万下'
        elif 'Icon_GradeType8' in str(race_name):
            self.race_info.grade = '900万下'
        elif 'Icon_GradeType9' in str(race_name):
            self.race_info.grade = '500万下'
        elif 'Icon_GradeType10' in str(race_name):
           self.race_info.grade = 'JGI'
        elif 'Icon_GradeType11' in str(race_name):
            self.race_info.grade = 'JGII'
        elif 'Icon_GradeType12' in str(race_name):
            self.race_info.grade = 'JGIII'
        elif 'Icon_GradeType15' in str(race_name):
            self.race_info.grade = 'L'
        elif 'Icon_GradeType16' in str(race_name):
            self.race_info.grade = '3勝'
        elif 'Icon_GradeType17' in str(race_name):
            self.race_info.grade = '2勝'
        elif 'Icon_GradeType18' in str(race_name):
            self.race_info.grade = '1勝'

        # TODO 待選とは何かわからないが、暫定処理としてグレードの末尾に付けておく
        if 'Icon_GradeType14' in str(race_name):
            self.race_info.grade += '待選'

        self.race_info.horse_num = race_data_list[6].replace('頭', '')

        # レース賞金
        prize = re.search('本賞金:(.+)、(.+)、(.+)、(.+)、(.+)万円', race_data_list[8])
        self.race_info.first_prize = prize.groups()[0]
        self.race_info.second_prize = prize.groups()[1]
        self.race_info.third_prize = prize.groups()[2]
        self.race_info.fourth_prize = prize.groups()[3]
        self.race_info.fifth_prize = prize.groups()[4]

        fc = soup.select('dl[class="fc"]')
        for i, info in enumerate(fc):
            # 本レースでの馬情報格納用(馬体重、馬齢...)
            horse_race_info = HorseRaceInfo()
            # 不変の馬情報格納用(馬名、父・母名...)
            horse_char_info = HorseCharInfo()

            # レースID追加
            horse_race_info.race_id = self.race_id

            # 所属や馬名の書いてる枠
            horse_type = info.find('dt', class_ = 'Horse02')

            # 外国産(所属)馬/地方所属馬判定
            if 'Icon_MaruChi' in str(horse_type):
                horse_race_info.belong = 'マル地'
            elif 'Icon_kakuChi' in str(horse_type):
                horse_race_info.belong = 'カク地'
            elif 'Icon_MaruGai' in str(horse_type):
                horse_race_info.country = 'マル外'
            elif 'Icon_KakuGai' in str(horse_type):
                horse_race_info.country = 'カク外'

            # ブリンカー有無
            if '<span class="Mark">B</span>' in str(horse_type):
                horse_race_info.blinker = '1'

            # netkeiba独自の馬ID
            m = re.search('db.netkeiba.com/horse/(\d+)/"', str(horse_type))
            if m != None:
                horse_race_info.horse_id = m.groups()[0]
                horse_char_info.horse_id = m.groups()[0]

            # 馬名
            horse_char_info.horse_name = horse_type.text.replace('\n', '')

            # 父名・母名・母父名
            horse_char_info.father = info.find('dt', class_ = 'Horse01').text
            horse_char_info.mother = info.find('dt', class_ = 'Horse03').text
            horse_char_info.grandfather = info.find('dt', class_ = 'Horse04').text.replace('(', '').replace(')', '')

            # 調教師・調教師所属
            trainer = info.find('dt', class_ = 'Horse05').text.split('・')
            horse_race_info.trainer_belong = trainer[0]
            horse_race_info.trainer = wordchange.rm(trainer[1])

            # netkeiba独自の調教師ID
            trainer_id = re.search('db.netkeiba.com/trainer/(\d+)/', str(info))
            if trainer_id != None:
                horse_race_info.trainer_id = trainer_id.groups()[0]

            # 出走間隔(週)
            blank = info.find('dt', class_ = 'Horse06').text
            if blank == '連闘':
                horse_race_info.blank = '0'
            else:
                blank_week = re.search('中(\d+)週', blank)
                # 初出走判定
                if blank_week == None:
                    horse_race_info.blank = '-1'
                else:
                    horse_race_info.blank = blank_week.groups()[0]

            # 脚質(netkeiba独自)
            running_type = str(info.find('dt', class_ = 'Horse06'))
            if 'horse_race_type00' in running_type:
                horse_race_info.running_type = '未'
            elif 'horse_race_type01' in running_type:
                horse_race_info.running_type = '逃'
            elif 'horse_race_type02' in running_type:
                horse_race_info.running_type = '先'
            elif 'horse_race_type03' in running_type:
                horse_race_info.running_type = '差'
            elif 'horse_race_type04' in running_type:
                horse_race_info.running_type = '追'
            elif 'horse_race_type05' in running_type:
                horse_race_info.running_type = '自在'

            # 馬体重
            weight = re.search('(\d+)kg\((.+)\)', info.find('dt', class_ = 'Horse07').text)
            # TODO 計不対応
            if weight != None:
                horse_race_info.weight = weight.groups()[0]
                horse_race_info.weight_change = str(int(weight.groups()[1]))

            # 単勝オッズ
            odds = re.search('(\d+\.\d)\((.+)人気\)', wordchange.rm(info.find('dt', class_ = 'Horse07').text))
            # TODO 取消馬対応
            if odds != None:
                horse_race_info.popular = odds.groups()[0]
                horse_race_info.win_odds = odds.groups()[1]

            # 馬番・枠番
            horse_race_info.horse_no = str(i + 1)
            horse_race_info.frame_no = self.frame_no_culc(self.race_info.horse_num, int(i + 1))

            self.horse_race_info_dict[str(i + 1)] = horse_race_info
            self.horse_char_info_dict[str(i + 1)] = horse_char_info

        # 騎手等記載の隣の枠から情報取得
        jockeys = soup.find_all('td', class_ = 'Jockey')
        for i, info in enumerate(jockeys):
            horse_race_info = self.horse_race_info_dict[str(i + 1)]
            horse_char_info = self.horse_char_info_dict[str(i + 1)]

            # 性別・馬齢・毛色
            m = re.search('([牡|牝|セ])(\d+)(.+)', info.find('span', class_ = 'Barei').text)
            if m != None:
                horse_race_info.gender = m.groups()[0]
                horse_race_info.age = m.groups()[1]
                horse_char_info.hair_color = m.groups()[2]

            # 騎手名・netkeiba独自の騎手ID
            # TODO 騎手ID未存在時、騎手名だけ
            jockey = re.search('db.netkeiba.com/jockey/(\d+)/">(.+)</a>', str(info))
            if jockey != None:
                horse_race_info.jockey_id = jockey.groups()[0]
                horse_race_info.jockey = jockey.groups()[1]

            # 斤量
            load = re.search('<span>(\d+\d.\d+)</span>', str(info))
            if load != None:
                horse_race_info.load = load.groups()[0]

            self.horse_race_info_dict[str(i + 1)] = horse_race_info
            self.horse_char_info_dict[str(i + 1)] = horse_char_info

    def get_bannei_umabashira(self):
        pass

    def get_result(self):
        '''レース結果ページからレース結果を抽出する'''

        url = 'https://nar.netkeiba.com/race/result.html?race_id=' + self.race_id

        # TODO owner, pass_rank, prizeが取れない
        # レース結果(HTML全体)
        soup = Soup.get_soup(url)

        # read_htmlで抜けなくなる余分なタグを除去後に結果テーブル抽出
        tables = pd.read_html(str(soup).replace('<diary_snap_cut>', '').replace('</diary_snap_cut>', ''))

        # 結果ページのテーブル数が少ない場合はレースが行われていないとみなし、出力を行わない
        if len(tables) <= 2:
            self.logger.info(f'{babacodechange.netkeiba(self.baba_id)}{self.race_no}R(race_id:{self.race_id})のレース結果ページのデータが不足しているため記録を行いません')
            self.logger.info(f'取得先URL:{url}')
            self.race_flg = False
            return

        # レース結果のテーブル
        table = tables[0]

        # 1着馬の馬番
        winner_horse_no = 0

        # 列ごとに切り出し
        # TODO 除外・取消馬の処理
        for i, index in enumerate(table.index):
            horse_result = HorseResult()

            # レースID追加
            horse_result.race_id = self.race_id

            # 結果テーブルの列取得
            row = table.loc[index]

            # レース結果の各項目を設定
            horse_result.horse_no = row['馬番']
            horse_result.rank = row['着順']
            horse_result.goal_time = row['タイム']

            # 着差、1着馬は2着との差をマイナスに
            # TODO 同着時対応
            if i == 0:
                winner_horse_no = str(row['馬番'])
            elif i == 1:
                self.horse_result_dict[winner_horse_no].diff = '-' + str(row['着差'])
                horse_result.diff = row['着差']
            else:
                horse_result.diff = row['着差']

            # TODO 同着時計算
            if str(row['着順']) == '1':
                horse_result.prize = str(self.race_info.first_prize)
            elif str(row['着順']) == '2':
                horse_result.prize = str(self.race_info.second_prize)
            elif str(row['着順']) == '3':
                horse_result.prize = str(self.race_info.third_prize)
            elif str(row['着順']) == '4':
                horse_result.prize = str(self.race_info.fourth_prize)
            elif str(row['着順']) == '5':
                horse_result.prize = str(self.race_info.fifth_prize)

            horse_result.agari = row['後3F']

            horse_result.horse_id = self.horse_race_info_dict[str(row['馬番'])].horse_id

            self.horse_result_dict[str(row['馬番'])] = horse_result

        # コーナー通過順抽出。pd.read_htmlでは','が除去されるため抽出不可
        # CSV出力時に区切り文字と混合しないため「|」を採用
        rank_table = soup.find('table', class_ = 'RaceCommon_Table Corner_Num').text.split('\n')
        for index in range(len(rank_table)):
            if rank_table[index] == '1コーナー':
                self.race_progress_info.corner1_rank = rank_table[index + 1].replace(',', '|')
            elif rank_table[index] == '2コーナー':
                self.race_progress_info.corner2_rank = rank_table[index + 1].replace(',', '|')
            elif rank_table[index] == '3コーナー':
                self.race_progress_info.corner3_rank = rank_table[index + 1].replace(',', '|')
            elif rank_table[index] == '4コーナー':
                self.race_progress_info.corner4_rank = rank_table[index + 1].replace(',', '|')

        # ラップ抽出。非公表の競馬場もあり
        # CSV出力時に区切り文字と混合しないため「|」を採用
        lap_table = soup.find('table', class_ = 'RaceCommon_Table Race_HaronTime')
        if lap_table != None:
            self.race_progress_info.lap_distance = '|'.join([distance.text.replace('m', '') for distance in lap_table.find_all('th')])
            self.race_progress_info.lap_time = '|'.join([wordchange.change_seconds(lap.text) for lap in lap_table.find('tr', class_ = 'HaronTime').find_all('td')])

    def get_bannei_result(self):
        pass

    def output_csv(self):
        '''取得したデータをCSV出力する'''

        # 出力タイプに応じてファイル名末尾の設定
        if self.output_type == 'y':
            filename_tail = f'_{self.race_date[:4]}'
        elif self.output_type == 'a':
            filename_tail = ''
        else:
            filename_tail = f'_{self.race_date[:6]}'

        # 発走前レースデータを出力
        race_info_df = pd.DataFrame.from_dict(vars(self.race_info), orient='index').T
        race_info_df.columns = [column.replace('_RaceInfo__', '') for column in race_info_df.columns]
        output.csv(race_info_df, f'race_info{filename_tail}')

        # 発走前馬データを出力
        if len(self.horse_race_info_dict) != 0:
            horse_race_info_df = pd.concat([pd.DataFrame.from_dict(vars(df), orient='index').T for df in self.horse_race_info_dict.values()])
            horse_race_info_df.columns = [column.replace('_HorseRaceInfo__', '') for column in horse_race_info_df.columns]
            output.csv(horse_race_info_df, f'horse_race_info{filename_tail}')
        else:
            self.logger.info(f'race_id:{self.race_id}\nが取得できなかったため出力を行いません')

        # 馬データを出力
        if len(self.horse_char_info_dict) != 0:
            horse_char_info_df = pd.concat([pd.DataFrame.from_dict(vars(df), orient='index').T for df in self.horse_char_info_dict.values()])
            horse_char_info_df.columns = [column.replace('_HorseCharInfo__', '') for column in horse_char_info_df.columns]
            output.csv(horse_char_info_df, f'horse_char_info{filename_tail}')
        else:
            self.logger.info(f'race_id:{self.race_id}\nが取得できなかったため出力を行いません')

        # レース進行データを出力
        race_progress_info_df = pd.DataFrame.from_dict(vars(self.race_progress_info), orient='index').T
        race_progress_info_df.columns = [column.replace('_RaceProgressInfo__', '') for column in race_progress_info_df.columns]
        output.csv(race_progress_info_df, f'race_progress_info{filename_tail}')

        # レース結果データを出力
        if len(self.horse_result_dict) != 0:
            horse_result_df = pd.concat([pd.DataFrame.from_dict(vars(df), orient='index').T for df in self.horse_result_dict.values()])
            horse_result_df.columns = [column.replace('_HorseResult__', '') for column in horse_result_df.columns]
            output.csv(horse_result_df, f'horse_result{filename_tail}')
        else:
            self.logger.info(f'race_id:{self.race_id}\nが取得できなかったため出力を行いません')

    def frame_no_culc(self, horse_num, horse_no):
        '''馬番と頭数から枠番を計算'''
        horse_no = int(horse_no)
        horse_num = int(horse_num)

        if horse_no == 1:
            return str(1)
        elif horse_num <= 8 or horse_no < horse_num * -1 + 18:
            return str(horse_no)
        elif horse_num <= 16:
            if horse_no <= 8:
                return str(min(8, horse_no) - int((horse_no - (horse_num * -1 + 16)) / 2))
            else:
                return str(int(8 - (horse_num - horse_no - 1) / 2))
        else:
            if horse_no >= 17:
                return str(8)
            elif horse_num == 18 and horse_no == 15:
                return str(7)
            else:
                return self.frame_no_culc(16, horse_no)

    def error_output(self, message, e, stacktrace):
        '''エラー時のログ出力/LINE通知を行う
        Args:
            message(str) : エラーメッセージ
            e(str) : エラー名
            stacktrace(str) : スタックトレース
        '''
        self.logger.error(message)
        self.logger.error(e)
        self.logger.error(stacktrace)
        line.send(message)
        line.send(e)
        line.send(stacktrace)

class RaceInfo():
    '''発走前のレースに関するデータのデータクラス'''
    def __init__(self):
        self.__race_id = '' # レースID(netkeiba準拠、PK)
        self.__race_date = '' # レース開催日
        self.__race_no = '' # レース番号
        self.__baba_id = '' # 競馬場コード
        self.__race_name = '' # レース名
        self.__race_type = '平' # レース形態(平地/障害)[地方は平地固定]
        self.__baba = '' # 馬場(芝/ダート)
        self.__weather = '' # 天候
        self.__glass_condition = '' # 馬場状態(芝)
        self.__dirt_condition = '' # 馬場状態(ダート)
        self.__distance = '' # 距離
        self.__around = '' # 回り(右/左)
        self.__in_out = '0' # 使用コース(内回り/外回り)[地方は内外ないため0固定]
        self.__race_time = '' # 発走時刻
        self.__hold_no = '' # 開催回
        self.__hold_date = '' # 開催日
        self.__race_class = '' # クラス
        self.__grade = '' # グレードo[ TODO 待戦未判明]
        self.__require_age = '' # 出走条件(年齢)o
        self.__load_kind = '0' # 斤量条件(定量/馬齢/別定/ハンデ)[地方では取れないため0固定]
        self.__first_prize = '' # 1着賞金
        self.__second_prize = '' # 2着賞金
        self.__third_prize = '' # 3着賞金
        self.__fourth_prize = '' # 4着賞金
        self.__fifth_prize = '' # 5着賞金
        self.__horse_num = '' # 出走頭数

    # getter
    @property
    def race_id(self): return self.__race_id
    @property
    def race_date(self): return self.__race_date
    @property
    def race_no(self): return self.__race_no
    @property
    def baba_id(self): return self.__baba_id
    @property
    def race_name(self): return self.__race_name
    @property
    def race_type(self): return self.__race_type
    @property
    def baba(self): return self.__baba
    @property
    def weather(self): return self.__weather
    @property
    def glass_condition(self): return self.__glass_condition
    @property
    def dirt_condition(self): return self.__dirt_condition
    @property
    def distance(self): return self.__distance
    @property
    def around(self): return self.__around
    @property
    def in_out(self): return self.__in_out
    @property
    def race_time(self): return self.__race_time
    @property
    def hold_no(self): return self.__hold_no
    @property
    def hold_date(self): return self.__hold_date
    @property
    def race_class(self): return self.__race_class
    @property
    def grade(self): return self.__grade
    @property
    def require_age(self): return self.__require_age
    @property
    def load_kind(self): return self.__load_kind
    @property
    def first_prize(self): return self.__first_prize
    @property
    def second_prize(self): return self.__second_prize
    @property
    def third_prize(self): return self.__third_prize
    @property
    def fourth_prize(self): return self.__fourth_prize
    @property
    def fifth_prize(self): return self.__fifth_prize
    @property
    def horse_num(self): return self.__horse_num

    # setter
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @race_date.setter
    def race_date(self, race_date): self.__race_date = race_date
    @race_no.setter
    def race_no(self, race_no): self.__race_no = race_no
    @baba_id.setter
    def baba_id(self, baba_id): self.__baba_id = baba_id
    @race_name.setter
    def race_name(self, race_name): self.__race_name = race_name
    @race_type.setter
    def race_type(self, race_type): self.__race_type = race_type
    @baba.setter
    def baba(self, baba): self.__baba = baba
    @weather.setter
    def weather(self, weather): self.__weather = weather
    @glass_condition.setter
    def glass_condition(self, glass_condition): self.__glass_condition = glass_condition
    @dirt_condition.setter
    def dirt_condition(self, dirt_condition): self.__dirt_condition = dirt_condition
    @distance.setter
    def distance(self, distance): self.__distance = distance
    @around.setter
    def around(self, around): self.__around = around
    @in_out.setter
    def in_out(self, in_out): self.__in_out = in_out
    @race_time.setter
    def race_time(self, race_time): self.__race_time = race_time
    @hold_no.setter
    def hold_no(self, hold_no): self.__hold_no = hold_no
    @hold_date.setter
    def hold_date(self, hold_date): self.__hold_date = hold_date
    @race_class.setter
    def race_class(self, race_class): self.__race_class = race_class
    @grade.setter
    def grade(self, grade): self.__grade = grade
    @require_age.setter
    def require_age(self, require_age): self.__require_age = require_age
    @load_kind.setter
    def load_kind(self, load_kind): self.__load_kind = load_kind
    @first_prize.setter
    def first_prize(self, first_prize): self.__first_prize = first_prize
    @second_prize.setter
    def second_prize(self, second_prize): self.__second_prize = second_prize
    @third_prize.setter
    def third_prize(self, third_prize): self.__third_prize = third_prize
    @fourth_prize.setter
    def fourth_prize(self, fourth_prize): self.__fourth_prize = fourth_prize
    @fifth_prize.setter
    def fifth_prize(self, fifth_prize): self.__fifth_prize = fifth_prize
    @horse_num.setter
    def horse_num(self, horse_num): self.__horse_num = horse_num

class RaceProgressInfo():
    '''レース全体のレース結果を保持するデータクラス'''
    def __init__(self):
        self.__race_id = '' # レースID(netkeiba準拠、PK)
        self.__corner1_rank = '' # 第1コーナー通過順(馬番)
        self.__corner2_rank = '' # 第2コーナー通過順(馬番)
        self.__corner3_rank = '' # 第3コーナー通過順(馬番)
        self.__corner4_rank = '' # 第4コーナー通過順(馬番)
        self.__lap_distance = '' # 先頭馬のラップ測定距離(m)
        self.__lap_time = '' # 先頭馬のラップタイム(秒)

    # getter
    @property
    def race_id(self): return self.__race_id
    @property
    def corner1_rank(self): return self.__corner1_rank
    @property
    def corner2_rank(self): return self.__corner2_rank
    @property
    def corner3_rank(self): return self.__corner3_rank
    @property
    def corner4_rank(self): return self.__corner4_rank
    @property
    def lap_distance(self): return self.__lap_distance
    @property
    def lap_time(self): return self.__lap_time

    # setter
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @corner1_rank.setter
    def corner1_rank(self, corner1_rank): self.__corner1_rank = corner1_rank
    @corner2_rank.setter
    def corner2_rank(self, corner2_rank): self.__corner2_rank = corner2_rank
    @corner3_rank.setter
    def corner3_rank(self, corner3_rank): self.__corner3_rank = corner3_rank
    @corner4_rank.setter
    def corner4_rank(self, corner4_rank): self.__corner4_rank = corner4_rank
    @lap_distance.setter
    def lap_distance(self, lap_distance): self.__lap_distance = lap_distance
    @lap_time.setter
    def lap_time(self, lap_time): self.__lap_time = lap_time

class HorseRaceInfo():
    '''各馬の発走前のデータを保持するデータクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)
        self.__race_id = '' # レースID(netkeiba準拠、PK) TODO
        self.__frame_no = '' # 枠番
        self.__horse_no = '' # 馬番
        self.__age = '' # 馬齢
        self.__gender = '' # 性別
        self.__load = '' # 斤量
        self.__jockey_id = '' # 騎手ID
        self.__jockey = '' # 騎手名
        self.__jockey_handi = '' # 騎手減量 [ TODO 出馬表から取れない]
        self.__win_odds = '' # 単勝オッズ
        self.__popular = '' # 人気
        self.__weight = '' # 馬体重
        self.__weight_change = '' # 馬体重増減
        self.__trainer_id = '' # 調教師ID
        self.__trainer = '' # 調教師名
        self.__trainer_belong = '' # 調教師所属厩舎
        self.__owner = '' # 馬主名 [ TODO 出馬表から取れない]
        self.__blank = '' # レース間隔
        self.__running_type = '' # 脚質(←netkeibaの主観データ？)
        self.__country = '' # 所属(外国馬か)
        self.__belong = '' # 所属(地方馬か)
        self.__blinker = '0' # ブリンカー(有/無)

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def race_id(self): return self.__race_id
    @property
    def frame_no(self): return self.__frame_no
    @property
    def horse_no(self): return self.__horse_no
    @property
    def age(self): return self.__age
    @property
    def gender(self): return self.__gender
    @property
    def load(self): return self.__load
    @property
    def jockey_id(self): return self.__jockey_id
    @property
    def jockey(self): return self.__jockey
    @property
    def jockey_handi(self): return self.__jockey_handi
    @property
    def win_odds(self): return self.__win_odds
    @property
    def popular(self): return self.__popular
    @property
    def weight(self): return self.__weight
    @property
    def weight_change(self): return self.__weight_change
    @property
    def trainer_id(self): return self.__trainer_id
    @property
    def trainer(self): return self.__trainer
    @property
    def trainer_belong(self): return self.__trainer_belong
    @property
    def owner(self): return self.__owner
    @property
    def blank(self): return self.__blank
    @property
    def running_type(self): return self.__running_type
    @property
    def country(self): return self.__country
    @property
    def belong(self): return self.__belong
    @property
    def blinker(self): return self.__blinker

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @frame_no.setter
    def frame_no(self, frame_no): self.__frame_no = frame_no
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @age.setter
    def age(self, age): self.__age = age
    @gender.setter
    def gender(self, gender): self.__gender = gender
    @load.setter
    def load(self, load): self.__load = load
    @jockey_id.setter
    def jockey_id(self, jockey_id): self.__jockey_id = jockey_id
    @jockey.setter
    def jockey(self, jockey): self.__jockey = jockey
    @jockey_handi.setter
    def jockey_handi(self, jockey_handi): self.__jockey_handi = jockey_handi
    @win_odds.setter
    def win_odds(self, win_odds): self.__win_odds = win_odds
    @popular.setter
    def popular(self, popular): self.__popular = popular
    @weight.setter
    def weight(self, weight): self.__weight = weight
    @weight_change.setter
    def weight_change(self, weight_change): self.__weight_change = weight_change
    @trainer_id.setter
    def trainer_id(self, trainer_id): self.__trainer_id = trainer_id
    @trainer.setter
    def trainer(self, trainer): self.__trainer = trainer
    @trainer_belong.setter
    def trainer_belong(self, trainer_belong): self.__trainer_belong = trainer_belong
    @owner.setter
    def owner(self, owner): self.__owner = owner
    @blank.setter
    def blank(self, blank): self.__blank = blank
    @running_type.setter
    def running_type(self, running_type): self.__running_type = running_type
    @country.setter
    def country(self, country): self.__country = country
    @belong.setter
    def belong(self, belong): self.__belong = belong
    @blinker.setter
    def blinker(self, blinker): self.__blinker = blinker


class HorseCharInfo():
    '''各馬の不変のデータを保持するクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)
        self.__horse_name = '' # 馬名
        self.__father = '' # 父名
        self.__mother = '' # 母名
        self.__grandfather = '' # 母父名
        self.__hair_color = '' # 毛色

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def horse_name(self): return self.__horse_name
    @property
    def father(self): return self.__father
    @property
    def mother(self): return self.__mother
    @property
    def grandfather(self): return self.__grandfather
    @property
    def hair_color(self): return self.__hair_color

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @horse_name.setter
    def horse_name(self, horse_name): self.__horse_name = horse_name
    @father.setter
    def father(self, father): self.__father = father
    @mother.setter
    def mother(self, mother): self.__mother = mother
    @grandfather.setter
    def grandfather(self, grandfather): self.__grandfather = grandfather
    @hair_color.setter
    def hair_color(self, hair_color): self.__hair_color = hair_color

class HorseResult():
    '''各馬のレース結果のデータクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK)
        self.__race_id = '' # レースID(netkeiba準拠、PK) TODO
        self.__horse_no = '' # 馬番
        self.__rank = '' # 着順
        self.__goal_time = '' # タイム
        self.__diff = '' # 着差
        self.__agari = '' # 上り3F
        self.__prize = '0' # 賞金

    # getter
    @property
    def horse_id(self): return self.__horse_id
    @property
    def race_id(self): return self.__race_id
    @property
    def horse_no(self): return self.__horse_no
    @property
    def rank(self): return self.__rank
    @property
    def goal_time(self): return self.__goal_time
    @property
    def diff(self): return self.__diff
    @property
    def agari(self): return self.__agari
    @property
    def prize(self): return self.__prize

    # setter
    @horse_id.setter
    def horse_id(self, horse_id): self.__horse_id = horse_id
    @race_id.setter
    def race_id(self, race_id): self.__race_id = race_id
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @rank.setter
    def rank(self, rank): self.__rank = rank
    @goal_time.setter
    def goal_time(self, goal_time): self.__goal_time = goal_time
    @diff.setter
    def diff(self, diff): self.__diff = diff
    @agari.setter
    def agari(self, agari): self.__agari = agari
    @prize.setter
    def prize(self, prize): self.__prize = prize


# TODO 単一メソッド動作確認用、後で消す
if __name__ == '__main__':
    rg = GetRaceData('202147012101')
    rg.main()