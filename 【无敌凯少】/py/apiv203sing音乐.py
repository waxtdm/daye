# coding=utf-8
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
from datetime import datetime
from bs4 import BeautifulSoup
from base64 import b64decode
import urllib.request
import urllib.parse
import datetime
import binascii
import requests
import hashlib
import base64
import html
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://5sing.kugou.com"

xurl1 = "https://5sservice.kugou.com"

headerx = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
          }

class Spider(Spider):

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

    def fetch_home_classes(self):
        try:
            detail = requests.get(url=f"{xurl}/yc/list?t=2&l=", headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            return doc
        except Exception:
            return None

    def parse_home_classes(self, doc):
        result = {"class": []}
        if not doc:
            return result
        try:
            soups = doc.find_all('dl', class_="song_sort")
            for soup in soups:
                vods = soup.find_all('dd')
                if len(vods) < 2:
                    continue
                links = vods[1].find_all('a')
                for link in links:
                    name = link.get('title')
                    if not name:
                        continue
                    skip_names = ["全部"]
                    if name in skip_names:
                        continue
                    id = link.get('href')
                    if not id:
                        continue
                    result["class"].append({"type_id": id, "type_name": name})
        except Exception:
            pass
        return result

    def homeContent(self, filter):
        doc = self.fetch_home_classes()
        return self.parse_home_classes(doc)

    def homeVideoContent(self):
        pass

    def fetch_category_data(self, cid, page):
        try:
            url = f'{xurl}{cid}&p={str(page)}'
            detail = requests.get(url=url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            return doc
        except Exception:
            return None

    def parse_category_videos(self, doc):
        videos = []
        if not doc:
            return videos
        try:
            soups = doc.find_all('div', class_="lists")
            for soup in soups:
                vods = soup.find_all('dl')
                for vod in vods:
                    try:
                        names = vod.find_all('dd', class_="l_info")
                        name = ""
                        id = ""
                        for n in names:
                            h3_link = n.find('h3').find('a') if n.find('h3') else None
                            if h3_link:
                                name = h3_link.get_text()
                                id = h3_link.get('href')
                                break
                        img_tag = vod.find('img')
                        if not img_tag:
                            continue
                        pic = img_tag.get('src', '').replace('48x48', '256x256')
                        remark = img_tag.get('alt', '')
                        if id and name:
                            video = {
                                "vod_id": id,
                                "vod_name": name,
                                "vod_pic": pic,
                                "vod_remarks": remark
                            }
                            videos.append(video)
                    except Exception:
                        continue
        except Exception:
            pass
        return videos

    def build_category_result(self, videos, pg):
        result = {
            'list': videos,
            'page': pg,
            'pagecount': 9999,
            'limit': 90,
            'total': 999999
                 }
        return result

    def categoryContent(self, cid, pg, filter, ext):
        try:
            page = int(pg) if pg else 1
        except ValueError:
            page = 1
        doc = self.fetch_category_data(cid, page)
        videos = self.parse_category_videos(doc)
        return self.build_category_result(videos, pg)

    def fetch_detail_data(self, did):
        try:
            if 'http' not in did:
                did = xurl + did
            detail = requests.get(url=did, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            doc = BeautifulSoup(res, "lxml")
            return doc, did
        except Exception:
            return None, did

    def parse_detail_content(self, doc, did):
        videos = []
        if not doc:
            return videos
        try:
            content_div = doc.find('div', class_="lrc_info_clip lrc-tab-content")
            if content_div:
                content = '为您介绍剧情' + content_div.text.strip()
            else:
                content = '为您介绍剧情'
            videos.append({
                "vod_id": did,
                "vod_content": content,
                "vod_play_from": "音乐专线",
                "vod_play_url": did
                          })
        except Exception:
            pass
        return videos

    def build_detail_result(self, videos):
        result = {}
        if videos:
            result['list'] = videos
        else:
            result['list'] = []
        return result

    def detailContent(self, ids):
        did = ids[0] if ids else ""
        if not did:
            return {'list': []}
        doc, did = self.fetch_detail_data(did)
        videos = self.parse_detail_content(doc, did)
        return self.build_detail_result(videos)

    def get_current_timestamp(self) -> int:
        return int(time.time() * 1000)

    def prepare_kugou_params(self, songid: str, current_timestamp: int) -> dict:
        return {
            'appid': '2918',
            'clientver': '1000',
            'mid': 'cf03967b54a2e0649ec26e8fa30935f5',
            'uuid': 'cf03967b54a2e0649ec26e8fa30935f5',
            'dfid': '0jH1Q52gH24w3ejVGJ4SNq8I',
            'songid': songid,
            'songtype': 'yc',
            'version': '6.6.72',
            'clienttime': str(current_timestamp)
               }

    def clean_params_and_key(self, params_dict: dict, app_key: str) -> tuple:
        try:
            cleaned_params = {k: str(v).strip() for k, v in params_dict.items() if v is not None}
            clean_app_key = app_key.strip() if app_key else ""
            return cleaned_params, clean_app_key
        except Exception:
            return {}, ""

    def build_signature_string(self, cleaned_params: dict, clean_app_key: str) -> str:
        try:
            sorted_keys = sorted(cleaned_params.keys())
            string_parts = [clean_app_key]
            for key in sorted_keys:
                string_parts.append(f"{key}={cleaned_params[key]}")
            string_parts.append(clean_app_key)
            return "".join(string_parts)
        except Exception:
            return ""

    def calculate_md5_signature(self, raw_string: str) -> str:
        try:
            return hashlib.md5(raw_string.encode('utf-8')).hexdigest()
        except Exception:
            return ""

    def generate_kugou_signature(self, params_dict: dict, app_key: str) -> tuple:
        cleaned_params, clean_app_key = self.clean_params_and_key(params_dict, app_key)
        if not cleaned_params or not clean_app_key:
            return "", ""
        raw_string = self.build_signature_string(cleaned_params, clean_app_key)
        if not raw_string:
            return "", ""
        calculated_signature = self.calculate_md5_signature(raw_string)
        return calculated_signature, raw_string

    def generate_kugou_signature_only(self, songid: str, app_key: str) -> str:
        if not songid or not app_key:
            return ""
        current_timestamp = self.get_current_timestamp()
        params = self.prepare_kugou_params(songid, current_timestamp)
        signature, _ = self.generate_kugou_signature(params, app_key)
        return signature

    def fetch_page_content(self, url):
        try:
            detail = requests.get(url=url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            return detail.text
        except Exception:
            return ""

    def extract_song_info(self, content):
        try:
            SongID = self.extract_middle_text(content, 'var SongID     = ', ';', 0)
            appkey = self.extract_middle_text(content, "appkey: '", "'", 0)
            return SongID, appkey
        except Exception:
            return "", ""

    def build_api_url(self, SongID, appkey):
        try:
            current_timestamp = int(time.time() * 1000)
            signature = self.generate_kugou_signature_only(SongID, appkey)
            if not signature:
                return ""
            return f'{xurl1}/song/getsongurl?appid=2918&clientver=1000&mid=cf03967b54a2e0649ec26e8fa30935f5&uuid=cf03967b54a2e0649ec26e8fa30935f5&dfid=0jH1Q52gH24w3ejVGJ4SNq8I&songid={SongID}&songtype=yc&version=6.6.72&clienttime={str(current_timestamp)}&signature={signature}'
        except Exception:
            return ""

    def fetch_song_data(self, api_url):
        try:
            detail = requests.get(url=api_url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            return detail.json()
        except Exception:
            return {}

    def extract_audio_url(self, data):
        try:
            song_data = data.get("data", {})
            return (
                    song_data.get("hqurl_backup") or
                    song_data.get("lqurl_backup") or
                    song_data.get("squrl_backup") or
                    ""
                   )
        except Exception:
            return ""

    def build_player_result(self, url):
        result = {
            "parse": 0,
            "playUrl": '',
            "url": url,
            "header": headerx
                 }
        return result

    def playerContent(self, flag, id, vipFlags):
        content = self.fetch_page_content(id)
        if not content:
            return self.build_player_result("")
        SongID, appkey = self.extract_song_info(content)
        if not SongID or not appkey:
            return self.build_player_result("")
        api_url = self.build_api_url(SongID, appkey)
        if not api_url:
            return self.build_player_result("")
        data = self.fetch_song_data(api_url)
        if not data:
            return self.build_player_result("")
        url = self.extract_audio_url(data)
        return self.build_player_result(url)

    def build_search_url(self, key, page):
        return f'http://search.5sing.kugou.com/home/json?keyword={key}&sort=1&page={str(page)}&filter=1&type=0'

    def fetch_search_data(self, url):
        try:
            detail = requests.get(url=url, headers=headerx, timeout=10)
            detail.raise_for_status()
            detail.encoding = "utf-8"
            res = detail.text
            return json.loads(res)
        except Exception:
            return {}

    def clean_song_name(self, song_name):
        try:
            if not song_name:
                return ""
            song_name = re.sub(r'<em[^>]*>', '', song_name)
            song_name = song_name.replace('</em>', '').strip()
            return song_name
        except Exception:
            return ""

    def parse_search_item(self, item):
        try:
            song_name = item.get('songName', '')
            cleaned_name = self.clean_song_name(song_name)
            song_url = item.get('songurl', '')
            nick_name = item.get('nickName', '')
            pic = "https://ts3.tc.mm.bing.net/th/id/OIP-C.PByoegkaKko9hVqEvy-ScAHaFj?cb=ucfimg2ucfimg=1&rs=1&pid=ImgDetMain&o=7&rm=3"
            if not song_url:
                return None
            return {
                "vod_id": song_url,
                "vod_name": cleaned_name,
                "vod_pic": pic,
                "vod_remarks": nick_name
                   }
        except Exception:
            return None

    def parse_search_results(self, data):
        videos = []
        try:
            if not isinstance(data, dict) or 'list' not in data:
                return videos
            for item in data['list']:
                video = self.parse_search_item(item)
                if video:
                    videos.append(video)
        except Exception:
            pass
        return videos

    def build_search_result(self, videos, pg):
        result = {
            'list': videos,
            'page': pg,
            'pagecount': 9999,
            'limit': 90,
            'total': 999999
                 }
        return result

    def searchContentPage(self, key, quick, pg):
        try:
            page = int(pg) if pg else 1
        except ValueError:
            page = 1
        if not key:
            return self.build_search_result([], pg)
        url = self.build_search_url(key, page)
        data = self.fetch_search_data(url)
        videos = self.parse_search_results(data)
        return self.build_search_result(videos, pg)

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





