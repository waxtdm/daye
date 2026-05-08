# coding=utf-8
# !/usr/bin/python
import time
import requests
import json
from urllib.parse import quote, unquote
import re
import base64
from bs4 import BeautifulSoup
from base.spider import Spider


class Spider(Spider):
    def __init__(self):
        self.meta = {
            "key": "华夏",
            "name": "直播",
            "type": 4,
            "api": "/video/华夏",
            "searchable": 1,
            "quickSearch": 1,
            "changeable": 0
        }
        self.http = requests.Session()
        self.http.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://tv.cctv.com/"
        })

    def getName(self):
        return self.meta["name"]

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return {
            "class": [
                {"type_id": "4K", "type_name": "4K"},
                {"type_id": "栏目大全", "type_name": "栏目大全"},
                {"type_id": "电视剧", "type_name": "电视剧"},
                {"type_id": "纪录片", "type_name": "纪录片"},
                {"type_id": "特别节目", "type_name": "特别节目"},
                {"type_id": "动画片", "type_name": "动画片"}
            ],
            "list": []
        }

    def homeVideoContent(self):
        pass

    def _category(self, cid, pg):
        pg = pg or 1
        url = ""
        pagecount = 20 if cid == "栏目大全" else 24

        if cid == "动画片":
            url = f"https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955899450127&area=&sc=&fc={quote(cid)}&letter=&p={pg}&n={pagecount}&serviceId=tvcctv&topv=1&t=json"
        elif cid == "纪录片":
            url = f"https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955924871139&fc={quote(cid)}&channel=&sc=&year=&letter=&p={pg}&n={pagecount}&serviceId=tvcctv&topv=1&t=json"
        elif cid == "电视剧":
            url = f"https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955853485115&area=&sc=&fc={quote(cid)}&year=&letter=&p={pg}&n={pagecount}&serviceId=tvcctv&topv=1&t=json"
        elif cid == "特别节目":
            url = f"https://api.cntv.cn/list/getVideoAlbumList?channelid=CHAL1460955953877151&channel=&sc=&fc={quote(cid)}&bigday=&letter=&p={pg}&n={pagecount}&serviceId=tvcctv&topv=1&t=json"
        elif cid == "栏目大全":
            url = f"https://api.cntv.cn/lanmu/columnSearch?&fl=&fc=&cid=&p={pg}&n={pagecount}&serviceId=tvcctv&t=json&cb=ko"
        elif cid == "4K":
            url = f"https://api.cntv.cn/NewVideo/getLastVideoList4K?serviceId=cctv4k&cid=CHAL1558416868484111&p={pg}&n={pagecount}&t=jsonp&cb=Callback"

        try:
            response = self.http.get(url)
            videos = []

            if cid == "4K":
                json_str = response.text
                if json_str.startswith('Callback(') and json_str.endswith(');'):
                    json_str = json_str[9:-2]

                json_data = json.loads(json_str)
                data = json_data.get("data", {})

                if data and data.get("list"):
                    videos = [{
                        "vod_id": f"{cid}###{item['title']}###{item['last_video']['url']}###{item['image']}###{item['id']}###{item['last_video']['title']}###{item.get('sc', '')}###{item.get('fc', '')}",
                        "vod_name": item["title"],
                        "vod_pic": item["image"],
                        "vod_remarks": item["last_video"].get("title", "")
                    } for item in data["list"]]

            elif cid == "栏目大全":
                html_text = response.text
                index = html_text.rfind(');')
                if index > -1:
                    html_text = html_text[3:index]
                    data = json.loads(html_text).get("response", {})
                    if data and data.get("docs"):
                        videos = [{
                            "vod_id": f"{cid}###{vod['column_name']}###{vod['column_website']}###{vod['column_logo']}###{vod.get('lastVIDE', {}).get('videoSharedCode', '')}###{vod['column_playdate']}###{vod['column_brief']}",
                            "vod_name": vod["column_name"],
                            "vod_pic": vod["column_logo"],
                            "vod_remarks": vod.get("column_playdate", "")
                        } for vod in data["docs"]]

            else:
                data = response.json().get("data", {})
                if data and data.get("list"):
                    videos = [{
                        "vod_id": f"{cid}###{vod['title']}###{vod['url']}###{vod['image']}###{vod['id']}###{vod.get('year', '')}###{vod.get('actors', '')}###{vod.get('brief', '')}",
                        "vod_name": vod["title"],
                        "vod_pic": vod["image"],
                        "vod_remarks": vod.get("year", "")
                    } for vod in data["list"]]

            return {
                "list": videos,
                "page": int(pg),
                "pagecount": 9999 if len(videos) >= pagecount else int(pg),
                "limit": 90,
                "total": 999999
            }

        except Exception as e:
            print(f"Category error: {e}")
            return {"list": [], "page": 1, "pagecount": 1}

    def categoryContent(self, cid, pg, filter, extend):
        return self._category(cid, pg)

    def _detail(self, vid):
        parts = vid.split("###")
        tid = parts[0]
        title = parts[1]
        last_video = parts[2]
        logo = parts[3]
        guid = parts[4]

        # Handle animation category specially
        if tid == "动画片":
            try:
                res = self.http.get(
                    f"https://api.cntv.cn/NewVideo/getVideoListByAlbumIdNew?id={guid}&serviceId=tvcctv&p=1&n=100")
                video_list = []
                if res.json().get("data", {}).get("list"):
                    video_list = [f"{item['title']}${item['guid']}" for item in res.json()["data"]["list"]]

                return {
                    "list": [{
                        "vod_id": vid,
                        "vod_name": title,
                        "vod_pic": logo,
                        "type_name": tid,
                        "vod_year": parts[5] or "",
                        "vod_actor": parts[6] or "",
                        "vod_content": parts[7] or "",
                        "vod_play_from": "华夏动画",
                        "vod_play_url": "#".join(video_list)
                    }]
                }
            except Exception as e:
                print(f"动画片详情获取失败: {e}")
                return {
                    "list": [{
                        "vod_id": vid,
                        "vod_name": title,
                        "vod_pic": logo,
                        "type_name": tid,
                        "vod_year": parts[5] or "",
                        "vod_actor": parts[6] or "",
                        "vod_content": parts[7] or "",
                        "vod_play_from": "华夏",
                        "vod_play_url": f"{title}${last_video}"
                    }]
                }

        # Other categories keep original logic
        if tid == "搜索":
            uploadtime = parts[5]
            channel = parts[6]

            return {
                "list": [{
                    "vod_id": vid,
                    "vod_name": title,
                    "vod_pic": logo,
                    "type_name": channel,
                    "vod_year": uploadtime,
                    "vod_actor": "",
                    "vod_content": "",
                    "vod_play_from": "华夏",
                    "vod_play_url": f"{title}${last_video}"
                }]
            }

        vod_year = parts[5] or ""
        actors = parts[6] or ""
        brief = parts[7] or ""

        if tid == "栏目大全":
            vod_year = parts[5] or ""
            brief = parts[6] or ""
        else:
            vod_year = parts[5] or ""
            actors = parts[6] or ""
            brief = parts[7] or ""

        video_list = []
        from_id = "CCTV"

        try:
            if tid == "栏目大全":
                response = self.http.get(f"https://api.cntv.cn/video/videoinfoByGuid?guid={guid}&serviceId=tvcctv")
                topic_id = response.json().get("ctid")
                res = self.http.get(
                    f"https://api.cntv.cn/NewVideo/getVideoListByColumn?id={topic_id}&d=&p=1&n=100&sort=desc&mode=0&serviceId=tvcctv&t=json")
                if res.json().get("data", {}).get("list"):
                    video_list = [f"{item['title']}${item['guid']}" for item in res.json()["data"]["list"]]
            elif tid == "4K":
                vsetid = guid
                url = f"https://api.cntv.cn/NewVideo/getVideoListByAlbumIdNew?id={vsetid}&serviceId=tvcctv&p=1&n=100&mode=0&pub=1"
                res = self.http.get(url)
                if res.json().get("data", {}).get("list"):
                    video_list = [f"{item['title']}${item['guid']}" for item in res.json()["data"]["list"]]
                from_id = "华夏"
            else:
                from_id = "华夏"
                url = f"https://api.cntv.cn/NewVideo/getVideoListByAlbumIdNew?id={guid}&serviceId=tvcctv&p=1&n=100&mode=0&pub=1"
                res = self.http.get(url)
                if res.json().get("data", {}).get("list"):
                    video_list = [f"{item['title']}${item['guid']}" for item in res.json()["data"]["list"]]
                else:
                    html_res = self.http.get(last_video)
                    pattern = r"'title':\s*'(?P<title>.+?)',\s*'brief':\s*'.+?',\s*'img':\s*'.+?',\s*'url':\s*'(?P<url>https:.+?)'" if tid in [
                        "电视剧",
                        "纪录片"] else r'class="tp1"><a\s*href="(?P<url>https:.+?)"\s*target="_blank"\s*title="(?P<title>.+?)"></a></div>'
                    matches = re.finditer(pattern, html_res.text)
                    video_list = [f"{match.group('title')}${match.group('url')}" for match in matches]

            return {
                "list": [{
                    "vod_id": vid,
                    "vod_name": title,
                    "vod_pic": logo,
                    "type_name": tid,
                    "vod_year": vod_year,
                    "vod_actor": actors,
                    "vod_content": brief,
                    "vod_play_from": from_id,
                    "vod_play_url": "#".join(video_list)
                }]
            }
        except Exception as e:
            print(f"Detail error: {e}")
            return {"list": []}

    def detailContent(self, ids):
        return self._detail(ids[0])

    async def get_guid(self, url):
        try:
            if "http" not in url:
                return url

            response = self.http.get(url)
            match = re.search(r'var\s+guid\s*=\s*"(\w+)";', response.text)
            return match.group(1) if match else url
        except Exception as e:
            print(f"Get GUID error: {e}")
            return url

    def parse_m3u8(self, content):
        lines = content.split('\n')
        streams = []
        # 定义替换模式
        pattern = r'/enc\d*/'
        replacement = '/'

        for i, line in enumerate(lines):
            if line.startswith("#EXT-X-STREAM-INF"):
                next_line = lines[i + 1] if i + 1 < len(lines) else None
                bandwidth_match = re.search(r"BANDWIDTH=(\d+)", line)
                resolution_match = re.search(r"RESOLUTION=(\d+x\d+)", line)

                if next_line and bandwidth_match and resolution_match:
                    # 使用预定义的模式和替换字符串
                    processed_url = re.sub(pattern, replacement, next_line)
                    streams.append({
                        "bandwidth": bandwidth_match.group(1),
                        "resolution": resolution_match.group(1),
                        "url": f"https://newcntv.qcloudcdn.com{processed_url}"
                    })
        return streams

    def _play(self, flag, pid):
        try:
            if flag == "华夏动画":
                api_url = f"https://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={pid}"
                response = self.http.get(api_url)
                data = response.json()
                print('解析',data)
                play_url = data.get("hls_url")
                if not play_url and data.get("video", {}).get("chapters4"):
                    chapters = data["video"]["chapters4"]
                    highest_quality = max(chapters, key=lambda x: x["bitrate"])
                    play_url = highest_quality["url"]

                if play_url:
                    return {
                        "parse": 0,
                        "url": play_url,
                        "header": {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                            "Referer": "https://tv.cctv.com/"
                        }
                    }

            # Handle search results and normal playback
            if flag in ["华夏", "中央台", "CCTV"]:
                play_url = pid
                print('解析1', play_url)
                # If it's a URL, try to extract guid
                if pid.startswith("http"):
                    try:
                        # First try to get guid from page
                        html_res = self.http.get(pid)
                        print('解析2', html_res)
                        guid_match = re.search(r'guid\s*=\s*"([a-f0-9]+)"', html_res.text, re.I)
                        if guid_match and guid_match.group(1):
                            play_url = guid_match.group(1)
                        else:
                            # Try to extract guid from URL path
                            path_match = re.search(r'/([a-f0-9]+)(?:/index\.html)?$', pid, re.I)
                            if path_match and path_match.group(1):
                                play_url = path_match.group(1)
                    except Exception as e:
                        print(f"解析页面获取guid失败: {e}")

                # Use the obtained guid or original ID to request video info
                try:
                    # api_url = f"https://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid={play_url}"
                    api_url = "https://vdn.apps.cntv.cn/api/getHttpVideoInfo.do"

                    params = {
                        "pid": pid,
                        "client": "flash",
                        "im": "0",
                        "tsp": str(int(time.time())),  # current timestamp
                        "vn": "2049",
                        "vc": "C8F76927F542220151CBBF4D31EE2B3F",
                        "uid": "34E67E3750C29C50AF1E89C985295F09",
                        "wlan": ""
                    }

                    headers = {
                        "Host": "vdn.apps.cntv.cn",
                        "Connection": "keep-alive",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
                        "Accept": "*/*",
                        "Origin": "https://tv.cctv.com",
                        "X-Requested-With": "mark.via",
                        "Sec-Fetch-Site": "cross-site",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                        "Referer": "https://tv.cctv.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
                    }
                    response = self.http.get(api_url, params=params, headers=headers)
                    data = response.json()
                    print('解析3',json.dumps(data, ensure_ascii=False, indent=2))
                    # Prefer hls_url
                    if data.get("hls_url"):
                        final_url = data["hls_url"]

                        # If there's encrypted m3u8 address, try to get the highest quality source
                        if data.get("manifest", {}).get("hls_enc2_url"):
                            print('解析4', data["manifest"]["hls_enc2_url"])
                            try:
                                m3u8_res = self.http.get(data["manifest"]["hls_enc2_url"])
                                print('解析5', m3u8_res.text)
                                streams = self.parse_m3u8(m3u8_res.text)
                                print('解析6', streams)
                                if streams:
                                    streams.sort(key=lambda x: int(x["bandwidth"]), reverse=True)
                                    final_url = streams[0]["url"]
                            except Exception as e:
                                print(f"解析M3U8失败: {e}")

                        return {
                            "parse": 0,
                            "url": final_url,
                            "header": {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                "Referer": "https://tv.cctv.com/"
                            }
                        }

                    # If no hls_url, try to use the highest quality source in video
                    if data.get("video", {}).get("chapters4"):
                        chapters = data["video"]["chapters4"]
                        highest_quality = max(chapters, key=lambda x: x["bitrate"])
                        if highest_quality.get("url"):
                            return {
                                "parse": 0,
                                "url": highest_quality["url"],
                                "header": {
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                                    "Referer": "https://tv.cctv.com/"
                                }
                            }
                except Exception as e:
                    print(f"获取视频信息失败: {e}")

            # If all methods fail, return the original address
            return {"parse": 1, "url": pid}
        except Exception as e:
            print(f"播放错误: {e}")
            return {"parse": 1, "url": pid}

    def playerContent(self, flag, pid, vipFlags=''):
        return self._play(flag, pid)

    def _search(self, pg, wd):
        pg = pg or 1
        url = f"https://search.cctv.com/ifsearch.php?page={pg}&qtext={quote(wd)}&sort=relevance&pageSize=20&type=video&vtime=-1&datepid=1&channel=&pageflag=0&qtext_str={quote(wd)}"

        try:
            response = self.http.get(url)
            data = response.json()

            def clean_text(text):
                if not text:
                    return ''
                return re.sub(r'<[^>]+>', '', text).replace('&[a-z]+;', '').replace('\s+', ' ').strip()

            videos = [{
                "vod_id": f"搜索###{clean_text(item['title'])}###{item['urllink']}###{item['imglink']}###{item['id']}###{clean_text(item['uploadtime'])}###{clean_text(item['channel'])}",
                "vod_name": clean_text(item["title"]),
                "vod_pic": item["imglink"],
                "vod_remarks": f"{clean_text(item['channel'])} · {clean_text(item.get('uploadtime', ''))}".strip()
            } for item in data.get("list", [])]

            return {
                "list": videos,
                "page": int(pg),
                "pagecount": 9999,
                "total": 999999
            }
        except Exception as e:
            print(f"Search error: {e}")
            return {"list": [], "page": 1, "pagecount": 1}

    def searchContent(self, key, quick, pg="1"):
        return self._search(int(pg), key)

    def searchContentPage(self, key, quick, pg):
        return self._search(int(pg), key)

    def localProxy(self, params):
        if params["type"] == "m3u8":
            return self.proxyM3u8(params)
        elif params["type"] == "media":
            return self.proxyMedia(params)
        elif params["type"] == "ts":
            return self.proxyTs(params)
        return None


if __name__ == '__main__':
    spider = Spider()

    # homeContent 调试
    print(">>> homeContent")
    result = spider.homeContent(filter=False)
    # print(result)
    #
    # # homeVideoContent 调试
    # print(">>> homeVideoContent")
    # result = spider.homeVideoContent()
    # print(result)
    # #
    # categoryContent 调试
    print(">>> categoryContent")
    result = spider.categoryContent(cid="电视剧", pg="1", filter=False, extend={})
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # detailContent 调试
    print(">>> detailContent")
    result = spider.detailContent(["电视剧###《浴血荣光》###https://tv.cctv.com/2025/07/15/VIDAj3HiUXkxbDOG7TRLINqV250715.shtml###https://p1.img.cctvpic.com/photoAlbum/vms/image/0938cdd8dbfb678fcf8db34cc5a77c0d.jpg###VIDAj3HiUXkxbDOG7TRLINqV250715###2025###王仁君,王志飞,刘智扬,孙维民,张一山,陶慧敏,张慧雯,宫哲,蒋依依###电视剧《浴血荣光》以“党的建军路线”为主线，聚焦1927年至1935年间中国共产党领导的革命武装，从南昌起义到遵义会议的热血奋斗历程，这段淬炼初心与信仰的峥嵘岁月，谱写了一曲从绝境奋起到伟大转折的英雄史诗。该剧由陈力执导，王仁君、王志飞、陈龙、刘智扬、孙维民、张一山、张慧雯、陶慧敏等众多实力演员集结，再现1927-1935热血征程！"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    #
    # # searchContent 调试
    # print(">>> searchContent")
    # result = spider.searchContent(key="神秘博士", quick=False, pg="1")
    # print(result)
    #
    # playerContent 调试
    print(">>> playerContent")
    result = spider.playerContent(flag="华夏", pid="201572ac97d6474788a37a4b6483601f")
    print(result)
    #
    # # getf 调试
    # print(">>> getf")
    # result = spider.getf({'type_id': '3'})
    # print(result)
    #
    # # fetch_page_data 调试
    # print(">>> fetch_page_data")
    # data, pdata = spider.fetch_page_data(page='1', id='cbe4c214f7e54c30af6f4e21dfbce264', b=True)  # 替换为真实ID
    # print(data)
    # print(pdata)