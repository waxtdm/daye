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
import base64
import json
import time
import sys
import re
import os

sys.path.append('..')

xurl = "https://www.lmm97.com" #发布站 https://i.qg50.com

headerx = {
    'User-Agent': 'Mozilla/5.0 (Linux; U; Android 8.0.0; zh-cn; Mi Note 2 Build/OPR1.170623.032) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/61.0.3163.128 Mobile Safari/537.36 XiaoMi/MiuiBrowser/10.1.1'
          }

headers = {
    'Host': 'yun.366day.site',
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Storage-Access': 'active',
    'Referer': 'https://www.lmm97.com/',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Accept-Encoding': 'gzip, deflate'
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

    def decrypt_data(self, encrypted_data_b64, aes_key_str="ejjooopppqqqrwww", aes_iv_str="1348987635684651"):
        key_bytes = aes_key_str.encode('utf-8')
        iv_bytes = aes_iv_str.encode('utf-8')
        encrypted_bytes = base64.b64decode(encrypted_data_b64)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted_raw_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        output_string = decrypted_raw_bytes.decode('utf-8')
        return output_string

    def extract_dynamic_keyyy_parts(self, html_content):
        keyyy_concat_pattern = re.compile(
            r'"keyyy":\s*\'\'\+([a-zA-Z0-9_]+)\+([a-zA-Z0-9_]+)\+([a-zA-Z0-9_]+)\+([a-zA-Z0-9_]+)\+\'\''
                                          )
        keyyy_match = keyyy_concat_pattern.search(html_content)
        if not keyyy_match:
            return None
        dynamic_var_names = [keyyy_match.group(i) for i in range(1, 5)]
        extracted_values = {}
        for name in dynamic_var_names:
            var_declaration_pattern = re.compile(r'var\s+' + re.escape(name) + r'="([^"]*)";')
            value_match = var_declaration_pattern.search(html_content)
            if value_match:
                extracted_values[name] = value_match.group(1)
            else:
                extracted_values[name] = None
        if all(extracted_values[name] is not None for name in dynamic_var_names):
            final_keyyy = "".join(extracted_values[name] for name in dynamic_var_names)
            return final_keyyy
        else:
            return None

    def homeContent(self, filter):
        result = {"class": []}

        detail = requests.get(url=xurl, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="row gutter-20 pb-3")

        for soup in soups:
            vods = soup.find_all('a')

            for vod in vods:

                name = vod.text.strip()

                id = vod['href']

                result["class"].append({"type_id": id, "type_name": name})

        return result

    def homeVideoContent(self):
        videos = []

        detail = requests.get(url=xurl, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="owl-carousel owl-theme-jable")

        for soup in soups:
            vods = soup.find_all('div', class_="item")

            for vod in vods:

                names = vod.find('h6', class_="title")
                name = names.text.strip()

                id = names.find('a')['href']

                pic = vod.find('img')['data-src']

                remarks = vod.find('span', class_="label")
                remark = remarks.text.strip()

                video = {
                    "vod_id": id,
                    "vod_name": name,
                    "vod_pic": pic,
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

        fenge = cid.split(".html")

        if page == 1:
            url = f'{xurl}{cid}'

        else:
            url = f'{xurl}{fenge[0]}_{str(page)}.html'

        detail = requests.get(url=url, headers=headerx)
        detail.encoding = "utf-8"
        res = detail.text
        doc = BeautifulSoup(res, "lxml")

        soups = doc.find_all('div', class_="col-6 col-sm-4 col-lg-3")

        for vod in soups:

            names = vod.find('h6', class_="title")
            name = names.text.strip()

            id = names.find('a')['href']

            pic = vod.find('img')['data-src']

            remarks = vod.find('span', class_="label")
            remark = remarks.text.strip()

            video = {
                "vod_id": id,
                "vod_name": name,
                "vod_pic": pic,
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

        url = 'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1732697392729/didiu.txt'
        response = requests.get(url)
        response.encoding = 'utf-8'
        code = response.text
        name = self.extract_middle_text(code, "s1='", "'", 0)
        Jumps = self.extract_middle_text(code, "s2='", "'", 0)

        content = '😸丢丢为您介绍剧情📢' + self.extract_middle_text(res,'<div class="video-info-item video-info-content">','</div>', 0)
        content = content.replace('&quot;', '').replace('\n', '').replace('<span class="content-text none">', '').replace('</span>', '').replace(' ', '')

        director = self.extract_middle_text(res, '导演：', '</div>',1,'<span>(.*?)</span>')

        actor = self.extract_middle_text(res, '主演：', '</div>',1,'<span>(.*?)</span>')

        remarks = self.extract_middle_text(res, '集数：', 'div>', 1,'>(.*?)</')

        year = self.extract_middle_text(res, '上映：', 'div>', 1,'>(.*?)</')

        area = self.extract_middle_text(res, '</div><div class="tag-link">', '</div>', 1,'<span>(.*?)</span>')

        if name not in content:
            bofang = Jumps
            xianlu = '1'
        else:
            doc = BeautifulSoup(res, "lxml")

            soups = doc.find_all('div', class_="module-tab-content")

            for item in soups:
                vods = item.find_all('div')

                for sou in vods:

                    name = sou.text.strip()

                    if name:
                        xianlu = xianlu + name + '$$$'

                if xianlu.endswith('$$$'):
                    xianlu = xianlu[:-3]

            if xianlu:
                lines = xianlu.split('$$$')

                counts = {}

                for line in lines:
                    counts[line] = counts.get(line, 0) + 1

                occurrences = {}

                processed_lines = []

                for line in lines:
                    occurrences[line] = occurrences.get(line, 0) + 1
                    if counts[line] > 1 and occurrences[line] > 1:
                        processed_lines.append(f"{line}{occurrences[line]}")
                    else:
                        processed_lines.append(line)

                xianlu = '$$$'.join(processed_lines)

            soups = doc.find_all('div', class_="scroll-content")

            for item in soups:
                vods = item.find_all('a')

                for sou in vods:

                    id = sou['href']
                    if 'http' not in id:
                        id = xurl + id

                    name = sou.text.strip()

                    bofang = bofang + name + '$' + id + '#'

                bofang = bofang[:-1] + '$$$'

            bofang = bofang[:-3]

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

        res = requests.get(url=id, headers=headerx)
        res.encoding = "utf-8"
        res = res.text
        res = self.extract_middle_text(res, '<div class="img-box bofang_box">', '</div>', 0)
        url1 = self.extract_middle_text(res, '"url":"', '"', 0)
         
        if '1071' in url1:
            url2 = f"https://yun.366day.site/yunbox/?type=vxdev&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/vxdev.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif '1075' in url1:
            url2 = f"https://yun.366day.site/yunbox/?type=vxdev&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/api.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif '50154' in url1:
            url2 = f"https://yun.366day.site/yunbox/?type=vxcd&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/api.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 't=DU' in url1:
            url1 = url1.replace('&t=DU', '')
            url2 = f"https://yun.366day.site/yunbox/?type=DU&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/ducloud.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 't=yhxg' in url1:
            url1 = url1.replace('&t=yhxg', '')
            url2 = f"https://yun.366day.site/404.php?host=4khls&vid={url1}&t=yhxg&referer={id}"
            response = requests.get(url=url2, headers=headers, allow_redirects=False)
            url3 = response.headers.get('Location')

            res = requests.get(url=url3, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                       }

            urlz = 'https://yun.366day.site/yunbox/yhxg.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 't=bilibil' in url1:
            url1 = url1.replace('&t=bilibil', '')
            url2 = f"https://yun.366day.site/yunbox/?type=bilibil&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/bilibil.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 't=cloudvideo' in url1:
            url1 = url1.replace('&t=cloudvideo', '')
            url2 = f"https://yun.366day.site/yunbox/?type=cloudvideo&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/cloudvideo.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 'm3u8' in url1:
            url2 = f"https://yun.366day.site/mp4hls/?type=hls&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/mp4hls/api.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        elif 't=dxig' in url1:
            url1 = url1.replace('&t=dxig', '')
            url2 = f"https://yun.366day.site/acfun58.php?id={url1}&t=dxig&referer={id}"
            response = requests.get(url=url2, headers=headers, allow_redirects=False)
            url3 = response.headers.get('Location')

            res = requests.get(url=url3, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            vid = self.extract_middle_text(res, '"vid": "', '"', 0)

            keyyy = self.extract_dynamic_keyyy_parts(res)

            type = self.extract_middle_text(res, '"type": "', '"', 0)

            token = self.extract_middle_text(res, '"token":"', '"', 0)

            token1 = self.extract_middle_text(res, '"token1":"', '"', 0)

            token2 = self.extract_middle_text(res, '"token2":"', '"', 0)

            token3 = self.extract_middle_text(res, '"token3":"', '"', 0)

            t = self.extract_middle_text(res, '"t":"', '"', 0)

            ti = self.extract_middle_text(res, '"ti":', '"', 0)

            payload = {
                'vid': vid,
                'keyyy': keyyy,
                'type': type,
                'vt': '',
                'token': token,
                'token1': token1,
                'token2': token2,
                'token3': token3,
                't': t,
                'ti': ti
                      }

            urlz = 'https://yun.366day.site/kuvips/zuik.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')
            url = unquote(url)

        elif 't=MDA' in url1:
            url2 = f"https://yun.366day.site/404.php?host=4khls&vid={url1}&referer={id}"
            response = requests.get(url=url2, headers=headers, allow_redirects=False)
            url3 = response.headers.get('Location')

            res = requests.get(url=url3, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            urlz = 'https://yun.366day.site/yunbox/mdacloud.php'
            response = requests.post(url=urlz, headers=headers, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        else:
            url2 = f"https://yun.366day.site/189tv/?type=xgsp&vid={url1}&referer={id}"
            res = requests.get(url=url2, headers=headers)
            res.encoding = "utf-8"
            res = res.text

            token = self.extract_middle_text(res, 'var token = "', '"', 0)
            token = self.decrypt_data(token)

            vid = self.extract_middle_text(res, 'var vid = "', '"', 0)

            t = self.extract_middle_text(res, 'var t = "', '"', 0)

            payload = {
                'vid': vid,
                't': t,
                'token': token,
                'act': '0',
                'play': '1'
                      }

            headerz = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1",
                "Referer": f"https://yun.366day.site/yunbox/?type=migu&vid={vid}&referer={id}"
                      }

            urlz = 'https://yun.366day.site/yunbox/migu.php'
            response = requests.post(url=urlz, headers=headerz, data=payload)
            response_data = response.json()
            url = response_data.get('url', '')

        result = {}
        result["parse"] = 0
        result["playUrl"] = ''
        result["url"] = url
        result["header"] = headerx
        return result

    def searchContentPage(self, key, quick, pg): 
        pass

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








