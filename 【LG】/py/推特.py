# coding = utf-8
# !/usr/bin/python

"""

作者 丢丢喵 🚓 内容均从互联网收集而来 仅供交流学习使用 版权归原创者所有 如侵犯了您的权益 请通知作者 将及时删除侵权内容
                    ====================Diudiumiao====================

"""

from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
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

xurl = "https://d1frehx187fm2c.cloudfront.net"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; V1938T Build/PQ3A.190705.08211809; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36;SuiRui/twitter/ver=1.3.4',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'deviceId': 'b77f1bda8515cf6149741ba2400bf864',
    't': '1738511086009',
    's': '07de104ba7337dfc7b9fb0d882f291ef',
    'aut': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNTQwNTU3NSIsImlzcyI6IiIsImlhdCI6MTczMjk5NTUyNywibmJmIjoxNzMyOTk1NTI3LCJleHAiOjE4OTA2NzU1Mjd9.-AWh492Dx3s0nwEzNuQ-TtqUOi56LCC7kfL38fWcCpM',
    'Host': 'd1frehx187fm2c.cloudfront.net',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip, deflate'
           }

headerz = {
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; V1938T Build/PQ3A.190705.08211809; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36;SuiRui/twitter/ver=1.3.4',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'deviceId': 'b77f1bda8515cf6149741ba2400bf864',
    't': '1738522342567',
    's': 'ae0bc3d83dfd1e061dd1e06c624b232b',
    'aut': 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxNTQwNTU3NSIsImlzcyI6IiIsImlhdCI6MTczMjk5NTUyNywibmJmIjoxNzMyOTk1NTI3LCJleHAiOjE4OTA2NzU1Mjd9.-AWh492Dx3s0nwEzNuQ-TtqUOi56LCC7kfL38fWcCpM',
    'Host': 'api.pdcqllfomw.work',
    'Connection': 'Keep-Alive',
    'Accept-Encoding': 'gzip, deflate'
          }

pm = ''

class Spider(Spider):
    global xurl
    global headerx
    global headers
    global headerz

    def getName(self):
        return "首页"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        result = {}
        result = {"class": [{"type_id": "2", "type_name": "国产🌠"},
                            {"type_id": "3", "type_name": "乱伦🌠"},
                            {"type_id": "4", "type_name": "短视🌠"},
                            {"type_id": "5", "type_name": "动漫🌠"},
                            {"type_id": "6", "type_name": "重口🌠"},
                            {"type_id": "7", "type_name": "传媒🌠"},
                            {"type_id": "8", "type_name": "男同🌠"}]
                  }

        return result

    def decrypt(self, encrypted_data):
        key_base64 = "SmhiR2NpT2lKSVV6STFOaQ=="
        iv_base64 = "SmhiR2NpT2lKSVV6STFOaQ=="
        key_bytes = base64.b64decode(key_base64)
        iv_bytes = base64.b64decode(iv_base64)
        ciphertext_base64 = encrypted_data
        ciphertext_bytes = base64.b64decode(ciphertext_base64)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted_bytes = unpad(cipher.decrypt(ciphertext_bytes), AES.block_size)
        decrypted_text = decrypted_bytes.decode('utf-8')
        return decrypted_text

    def homeVideoContent(self):
        videos = []
        payload = {}

        url = xurl + "/api/video/queryVideoByClassifyId?pageSize=20&page=1&classifyId=1&sortType=1"
        detail = requests.get(url, headers=headers, verify=False)
        response_data = detail.json()
        data = response_data.get('encData')
        encrypted_data = data
        detail = self.decrypt(encrypted_data)
        detail = json.loads(detail)

        gl = ['视频流出，身材诱人。点赞到5w出下一期。']

        js = detail['data']
        for vod in js:
            name = vod['title']
            if any(item in name for item in gl):
                continue

            id = vod['videoId']

            img = 'https://dg2ordyr4k5v3.cloudfront.net/' + vod['coverImg'][0]

            remark = vod['nickName']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": self.getProxyUrl() + '&url=' + img,
                "vod_remarks": remark
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
            url = f'{xurl}/api/video/queryVideoByClassifyId?pageSize=20&page=1&classifyId={cid}&sortType=1'

        else:
            url = f'{xurl}/api/video/queryVideoByClassifyId?pageSize=20&page={str(page)}&classifyId={cid}&sortType=1'

        detail = requests.get(url, headers=headers, verify=False)
        response_data = detail.json()
        data = response_data.get('encData')
        encrypted_data = data
        detail = self.decrypt(encrypted_data)
        detail = json.loads(detail)

        js = detail['data']
        for vod in js:
            name = vod['title']

            id = vod['videoId']

            img = 'https://dg2ordyr4k5v3.cloudfront.net/' + vod['coverImg'][0]

            remark = vod['nickName']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": self.getProxyUrl() + '&url=' + img,
                "vod_remarks": remark
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

        url = xurl + "/api/video/can/watch?videoId=" + did
        detail = requests.get(url, headers=headers, verify=False)
        response_data = detail.json()
        data = response_data.get('encData')
        encrypted_data = data
        detail = self.decrypt(encrypted_data)
        detail = json.loads(detail)

        authKey = detail['authKey']

        videoUrl = detail['videoUrl']

        parse = xurl + "/api/m3u8/decode/authPath?auth_key=" + authKey + '&path=' + videoUrl

        videos.append({
            "vod_id": did,
            "vod_actor": '集多和他的朋友们',
            "vod_director": '集多',
            "vod_play_from": '集多专线',
            "vod_play_url": parse
                      })

        result['list'] = videos
        return result

    def playerContent(self, flag, id, vipFlags):
        parts = id.split("http")

        xiutan = 1

        if xiutan == 1:
            if len(parts) > 1:
                before_https, after_https = parts[0], 'http' + parts[1]
            result = {}
            result["parse"] = xiutan
            result["playUrl"] = ''
            result["url"] = after_https
            result["header"] = headerx
            return result

    def searchContentPage(self, key, quick, page):
        result = {}
        videos = []

        if not page:
            page = '1'
        if page == '1':
            url = f'https://api.wcyfhknomg.work/api/search/keyWord?pageSize=20&page=1&searchWord={key}&searchType=1'

        else:
            url = f'https://api.wcyfhknomg.work/api/search/keyWord?pageSize=20&page={str(page)}&searchWord={key}&searchType=1'

        detail = requests.get(url, headers=headerz, verify=False)
        response_data = detail.json()
        data = response_data.get('encData')
        encrypted_data = data
        detail = self.decrypt(encrypted_data)
        detail = json.loads(detail)

        js = detail['videoList']
        for vod in js:
            name = vod['title']

            id = vod['videoId']

            img = 'https://dg2ordyr4k5v3.cloudfront.net/' + vod['coverImg'][0]

            remark = vod['nickName']

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": self.getProxyUrl() + '&url=' + img,
                "vod_remarks": remark
                    }
            videos.append(video)

        result = {'list': videos}
        result['page'] = page
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        return result

    def searchContent(self, key, quick):
        return self.searchContentPage(key, quick, '1')

    def localProxy(self, param):
        return self.imgs(param)

    def imgs(self, param):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; V1938T Build/PQ3A.190705.08211809; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Safari/537.36;SuiRui/twitter/ver=1.3.4'}
        url = param['url']
        type = url.split('.')[-1].split('_')[0]
        data = self.fetch(url, headers=headers).content
        bdata = self.img(data, 100, '2020-zq3-888')
        return [200, f'image/{type}', bdata]

    def img(self, data: bytes, length: int, key: str):
        GIF = b'\x47\x49\x46'
        JPG = b'\xFF\xD8\xFF'
        PNG = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

        def is_dont_need_decode_for_gif(data):
            return len(data) > 2 and data[:3] == GIF

        def is_dont_need_decode_for_jpg(data):
            return len(data) > 7 and data[:3] == JPG

        def is_dont_need_decode_for_png(data):
            return len(data) > 7 and data[1:8] == PNG[1:8]

        if is_dont_need_decode_for_png(data):
            return data
        elif is_dont_need_decode_for_gif(data):
            return data
        elif is_dont_need_decode_for_jpg(data):
            return data
        else:
            key_bytes = key.encode('utf-8')
            result = bytearray(data)
            for i in range(length):
                result[i] ^= key_bytes[i % len(key_bytes)]
            return bytes(result)




