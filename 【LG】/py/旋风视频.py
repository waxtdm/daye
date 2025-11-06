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

xurl = "https://miao101.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

pm = ''

class Spider(Spider):
    global xurl
    global headerx

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
        result = {"class": [{"type_id": "动作片", "type_name": "电影动作片"},
                            {"type_id": "喜剧片", "type_name": "电影喜剧片"},
                            {"type_id": "爱情片", "type_name": "电影爱情片"},
                            {"type_id": "科幻片", "type_name": "电影科幻片"},
                            {"type_id": "奇幻片", "type_name": "电影奇幻片"},
                            {"type_id": "冒险片", "type_name": "电影冒险片"},
                            {"type_id": "恐怖片", "type_name": "电影恐怖片"},
                            {"type_id": "惊悚片", "type_name": "电影惊悚片"},
                            {"type_id": "悬疑片", "type_name": "电影悬疑片"},
                            {"type_id": "犯罪片", "type_name": "电影犯罪片"},
                            {"type_id": "动漫片", "type_name": "电影动漫片"},
                            {"type_id": "剧情片", "type_name": "电影剧情片"},
                            {"type_id": "战争片", "type_name": "电影战争片"},
                            {"type_id": "纪录片", "type_name": "电影纪录片"},
                            {"type_id": "国产剧", "type_name": "剧集国产剧"},
                            {"type_id": "香港剧", "type_name": "剧集香港剧"},
                            {"type_id": "韩国剧", "type_name": "剧集韩国剧"},
                            {"type_id": "欧美剧", "type_name": "剧集欧美剧"},
                            {"type_id": "台湾剧", "type_name": "剧集台湾剧"},
                            {"type_id": "日本剧", "type_name": "剧集日本剧"},
                            {"type_id": "泰国剧", "type_name": "剧集泰国剧"},
                            {"type_id": "大陆综艺", "type_name": "综艺大陆"},
                            {"type_id": "日韩综艺", "type_name": "综艺日韩"},
                            {"type_id": "港台综艺", "type_name": "综艺港台"},
                            {"type_id": "欧美综艺", "type_name": "动漫综艺"},
                            {"type_id": "国产动漫", "type_name": "动漫国产"},
                            {"type_id": "港台动漫", "type_name": "动漫港台"},
                            {"type_id": "日韩动漫", "type_name": "动漫日韩"},
                            {"type_id": "欧美动漫", "type_name": "动漫欧美"},
                            {"type_id": "海外动漫", "type_name": "动漫海外"}],}

        return result

    def homeVideoContent(self):
        videos = []

        try:
            detail = requests.get(url=xurl, headers=headerx)
            detail.encoding = "utf-8"
            res = detail.text

            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="g-2")

            for soup in soups:
                vods = soup.find_all('div', class_="col-md-2")

                for vod in vods:

                    name = vod.find('img')['alt']

                    ids = vod.find('div', class_="cover-wrap")
                    id = ids.find('a')['href']

                    pic = vod.find('img')['src']

                    if 'http' not in pic:
                        pic = xurl + pic

                    remarks = vod.find('span', class_="sub")
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
        except:
            pass

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        payload = {
            "page": str(page),
                  }

        url = f"{xurl}/api/tag/{cid}/load.json"
        response = requests.post(url, headers=headerx, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            js = response_data['videos']
            for vod in js:
                name = vod['Title']

                id = vod['ID']
                id = '/video/' + id

                pic = vod['Cover']

                remark = vod['Sub']

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

        content = '😸集多🎉为您介绍剧情📢' + self.extract_middle_text(res, '<div class="text-break ft14">', '</p>', 0)
        content = content.replace('<br/>', '').replace('<p>', '').replace(' ', '').replace('\u3000', '')

        director = self.extract_middle_text(res, '导演：', '</p>', 0, )

        actor = self.extract_middle_text(res, '演员：', '</p>', 0, )

        doups = doc.find('div', class_="row mb-3")
        update = doups.find('span', class_='sub')
        remarks = update.text.strip()

        year = self.extract_middle_text(res, '年代：', '</p>', 0)

        area = self.extract_middle_text(res, '地区：', '</p>', 0)

        url = 'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1732707176882/jiduo.txt'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)

        if name not in content:
            bofang = Jumps
            xianlu = '1'
        else:
            res1 = self.extract_middle_text(res, 'JSON.parse("', '")', 0)
            res1 = res1.replace('u0022', '"')
            json_data = json.loads(res1)
            js = json_data['headers']

            gl = []

            for vod in js:

                name = vod['Vid']

                xian=vod['Name']
                if any(item in xian for item in gl):
                    continue

                id = vod['ID']

                xianlu = xianlu + xian + '$$$'

                url = f"{xurl}/video/{name}/{id}/1#"
                res2 = requests.get(url=url, headers=headerx)
                res2.encoding = "utf-8"
                res2 = res2.text

                res3 = self.extract_middle_text(res2, 'JSON.parse("', '")', 0)
                res3 = res3.replace('u0022', '"')
                json_data1 = json.loads(res3)
                js1 = json_data1['clips']

                for vod1 in js1:

                    name = vod1[0]

                    parse = vod1[1]

                    bofang = bofang + name + '$' + parse + '#'

                bofang = bofang[:-1] + '$$$'

            xianlu=xianlu[:-3]

            bofang=bofang[:-3]

        videos.append({
            "vod_id": did,
            "vod_director": director,
            "vod_actor": actor,
            "vod_remarks": remarks,
            "vod_year": year,
            "vod_area": area,
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

        url = f'{xurl}/search?q={key}'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="g-2")

        for soup in soups:
            vods = soup.find_all('div', class_="col-md-2")

            for vod in vods:

                name = vod.find('img')['alt']

                ids = vod.find('div', class_="cover-wrap")
                id = ids.find('a')['href']

                pic = vod.find('img')['src']

                if 'http' not in pic:
                    pic = xurl + pic

                remarks = vod.find('span', class_="sub")
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




