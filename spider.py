import numpy as np
import pandas as pd
import requests as rq
import json
import os
import base64
from bs4 import BeautifulSoup


def get_token():
    # 百度Access Token
    AK = "nNSR8Tj3fmLLLhryRrSN9EOH"
    SK = "YC8Oxy6NpngvMS9fMsqgQz2i9j94xU7D"
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials'\
        '&client_id=%s'\
        '&client_secret=%s' % (AK, SK)
    url = host
    response = rq.post(url)
    if (response):
        js = json.loads(response.text)
        return js['access_token']
    return None


# 臉部辨識
def FaceDetect(pic, token):
    # 圖片轉base64
    img = base64.b64encode(pic)
    URL = "https://aip.baidubce.com/rest/2.0/face/v3/detect"  # 百度AipFace
    params = {"access_token": token}
    data = {
        "face_field": "age,gender,beauty,qualities",
        "image_type": "BASE64",
        "image": img
    }
    s = rq.post(URL, params=params, data=data)
    r = s.json()["result"]
    for face in r["face_list"]:
        a = face['age']  # AI識別年紀
        b = face['beauty']  # AI識別顏值
        return a, b


def download(tmp2, titles, u, l):
    if tmp2 == 'i.imgur.com' or tmp2 == 'pbs.twimg.com' or tmp2 == '6.share.photo.xuite.net' or tmp2 == 's1.imgs.cc':
        pic_name = l.string.split("/")[-1]
        img2 = rq.get(l.string).content
    else:
        pic_name = l.string.split("/")[-1] + ".jpg"
        img2 = rq.get(l.string + '.jpg').content
    path = os.getcwd() + "/" + titles[urls.index(u)].strip('? ')  # 儲存路徑&標題防呆
    if not os.path.isdir(path):
        os.mkdir(path)
    with open(path + '/' + pic_name, 'wb') as f:
        f.write(img2)
    return img2


def get_article(n, url):
    while len(votes) < n:  # 至少n筆
        html = r.get(url).text
        soup = BeautifulSoup(html, 'lxml')  # lxml 解析器
        u = soup.select("div.btn-group.btn-group-paging a")  # paging按鈕
        url = "https://www.ptt.cc" + u[1]["href"]  # 上一頁的網址
        posts = soup.find_all("div", class_="r-ent")  # 貼文
        for post in posts:
            try:
                # 修正爆文為100
                if post.find("span").string != '爆':
                    v = int(post.find("span").string)  # 推文數
                else:
                    v = 100
                t = post.find("a").string.split(" ")[0]  # 分類
            except:
                v = np.nan
                t = np.nan
            # 排除推文數過低,其他分類和已刪除文章
            if t == '[正妹]' and v >= 15:
                titles.append(post.find("a").string.strip('[正妹] '))
                urls.append(post.find("a").get('href'))
                votes.append(v)
                author.append(post.find("div", class_="author").string)
                date.append(post.find("div", class_="date").string)


def get_link(links):
    for l in links:
        # 解析域名
        try:
            tmp2 = l.string.split("/")[2]
        except:
            tmp2 = np.nan
        # 排除非圖床連結 & 推文垃圾meme
        if l.parent.name != 'span' and (tmp2 == 'i.imgur.com'
                                        or tmp2 == 'imgur.com'
                                        or tmp2 == 'pbs.twimg.com'
                                        or tmp2 == '6.share.photo.xuite.net'
                                        or tmp2 == 's1.imgs.cc'):
            img[urls.index(u)].append(l.string)

            if votes[urls.index(u)] > 30:
                # 下載
                img2 = download(tmp2, titles, u, l)
                try:
                    a, b = FaceDetect(img2, get_token())
                    at.append(a)
                    bt.append(b)
                except:
                    pass

        # 有車就上
        elif tmp2 == 'www.instagram.com' or tmp2 == 'instagram.com' or tmp2 == 'twitter.com':
            ig[urls.index(u)].append(l.string)  # 門


if __name__ == '__main__':

    titles = []
    urls = []
    votes = []
    author = []
    date = []

    r = rq.Session()
    payload = {"from": "/bbs/Beauty/index.html", "yes": "yes"}
    r18 = r.post(
        "https://www.ptt.cc/ask/over18?from=%2Fbbs%2FBeauty%2Findex.html",
        payload)  # 18歲驗證
    url = "https://www.ptt.cc/bbs/Beauty/index.html"  # PTT 表特板
    n = int(input('到底?到底要幾篇?: '))
    get_article(n, url)

    img = []
    ig = []
    age = []
    beauty = []

    i = 1
    for u in urls:
        img.append([])  # 二維陣列初始化
        ig.append([])
        url = "https://www.ptt.cc" + u  # 文章網址
        os.system('cls')
        html = r.get(url).text
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find(id="main-content").find_all("a")  # 文章本體內連結
        print(titles[urls.index(u)].strip())  # 對應標題
        get_link(links)

        at = []
        bt = []
        try:
            age.append(sum(at) / len(at))
            beauty.append(sum(bt) / len(bt))
            print("看起來像%d歲, 顏值: %2.2f" %
                  (age[urls.index(u)], beauty[urls.index(u)]))
        except:
            pass

        print("...done(" + str(i) + ")")
        i += 1

    # 導入DataFrame
    Beauty_dict = {
        "votes": votes,
        "title": titles,
        "url": urls,
        "img": img,
        "ig": ig,
        "author": author,
        "date": date
        # "age(estimate)": age,
        # "beauty": beauty
    }
    df = pd.DataFrame(Beauty_dict)
    df.to_csv('Result.csv', na_rep='NA',
              encoding="utf_8_sig")  # 輸出csv檔, utf_8_sig避免中文亂碼
    print('--------------')
    print('top 20')
    print(df.sort_values(by='votes')[['votes', 'title']].tail(20))
