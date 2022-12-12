import numpy as np
import pandas as pd
import re
from common import line, soup as Soup, wordchange, logger as lg

class GetRaceData():
    '''netkeibaのサイトから中央競馬の過去レースデータを取得する

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

    def __init__(self, race_id, output_type = 'm', race_date = None):
        self.logger = lg.Logger(0)
        self.race_info = RaceInfo()
        self.horse_race_info_dict = {}
        self.horse_char_info_dict = {}
        self.race_progress_info = RaceProgressInfo()
        self.horse_result_dict = {}
        self.race_id = self.race_info.race_id = self.race_progress_info.race_id = race_id
        self.baba_id = self.race_info.baba_id = race_id[4:6]
        self.race_no = self.race_info.race_no = race_id[10:]
        self.race_date = race_date
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
        # 馬柱からデータ取得
        self.get_umabashira()

        # レース結果(DB)からデータ取得
        horse_dict = self.get_result()

    def get_umabashira(self):
        url = f'https://race.netkeiba.com/race/shutuba_past.html?race_id={self.race_id}'

        # 馬柱からデータを取得
        soup = Soup.get_soup(url)

        # コース情報や状態を抽出
        race_data_01 = soup.find('div', class_ = 'RaceData01')
        race_data_list = wordchange.rm(race_data_01.text).split('/')

        # TODO レースデータ不足チェック

        # 発走時刻取得
        self.race_info.race_time = race_data_list[0].replace('発走', '')

        # コース情報
        course = re.search('([芝|ダ|障])(\d+)m\((.*)\)', race_data_list[1])

        # 距離
        self.race_info.distance = course.groups()[1]

        # 平場/障害判定
        if course.groups()[0] == '障':
            self.race_info.race_type = '障'

            # 馬場と馬場状態
            baba = course.groups()[2]
            if '芝' in baba:
                if 'ダート' in baba:
                    self.race_info.baba = '芝ダ'
                    self.race_info.glass_condition = race_data_list[3].replace('馬場:', '')
                    if len(race_data_list) == 5:
                        self.race_info.dirt_condition = race_data_list[4].replace('馬場:', '')
                else:
                    self.race_info.baba = '芝'
                    self.race_info.glass_condition = race_data_list[3].replace('馬場:', '')
            else:
                self.race_info.baba = 'ダ'
                self.race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

            # 右回り/左回り
            around = re.sub(r'[芝ダート]', '', baba)
            if len(around) != 0:
                self.race_info.in_out = around

        else:
            self.race_info.race_type = '平'

            # 馬場と馬場状態
            baba = course.groups()[0]
            self.race_info.baba = baba
            if baba == '芝':
                self.race_info.glass_condition = race_data_list[3].replace('馬場:', '')
            elif baba == 'ダ':
                self.race_info.dirt_condition = race_data_list[3].replace('馬場:', '')

            # 右/左、内/外、直線
            around = course.groups()[2]
            if around == '直線':
                self.race_info.around = '直'
            else:
                self.race_info.around = around[0]
                if len(around) != 1:
                    self.race_info.in_out = around[1:]

        # 天候
        self.race_info.weather = race_data_list[2].replace('天候:', '')

        # 出走条件等の抽出
        race_data_02 = soup.find('div', class_ = 'RaceData02')

        # 開催回/日
        race_data_list = race_data_02.text.split('\n')
        self.race_info.hold_no = race_data_list[1].replace('回', '')
        # TODO 馬場コード
        self.race_info.hold_date = race_data_list[3].replace('日目', '')

        # 出走条件(馬齢/クラス)
        self.race_info.require_age = wordchange.full_to_half(race_data_list[4]).replace('サラ系', '').replace('障害', '')
        self.race_info.race_class = wordchange.full_to_half(race_data_list[5])

        # レース名
        race_name = soup.find('div', class_ = 'RaceName')
        self.race_info.race_name = race_name.text.replace('\n', '')

        # CSSからクラスチェック、13はWIN5
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

        # 待選、暫定処理としてグレードの末尾に付けておく
        if 'Icon_GradeType14' in str(race_name):
            self.race_info.grade += '待選'

        # 馬齢以外の出走条件
        require = race_data_list[7]

        # 国際/混合レース
        # 国際...外国産馬が出走可
        # 混合...日本調教外国産馬が出走可
        if '(国際)' in require:
            self.race_info.require_country = '国'
        elif '(混)' in require:
            self.race_info.require_country = '混'

        # 出走条件性別
        if '牡・牝' in require:
            self.race_info.require_gender = '牡牝'
        elif '牝' in require:
            self.race_info.require_gender = '牝'

        # 指定/特別指定
        #   マル指...特指以外の地方出走可
        #   カク指...地方騎手騎乗可
        # 特別指定...JRA認定地方レースの1着馬が出走可
        if '(指)' in require:
            self.race_info.require_local = 'マル指'
        elif '(特指)' in require:
            self.race_info.require_local = '特指'
        elif '指' in require:
            self.race_info.require_local = 'カク指'

        '''
        # 九州産馬限定戦・見習騎手限定戦、レース数が極端に少ないうえ
        # レース結果に影響を及ぼすとは考えにくいので現状はコメントアウト

        if '九州産馬' in require:
            self.race_info.require_local = '1'

        # レース結果に影響を及ぼすとは考えにくいのでこちらもコメントアウト
        if '見習騎手' in require:
            self.race_info.require_beginner_jockey = '1'
        '''

        # 斤量条件[定量/馬齢/別定/ハンデ] TODO 詳細条件取れるか
        self.race_info.load_kind = race_data_list[8]

        # 登録頭数
        self.race_info.regist_num = race_data_list[9].replace('頭', '')

        # TODO 出走頭数計算

        # レース賞金
        prize = re.search('本賞金:(\d+),(\d+),(\d+),(\d+),(\d+)万円', race_data_list[11])
        self.race_info.first_prize = prize.groups()[0]
        self.race_info.second_prize = prize.groups()[1]
        self.race_info.third_prize = prize.groups()[2]
        self.race_info.fourth_prize = prize.groups()[3]
        self.race_info.fifth_prize = prize.groups()[4]

        # 各馬の情報取得
        fc = soup.select('div[class="fc"]')
        for i, info in enumerate(fc):
            # 本レースでの馬情報格納用(馬体重、馬齢...)
            horse_race_info = HorseRaceInfo()
            # 不変の馬情報格納用(馬名、父・母名...)
            horse_char_info = HorseCharInfo()

            # レースID追加
            horse_race_info.race_id = self.race_id

            # 所属や馬名の書いてる枠
            horse_type = info.find('div', class_ = 'Horse02')

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

            # TODO 馬ID取得

            # TODO 馬名取得

            # 父名・母名・母父名
            horse_char_info.father = info.find('div', class_ = 'Horse01').text
            horse_char_info.mother = info.find('div', class_ = 'Horse03').text
            horse_char_info.grandfather = info.find('div', class_ = 'Horse04').text.replace('(', '').replace(')', '')

            # TODO 調教師・調教師所属

            # TODO netkeiba独自の調教師ID

            # 出走間隔(週)
            blank = info.find('div', class_ = 'Horse06').text
            if blank == '連闘':
                horse_race_info.blank = '0'
            else:
                blank_week = re.search('中(\d+)週', blank)
                # 初出走判定
                if blank_week == None:
                    horse_race_info.blank = '-1'
                else:
                    horse_race_info.blank = prize.groups()[0]

            # 脚質(netkeiba独自)
            running_type = str(info.find('div', class_ = 'Horse06'))
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

            # TODO 馬体重

            # TODO 計不対応

            # TODO 単勝オッズ

            # 馬番・枠番
            horse_race_info.horse_no = str(i + 1)
            horse_race_info.frame_no = self.frame_no_culc(self.race_info.regist_num, int(i + 1))

            self.horse_race_info_dict[str(i + 1)] = horse_race_info
            self.horse_char_info_dict[str(i + 1)] = horse_char_info

        # 騎手等記載の隣の枠から情報取得
        jockeys = soup.find_all('td', class_ = 'Jockey')
        for i, info in enumerate(jockeys):

            # 最後の枠は説明用のサンプル枠なので飛ばす
            if i == len(jockeys) - 1:
                break

            horse_race_info = self.horse_race_info_dict[str(i + 1)]
            horse_char_info = self.horse_char_info_dict[str(i + 1)]

            # 性別・馬齢・毛色
            m = re.search('([牡|牝|セ])(\d+)(.+)', info.find('span', class_ = 'Barei').text)
            if m != None:
                horse_race_info.gender = m.groups()[0]
                horse_race_info.age = m.groups()[1]
                horse_char_info.hair_color = m.groups()[2]

            # 騎手名・netkeiba独自の騎手ID
            jockey = re.search('db.netkeiba.com/jockey/result/recent/(\d+)/" target="_blank">(.+)</a>', str(info))
            if jockey != None:
                horse_race_info.jockey_id = str(jockey.groups()[0])
                horse_race_info.jockey = jockey.groups()[1]

            # 斤量
            load = re.search('<span>(\d+\d.\d+)</span>', str(info))
            if load != None:
                horse_race_info.load = load.groups()[0]

            self.horse_race_info_dict[str(i + 1)] = horse_race_info
            self.horse_char_info_dict[str(i + 1)] = horse_char_info

    def get_result(self):
        '''レース結果ページからレース結果を抽出する'''

        url = f'https://race.netkeiba.com/race/result.html?race_id={self.race_id}'

        # レース結果(HTML全体)
        soup = Soup.get_soup(url)

        # read_htmlで抜けなくなる余分なタグを除去後に結果テーブル抽出
        tables = pd.read_html(str(soup).replace('<diary_snap_cut>', '').replace('</diary_snap_cut>', ''))

        # TODO ここまで
        print(tables)
        exit()

        table = tables[0]

        # 箱用意{馬番:[HorseInfo, HorseResult]}
        horse_dict = {i: [HorseInfo(), HorseResult()] for i in table['馬番']}

        # 1着馬の馬番
        winner_horse_no = 0

        # 行ごとに切り出し
        # TODO 除外・取消馬の処理
        for i, index in enumerate(table.index):
            row = table.loc[index]

            # キーになる馬番を先に取得
            no = row['馬番']

            # 馬の情報の各項目を設定
            horse_dict[no][0].frame_no = row['枠番']
            horse_dict[no][0].horse_no = row['馬番']
            horse_dict[no][0].horse_name = row['馬名']
            # 頭1文字が性別、2文字目以降が年齢
            horse_dict[no][0].gender = row['性齢'][0]
            horse_dict[no][0].age = row['性齢'][1:]
            horse_dict[no][0].load = row['斤量']
            horse_dict[no][0].jockey = row['騎手']
            horse_dict[no][0].win_odds = row['単勝']
            horse_dict[no][0].popular = row['人気']
            # 括弧内が増減、外が馬体重
            weight = re.search('(\d+)\((.+)\)', row['馬体重'])
            # 馬体重不明チェック(新馬・前走計不時は増減は0と表記)
            if weight == None:
                horse_dict[no][0].weight = -1
                horse_dict[no][0].weight_change = -999
            else:
                horse_dict[no][0].weight = weight.groups()[0]
                horse_dict[no][0].weight_change = weight.groups()[1].replace('±', '').replace('+', '')
            # 調教師チェック[東]美浦、[西]栗東
            trainer = re.search('\[(.+)\] (.+)', row['調教師'])
            if trainer == None:
                horse_dict[no][0].trainer_belong = '-'
                horse_dict[no][0].trainer = '-'
            else:
                horse_dict[no][0].trainer_belong = trainer.groups()[0]
                horse_dict[no][0].trainer = trainer.groups()[1]
            horse_dict[no][0].horse_no = row['馬番']
            horse_dict[no][0].owner = row['馬主']

            # レース結果の各項目を設定
            horse_dict[no][1].horse_no = row['馬番']
            horse_dict[no][1].rank = row['着順']
            horse_dict[no][1].goal_time = row['タイム']
            # 着差、1着馬は2着との差をマイナスに
            if i == 0:
                winner_horse_no = no
            elif i == 1:
                horse_dict[winner_horse_no][1].diff = '-' + str(row['着差'])
                horse_dict[no][1].diff = row['着差']
            else:
                horse_dict[no][1].diff = row['着差']
            horse_dict[no][1].agari = row['上り']
            if not np.isnan(row['賞金(万円)']):
                horse_dict[no][1].prize = row['賞金(万円)']

        return horse_dict

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
        self.__race_id = '' # レースID(netkeiba準拠、PK)o
        self.__race_date = '' # レース開催日 TODO
        self.__race_no = '' # レース番号o
        self.__baba_id = '' # 競馬場コードo
        self.__race_name = '' # レース名o
        self.__race_type = '' # レース形態(平地/障害)o
        self.__baba = '' # 馬場(芝/ダート)o
        self.__weather = '' # 天候o
        self.__glass_condition = '' # 馬場状態(芝)o
        self.__dirt_condition = '' # 馬場状態(ダート)o
        self.__distance = '' # 距離o
        self.__around = '' # 回り(右/左)o
        self.__in_out = '' # 使用コース(内回り/外回り)o
        self.__race_time = '' # 発走時刻o
        self.__hold_no = '' # 開催回o
        self.__hold_date = '' # 開催日o
        self.__race_class = '' # クラスo
        self.__grade = '' # グレード TODO
        self.__require_age = '' # 出走条件(年齢)o
        self.__require_gender = '' # 出走条件(牝馬限定戦)o
        self.__require_kyushu = '0' # 出走条件(九州産馬限定戦)o
        self.__require_beginner_jockey = '0' # 出走条件(見習騎手限定戦)o
        self.__require_country = '' # 出走条件(国際/混合)o
        self.__require_local = '' # 出走条件(特別指定/指定)o
        self.__load_kind = '' # 斤量条件(定量/馬齢/別定/ハンデ)o
        self.__first_prize = '' # 1着賞金o
        self.__second_prize = '' # 2着賞金o
        self.__third_prize = '' # 3着賞金o
        self.__fourth_prize = '' # 4着賞金o
        self.__fifth_prize = '' # 5着賞金o
        self.__regist_num = '' # 登録頭数o

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
    def require_gender(self): return self.__require_gender
    @property
    def require_kyushu(self): return self.__require_kyushu
    @property
    def require_beginner_jockey(self): return self.__require_beginner_jockey
    @property
    def require_country(self): return self.__require_country
    @property
    def require_local(self): return self.__require_local
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
    def regist_num(self): return self.__regist_num

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
    @require_gender.setter
    def require_gender(self, require_gender): self.__require_gender = require_gender
    @require_kyushu.setter
    def require_kyushu(self, require_kyushu): self.__require_kyushu = require_kyushu
    @require_beginner_jockey.setter
    def require_beginner_jockey(self, require_beginner_jockey): self.__require_beginner_jockey = require_beginner_jockey
    @require_country.setter
    def require_country(self, require_country): self.__require_country = require_country
    @require_local.setter
    def require_local(self, require_local): self.__require_local = require_local
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
    @regist_num.setter
    def regist_num(self, regist_num): self.__regist_num = regist_num

class RaceProgressInfo():
    '''レース全体のレース結果を保持するデータクラス'''
    def __init__(self):
        self.__race_id = '' # レースID(netkeiba準拠、PK) TODO
        self.__corner1_rank = '' # 第1コーナー通過順(馬番) TODO
        self.__corner2_rank = '' # 第2コーナー通過順(馬番) TODO
        self.__corner3_rank = '' # 第3コーナー通過順(馬番) TODO
        self.__corner4_rank = '' # 第4コーナー通過順(馬番) TODO
        self.__lap_distance = '' # 先頭馬のラップ測定距離(m) TODO
        self.__lap_time = '' # 先頭馬のラップタイム(秒) TODO

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
    pass

class HorseCharInfo():
    pass

class HorseInfo(): # TODO 地方と同じになるように分割し、あとで消す
    '''各馬の発走前のデータを保持するデータクラス'''
    def __init__(self):
        self.__frame_no = '' # 枠番o
        self.__horse_no = '' # 馬番(複合PK)o
        self.__horse_name = '' # 馬名o
        self.__age = '' # 馬齢o
        self.__gender = '' # 性別o
        self.__load = '' # 斤量o
        self.__jockey = '' # 騎手名o
        self.__jockey_handi = '' # 騎手減量 TODO
        self.__win_odds = '' # 単勝オッズo
        self.__popular = '' # 人気o
        self.__weight = '' # 馬体重o
        self.__weight_change = '' # 馬体重増減o
        self.__trainer = '' # 調教師名o
        self.__trainer_belong = '' # 調教師所属(美浦/栗東)o
        self.__owner = '' # 馬主名o

        # 以下は馬柱から
        # TODO 不変データ(血統関係)は別クラスで切り出し、未出走時のみ入れるか検討
        # TODO ↑最古データが未出走でない場合は取得できないから一回ずつチェック入れる？
        self.__blank = '' # レース間隔o
        self.__father = '' # 父名o
        self.__mother = '' # 母名o
        self.__grandfather = '' # 母父名o
        self.__running_type = '' # 脚質(←netkeibaの主観データ？)o
        self.__country = '日' # 所属(外国馬か)o
        self.__belong = '非' # 所属(地方馬か)o
        self.__blinker = '0' # ブリンカー(有/無)o
        self.__hair_color = '' # 毛色

    # getter
    @property
    def frame_no(self): return self.__frame_no
    @property
    def horse_no(self): return self.__horse_no
    @property
    def horse_name(self): return self.__horse_name
    @property
    def age(self): return self.__age
    @property
    def gender(self): return self.__gender
    @property
    def load(self): return self.__load
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
    def trainer(self): return self.__trainer
    @property
    def trainer_belong(self): return self.__trainer_belong
    @property
    def owner(self): return self.__owner
    @property
    def blank(self): return self.__blank
    @property
    def father(self): return self.__father
    @property
    def mother(self): return self.__mother
    @property
    def grandfather(self): return self.__grandfather
    @property
    def running_type(self): return self.__running_type
    @property
    def country(self): return self.__country
    @property
    def belong(self): return self.__belong
    @property
    def blinker(self): return self.__blinker
    @property
    def hair_color(self): return self.__hair_color

    # setter
    @frame_no.setter
    def frame_no(self, frame_no): self.__frame_no = frame_no
    @horse_no.setter
    def horse_no(self, horse_no): self.__horse_no = horse_no
    @horse_name.setter
    def horse_name(self, horse_name): self.__horse_name = horse_name
    @age.setter
    def age(self, age): self.__age = age
    @gender.setter
    def gender(self, gender): self.__gender = gender
    @load.setter
    def load(self, load): self.__load = load
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
    @trainer.setter
    def trainer(self, trainer): self.__trainer = trainer
    @trainer_belong.setter
    def trainer_belong(self, trainer_belong): self.__trainer_belong = trainer_belong
    @owner.setter
    def owner(self, owner): self.__owner = owner
    @blank.setter
    def blank(self, blank): self.__blank = blank
    @father.setter
    def father(self, father): self.__father = father
    @mother.setter
    def mother(self, mother): self.__mother = mother
    @grandfather.setter
    def grandfather(self, grandfather): self.__grandfather = grandfather
    @running_type.setter
    def running_type(self, running_type): self.__running_type = running_type
    @country.setter
    def country(self, country): self.__country = country
    @belong.setter
    def belong(self, belong): self.__belong = belong
    @blinker.setter
    def blinker(self, blinker): self.__blinker = blinker
    @hair_color.setter
    def hair_color(self, hair_color): self.__hair_color = hair_color

class HorseResult():
    '''各馬のレース結果のデータクラス'''
    def __init__(self):
        self.__horse_id = '' # 競走馬ID(netkeiba準拠、複合PK) TODO
        self.__race_id = '' # レースID(netkeiba準拠、PK) TODO
        self.__horse_no = '' # 馬番(複合PK)o
        self.__rank = '' # 着順o
        self.__goal_time = '' # タイムo
        self.__diff = '' # 着差o
        self.__agari = '' # 上り3Fo
        self.__prize = '0' # 賞金o

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
    rg = GetRaceData('202006010901', '20200126')
    rg.main()