import package
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from common import soup, logger, output

def main(url = 'https://www.ai-yuma.com/'):
    while True:
        logger.info(url)

        # 記事一覧のHTMLを取得
        html = soup.get_soup(url)

        # 記事/予測画像のURLを取得
        try:
            img_links, text_links = get_article_link(html)
        except Exception as e:
            logger.error(str(html))
            logger.error(str(e))

        # 画像の予測を取得
        for link in img_links:
            try:
                get_img_pred(link, img_links[link])
            except Exception as e:
                logger.error(str(link))
                logger.error(str(e))

        # テキストの予測を取得
        for link in text_links:
            get_text_pred(link, text_links[link])
            try:
                get_text_pred(link)
            except Exception as e:
                logger.error(str(link))
                logger.error(str(e))

        # 次ページのURL取得
        try:
            url = get_url(html)
        except Exception as e:
            logger.error(str(link))
            logger.error(str(e))

        if url == None: break

def get_img_pred(img_url, title):
    # TODO
    pass

def get_text_pred(url, title):
    get_flg = False
    html = soup.get_soup(url)
    content = html.find('div', class_ = 'entry-content').text
    pred_list = []

    for pred in re.finditer('[◎|◯|▲|△|☆|－].+\d+【.+%】.+\(.+\)', content):
        pred_list.append(pred[0].replace(' ', ''))
        get_flg = True

    if not get_flg:
        logger.warning(f'予測未取得：{url}')
        return

    output(pred_list, title)


def get_url(html):
    # span pager-next 次のページ /pager-prev 前のページ
    url_frame = html.find('span', class_ = 'pager-next')
    if url_frame == None:
        return None
    url = url_frame.find('a').get('href')
    return url

def output_csv(pred_list, title):
    race_info = pd.DataFrame(list(re.search('(\d+)(.+)(\d+)R', title).groups()) for _ in range(len(pred_list)))
    pred = pd.DataFrame([re.search('.(\d+)【(.+)%】(.+)\((.+)\)', i).groups() for i in pred_list], index = race_info.index)
    df = pd.concat([race_info, pred], axis = 1)
    df.columns = []

    output.csv(df, 'yuma')

def get_article_link(html):
    # リンク先の記事が予測ページかの判定
    pred_link_index = []
    link_url = []
    article_title = []
    links = html.find_all('h1', class_ = 'entry-title')
    for index, link in enumerate(links):
        pred_link = re.search('\d{8} .+\dR', link.text)
        if pred_link != None:
            pred_link_index.append(index)
        # index単位で管理するので対象外のリンクも一時保管
        link_url.append(link.find('a').get('href'))
        article_title.append(link.text)

    # 記事概要に文字があるか(=テキスト予測か画像予測か)の判定
    img_pred = {}
    text_pred = {}
    bodys = html.find_all('div', class_ = 'entry-content')
    for index in pred_link_index:
        if bodys[index].text.replace('\n', '') == '':
            img = bodys[index].find('img').get('src')
            if img != None:
                img_pred[img] = article_title[index].replace('\n', '')
        else:
            text_pred[link_url[index]] = article_title[index].replace('\n', '')

    return img_pred, text_pred


if __name__ == '__main__':
    logger = logger.Logger(0)
    main()