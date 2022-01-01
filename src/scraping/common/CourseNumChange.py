def netkeiba(race_course_num):
    if race_course_num == '01':
        return '札幌'
    elif race_course_num == '02':
        return '函館'
    elif race_course_num == '03':
        return '福島'
    elif race_course_num == '04':
        return '新潟'
    elif race_course_num == '05':
        return '東京'
    elif race_course_num == '06':
        return '中山'
    elif race_course_num == '07':
        return '中京'
    elif race_course_num == '08':
        return '京都'
    elif race_course_num == '09':
        return '阪神'
    elif race_course_num == '10':
        return '小倉'
    elif race_course_num == '30':
        return '門別'
    elif race_course_num == '31':
        return '北見' # ～2006年
    elif race_course_num == '32':
        return '岩見沢' # ～2006年
    elif race_course_num == '33':
        return '帯広' # ～1997年。ばんえいではない
    elif race_course_num == '34':
        return '旭川' # ～2008年
    elif race_course_num == '35':
        return '盛岡'
    elif race_course_num == '36':
        return '水沢'
    elif race_course_num == '37':
        return '上山' # ～2003年
    elif race_course_num == '38':
        return '三条' # ～2001年
    elif race_course_num == '39':
        return '足利' # ～2003年
    elif race_course_num == '40':
        return '宇都宮' # ～2005年
    elif race_course_num == '41':
        return '高崎' # ～2004年
    elif race_course_num == '42':
        return '浦和'
    elif race_course_num == '43':
        return '船橋'
    elif race_course_num == '44':
        return '大井'
    elif race_course_num == '45':
        return '川崎'
    elif race_course_num == '46':
        return '金沢'
    elif race_course_num == '47':
        return '笠松'
    elif race_course_num == '48':
        return '名古屋'
    elif race_course_num == '49':
        return '紀三井寺' # ～1988年
    elif race_course_num == '50':
        return '園田'
    elif race_course_num == '51':
        return '姫路'
    elif race_course_num == '52':
        return '益田' # ～2002年
    elif race_course_num == '53':
        return '福山' # ～2013年
    elif race_course_num == '54':
        return '高知'
    elif race_course_num == '55':
        return '佐賀'
    elif race_course_num == '56':
        return '荒尾' # ～2011年
    elif race_course_num == '57':
        return '中津' # ～2001年
    elif race_course_num == '58':
        return '札幌' # ～2009年。地方競馬
    elif race_course_num == '59':
        return '函館' # ～1997年。地方競馬
    elif race_course_num == '60':
        return '新潟' # ～2002年。地方競馬
    elif race_course_num == '61':
        return '中京' # ～2002年。地方競馬
    elif race_course_num == '62':
        return '春木' # ～1974年
    elif race_course_num == '63':
        return '北見' # ～2006年。ばんえい
    elif race_course_num == '64':
        return '岩見沢' # ～2006年。ばんえい
    elif race_course_num == '65':
        return '帯広'
    elif race_course_num == '66':
        return '旭川' # ～2006年。ばんえい

    raise ValueError("競馬場コード変換で例外が発生しました")

def rakuten(race_course_num):
    if race_course_num == '01':
        return '北見' # ～2006年。ばんえい
    elif race_course_num == '02':
        return '岩見沢' # ～2006年。ばんえい
    elif race_course_num == '03':
        return '帯広'
    elif race_course_num == '04':
        return '旭川' # ～2006年。ばんえい
    elif race_course_num == '05':
        return '岩見沢' # ～2006年
    elif race_course_num == '06':
        return '帯広' # ～1997年。ばんえいではない
    elif race_course_num == '07':
        return '旭川' # ～2008年。
    elif race_course_num == '08':
        return '札幌' # ～2009年。地方競馬
    elif race_course_num == '09':
        return '函館' # ～1997年。地方競馬
    elif race_course_num == '10':
        return '盛岡'
    elif race_course_num == '11':
        return '水沢'
    elif race_course_num == '12':
        return '上山' # ～2003年
    elif race_course_num == '13':
        return '新潟' # ～2002年。地方競馬
    elif race_course_num == '14':
        return '三条' # ～2001年
    elif race_course_num == '15':
        return '足利' # ～2003年
    elif race_course_num == '16':
        return '宇都宮' # ～2005年
    elif race_course_num == '17':
        return '高崎' # ～2004年
    elif race_course_num == '18':
        return '浦和'
    elif race_course_num == '19':
        return '船橋'
    elif race_course_num == '20':
        return '大井'
    elif race_course_num == '21':
        return '川崎'
    elif race_course_num == '22':
        return '金沢'
    elif race_course_num == '23':
        return '笠松'
    elif race_course_num == '24':
        return '名古屋'
    elif race_course_num == '25':
        return '中京' # ～2002年。地方競馬
    elif race_course_num == '26':
        return '紀三井寺' # ～1988年
    elif race_course_num == '27':
        return '園田'
    elif race_course_num == '28':
        return '姫路'
    elif race_course_num == '29':
        return '益田' # ～2002年
    elif race_course_num == '30':
        return '福山' # ～2013年
    elif race_course_num == '31':
        return '高知'
    elif race_course_num == '32':
        return '佐賀'
    elif race_course_num == '33':
        return '荒尾'
    elif race_course_num == '34':
        return '中津' # ～2001年
    elif race_course_num == '35':
        return '春木' # ～1974年
    elif race_course_num == '36':
        return '門別'
    
    raise ValueError("競馬場コード変換で例外が発生しました")