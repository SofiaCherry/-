# 抓取今日头条图片（打开今日头条，搜索需要的关键词）
# 运行前请更换你自己的cookie(手动打开浏览器搜索今日头条并登录，然后复制你自己的cookie)，
# 然后还需确定你搜索的关键词和一级文件夹是否已经创建好(文件夹有4处需要替换(path)，关键词1处)，
# 这里默认翻6页，所以还需确认你搜索的是否够翻6次（这个是有底线的，一直往下划，查看json能加载多少个(有些只能加载到offset=180，也就是9次)）
# 因时间问题，不做动态输入搜索关键词和一级文件夹，有需要修改代码即可
import requests
import re
from urllib import request
import os
import random

headers = {
    'cookie': 'csrftoken=9494ae34e9e75cdfdf6a977b9834f1c2; tt_webid=6801649363082216967; ttcid=b6f21a882d6a422a8bcf2fe3dd044d9a31; WEATHER_CITY=%E5%8C%97%E4%BA%AC; SLARDAR_WEB_ID=f32ac3e9-b215-4984-bcf8-1db3a8a187cf; tt_webid=6801649363082216967; sso_uid_tt=4e51ff47e369b88c05102c33158b3bd5; sso_uid_tt_ss=4e51ff47e369b88c05102c33158b3bd5; toutiao_sso_user=fda05989c553dfe23cb314a273195daf; toutiao_sso_user_ss=fda05989c553dfe23cb314a273195daf; sid_guard=4f1c7eea3c3edd896413f228cde9e367%7C1583633831%7C5184000%7CThu%2C+07-May-2020+02%3A17%3A11+GMT; uid_tt=41a95671a8e5d4f4300b1cf1263a84d9; uid_tt_ss=41a95671a8e5d4f4300b1cf1263a84d9; sid_tt=4f1c7eea3c3edd896413f228cde9e367; sessionid=4f1c7eea3c3edd896413f228cde9e367; sessionid_ss=4f1c7eea3c3edd896413f228cde9e367; s_v_web_id=verify_k7jttqgy_gtUHQcJQ_tg1G_4JaZ_8YOI_dEvuza9I76JH; __tasessionId=o9xyn362l1583745314873; tt_scid=fCtjtxzJ5.oygNq9E6MKnA0Luj.RM5YlI64ZqlBkqzIlApWDsGVVHTOiw-12jTtPa222',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
}

# 避免文件名含有不合法字符
def correct_title(title):
    # 文件名最好不要含有.，否则有的系统会报错
    error_set = ['/', '\\', ':', '*', '?', '"', '|', '<', '>','.']
    for c in title:
        if c in error_set:
            title = title.replace(c, '')
    return title


def get_article_url(url,offset):
    article_urls = []
    gallery_article_url =[]
    params = {
        'aid': '24',
        'app_name': 'web_search',
        # 控制翻页的参数
        'offset': offset,
        'format': 'json',
        # 搜索图片的关键词
        'keyword': '章若楠',
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    response = requests.get(url=url,headers=headers,params=params).json()
    for i in response['data']:
        # 含有文章链接的data和文章里面不允许有视频
        # get取值如果该键名则会返回None,中括号取值如果没有键名则会报错
        if i.get('article_url') is not None and i.get('has_video') == False:
            # 手动轮播图与普通图的区别
            if i.get('has_gallery') == False:
                article_urls.append(i.get('article_url'))
            else:
                gallery_article_url.append(i.get('article_url'))
        else:
            continue
    # 返回一个元组，（[普通图片文章链接]，[手动轮播文章链接]）
    return article_urls,gallery_article_url


def get_img(urls):
    # 如果有普通文章链接
    if len(urls[0]) >= 1:
        for i in urls[0]:
            print(i)
            html = requests.get(url=i, headers=headers).text
            # 第一个括号匹配的是该文章的标题，第二个括号匹配的是包含图片链接的字符串
            img_str = re.search('articleInfo.*?title: \'&quot;(.*?)&quot;.*?content(.*?)groupId', html, re.S)
            # 有些链接无法下载，比如里面有微信公众号的文章（里面的图片并不好看，所以直接跳过，不做兼容）
            try:
                # 以每一篇文章的标题命名二级文件夹
                filename = img_str.group(1)
                # 过滤文件命名中的不合法字符
                filename = correct_title(filename)
                # 以标题创建文件夹
                try:
                    path = './zhangruonan/' + filename
                    # mkdir需要事先创建好一级文件夹，makedirs才会递归创建文件夹
                    os.mkdir(path)
                # 如果有重复文件名则在文件名后面随机加一个数字
                except FileExistsError:
                    path = './zhangruonan/' + filename + str(random.randint(1, 100))
                    os.mkdir(path)
                # 匹配图片的正则表达式
                img_pattern = '.*?http(:.*?)\&quot'
                img_list = re.findall(img_pattern, img_str.group(2), re.S)
                for i in img_list:
                    # 替换每个链接中多余的字符
                    i = i.replace('\\u002F', '/')
                    i = i.replace('\\', '')
                    # 拼接url
                    i = 'http' + i
                    # 截取链接最后一串字符作为图片的名称(包含了"/")
                    img_title = i[i.rfind("/"):]
                    request.urlretrieve(i, path + img_title + ".jpg")
                print(filename + "共" + str(len(img_list)) + "张图片下载完毕！！！")
            except AttributeError:
                print("此链接无法下载！！！")
                continue
    # 如果有手动轮播文章链接
    if len(urls[1]) >=1:
        for i in urls[1]:
            print(i)
            html = requests.get(url=i, headers=headers).text
            # 匹配手动轮播文章的标题和含有图片链接的字符串
            img_str = re.search('BASE_DATA.galleryInfo.*?title: \'(.*?)\'.*?gallery(.*?)\)', html,re.S)
            # 以下步骤和上面基本无异（因小生才疏学浅，写了一些重复代码，若有高手还请指点）
            try:
                text = img_str.group(2)
                filename = img_str.group(1)
                filename = correct_title(filename)
                try:
                    path = './zhangruonan/' + filename
                    os.mkdir(path)
                except FileExistsError:
                    path = './zhangruonan/' + filename + str(random.randint(1, 100))
                    os.mkdir(path)
                # 这个正则用于匹配图片链接，需要多揣摩
                img_pattern = r'{\\"url\\":\\"http([^,]*?)\\",\\"width.*?}'
                img_list = re.findall(img_pattern,text,re.S)
                for i in img_list:
                    i = i.replace(r'\\\u002F','/')
                    i = "http" + i
                    img_title = i[i.rfind("/"):]
                    request.urlretrieve(i, path + img_title + ".jpg")
                print(filename + "共" + str(len(img_list)) + "张图片下载完毕！！！")
            except AttributeError:
                print("此链接无法下载！！！")
                continue


if __name__ == "__main__":
    url = 'https://www.toutiao.com/api/search/content/'
    # 控制翻页
    for i in range(0,6):
        print("第"+str(i+1)+"页开始下载！！！")
        offset = i * 20
        urls = get_article_url(url,offset)
        get_img(urls)