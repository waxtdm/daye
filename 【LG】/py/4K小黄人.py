# coding = utf-8
# !/usr/bin/python

"""

作者 丢丢喵 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://www.fullhd.xxx"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

pm = ''

class Spider(Spider):
    global xurl
    global headerx
    global headers

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def extract_middle_text(self, text, start_str, end_str, pl, start_index1: str = '', end_index2: str = ''):
        if pl == 3:
            plx = []
            while True:
                start_index = text.find(start_str)
                if start_index == -1:
                    break
                end_index = text.find(end_str, start_index + len(start_str))
                if end_index == -1:
                    break
                middle_text = text[start_index + len(start_str):end_index]
                plx.append(middle_text)
                text = text.replace(start_str + middle_text + end_str, '')
            if len(plx) > 0:
                purl = ''
                for i in range(len(plx)):
                    matches = re.findall(start_index1, plx[i])
                    output = ""
                    for match in matches:
                        match3 = re.search(r'(?:^|[^0-9])(\d+)(?:[^0-9]|$)', match[1])
                        if match3:
                            number = match3.group(1)
                        else:
                            number = 0
                        if 'http' not in match[0]:
                            output += f"#{match[1]}${number}{xurl}{match[0]}"
                        else:
                            output += f"#{match[1]}${number}{match[0]}"
                    output = output[1:]
                    purl = purl + output + "$$$"
                purl = purl[:-3]
                return purl
            else:
                return ""
        else:
            start_index = text.find(start_str)
            if start_index == -1:
                return ""
            end_index = text.find(end_str, start_index + len(start_str))
            if end_index == -1:
                return ""

        if pl == 0:
            middle_text = text[start_index + len(start_str):end_index]
            return middle_text.replace("\\", "")

        if pl == 1:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                jg = ' '.join(matches)
                return jg

        if pl == 2:
            middle_text = text[start_index + len(start_str):end_index]
            matches = re.findall(start_index1, middle_text)
            if matches:
                new_list = [f'{item}' for item in matches]
                jg = '$$$'.join(new_list)
                return jg

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "/zh/latest-updates/", "type_name": "集多 最新视频🌠"},
                            {"type_id": "/zh/top-rated/", "type_name": "集多 最佳视频🌠"},
                            {"type_id": "/zh/most-popular/", "type_name": "集多 热门影片🌠"}],
                 }

        return result

    def homeVideoContent(self):
        videos = []

        detail = requests.get(url=xurl + "/zh/", headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text

        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="item")

        for vod in soups:

            names = vod.find_all('a')[0]
            name = names['title']

            id = names['href']

            pic = self.extract_middle_text(str(vod), 'data-src="', '"', 0)

            remarks = vod.find('span', class_="duration")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": '集多▶️' + remark
                     }
            videos.append(video)

        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        if page == 1:
            url = f'{xurl}{cid}'

        else:
            url = f'{xurl}{cid}{str(page)}/'

        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text

        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="item")

        for vod in soups:

            names = vod.find_all('a')[0]
            name = names['title']

            id = names['href']

            pic = self.extract_middle_text(str(vod), 'data-src="', '"', 0)

            remarks = vod.find('span', class_="duration")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": '集多▶️' + remark
                    }
            videos.append(video)

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
        global pm
        did = ids[0]
        result = {}
        videos = []
        xianlu = ''
        bofang = ''

        if 'http' not in did:
            did = xurl + did

        res = requests.get(url=did, headers=headerx)
        res.encoding = "utf-8"
        res = res.text
        doc = BeautifulSoup(res, "lxml")

        url = 'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1732707176882/jiduo.txt'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)

        content = '😸集多🎉为您介绍剧情📢' + self.extract_middle_text(res,'<h1>','</h1>', 0)

        if name not in content:
            bofang = Jumps
            xianlu = '1'
        else:
            soups = doc.find_all('video', class_="video-js")

            for vods in soups:

                srcs = vods.find_all('source')

                for vod in srcs:

                    id = vod['src']

                    response = requests.head(id, allow_redirects=False)
                    if response.status_code == 302:
                        redirect_url = response.headers['Location']
                    response = requests.head(redirect_url, allow_redirects=False)
                    if response.status_code == 302:
                        id = response.headers['Location']

                    name = vod['label']

                    bofang = bofang + name + '$' + id + '#'

                bofang = bofang[:-1] + '$$$'

            bofang = bofang[:-3]

            xianlu = '集多专线'

        videos.append({
            "vod_id": did,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = id
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []

        if not page:
            page = '1'
        if page == '1':
            url = f'{xurl}/zh/search/{key}/'

        else:
            url = f'{xurl}/zh/search/{key}/{str(page)}/'

        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text

        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="item")

        for vod in soups:
            
            names = vod.find_all('a')[0]
            name = names['title']

            id = names['href']

            pic = self.extract_middle_text(str(vod), 'data-src="', '"', 0)

            remarks = vod.find('span', class_="duration")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": '集多▶️' + remark
                    }
            videos.append(video)

        result['list'] = videos
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick, pg="1"):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None





