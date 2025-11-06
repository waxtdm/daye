# coding=utf-8
# !/usr/bin/python

"""

作者 丢丢喵 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
from urllib.parse import unquote
from Crypto.Cipher import ARC4
from urllib.parse import quote
from base.spider import Spider
from Crypto.Cipher import AES
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
from io import BytesIO
import urllib.parse
import datetime
import binascii
import requests
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://m.ting15.com"

headerx = {
    'referer': 'https://m.ting15.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
          }

headers = {
    "Host": "oss-links.guoguo.org.cn",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "sec-ch-ua": '"Microsoft Edge";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Dest": "audio",
    "Referer": "https://m.ting15.com/",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Range": "bytes=0-",
    "Accept-Encoding": "identity"
          }

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

    def url_to_base64_in_memory(self, image_url):
        response = requests.get(image_url, headers=headerx)
        response.raise_for_status()
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        return 'data:image/png;base64,' + encoded_string

    def urls_to_base64_in_memory_multithread(self, image_urls, max_workers=10):
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(self.url_to_base64_in_memory, url): url
                for url in image_urls
                            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results[url] = result
                except Exception as exc:
                    print(f'URL {url} generated an exception: {exc}')
                    results[url] = None
        return results

    def _process_video_items(self, soups):
        videos = []
        for item in soups:
            vods = item.find_all('a')
            for vod in vods:
                video = self._parse_video_item(vod)
                if video:
                    videos.append(video)
        return videos

    def _parse_video_item(self, vod):
        name = vod.find('img')['alt']
        id = vod['href']
        pic = vod.find('img')['src']
        pic2=self.url_to_base64_in_memory(pic)
        return {
            "vod_id": id,
            "vod_name": name,
            "vod_pic": pic2
               }

    def homeContent(self, filter):
        result = {"class": []}

        detail = requests.get(url=xurl, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")
        soups = doc.find_all('nav', class_="nav clear")

        for soup in soups:
            vods = soup.find_all('a')

            for vod in vods:

                name = vod.text.strip()

                skip_names = ["首页", "更多↓"]
                if name in skip_names:
                    continue

                id = vod['href']

                result["class"].append({"type_id": id, "type_name":"集多🌠" + name})

        return result

    def homeVideoContent(self):
        videos = []

        detail = requests.get(url=xurl, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="tlist")

        videos = self._process_video_items(soups)

        result = {'list': videos}
        return result

    def categoryContent(self, cid, pg, filter, ext):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}{cid}index{str(page)}.html'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="clist")

        videos = self._process_video_items(soups)

        result = {'list': videos}
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def detailContent(self, ids):
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

        url = 'http://rihou.cc:88/je.json'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)

        content = '集多为您介绍剧情📢' + self.extract_middle_text(res,'<div class="intro">','</a>', 0)
        content = content.replace(' ', '').replace('<p>', '').replace('\r', '').replace('\n', '')

        director = self.extract_middle_text(res,'播音：','<', 0)

        actor = self.extract_middle_text(res,'作者：','<', 0)

        remarks = self.extract_middle_text(res,'状态：','<', 0)

        year = self.extract_middle_text(res,'时间：','<', 0)

        if name not in content:
            bofang = Jumps
            xianlu = '1'
        else:
            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="plist")

            for item in soups:
                vods = item.find_all('a')

            for sou in vods:

                id = sou['href']

                if 'http' not in id:
                    id = xurl + id

                name = sou.text.strip()

                bofang = bofang + name + '$' + id + '#'

            bofang = bofang[:-1]

            xianlu = '听书专线'

        videos.append({
            "vod_id": did,
            "vod_director": director,
            "vod_actor": actor,
            "vod_remarks": remarks,
            "vod_year": year,
            "vod_content": content,
            "vod_play_from": xianlu,
            "vod_play_url": bofang
                     })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):

        detail = requests.get(url=id, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text

        bookId = self.extract_middle_text(res, 'name="_b" content="', '"', 0)
        isPay = self.extract_middle_text(res, 'name="_p" content="', '"', 0)
        page = self.extract_middle_text(res, 'name="_cp" content="', '"', 0)

        payload = {
            'bookId': bookId,
            'isPay': isPay,
            'page': page
                  }

        urlz = 'https://m.ting15.com/?s=api-getneoplay'
        response = requests.post(url=urlz, headers=headerx, data=payload)
        clean_text = response.text.replace('\ufeff', '', 1)
        response_data = json.loads(clean_text)
        audio_url = response_data.get('url', '')

        current_timestamp = int(datetime.datetime.now().timestamp())
        url = f"{audio_url}?v={str(current_timestamp)}"

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headers
        return result

    def searchContentPage(self, key, quick, pg):
        result = {}
        videos = []

        if pg:
            page = int(pg)
        else:
            page = 1

        url = f'{xurl}/?s=ting-search-wd-{key}-p-{str(page)}.html'
        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="clist")

        videos = self._process_video_items(soups)

        result['list'] = videos
        result['page'] = pg
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








