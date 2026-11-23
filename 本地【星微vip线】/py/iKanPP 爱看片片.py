# -*- coding: utf-8 -*-
"""
iKanPP 爱看片片（https://www.ikanpp.com/）TVBox / LookPro Python 爬虫。

仅依赖 requests。
配置示例：
{"key":"py_ikanpp","name":"爱看片片(PY)","type":3,"api":"./py_ikanpp.py","searchable":1,"quickSearch":1,"filterable":0}

extend 可指定额外域名：{"hosts":["https://www.ikanpp.com","https://ikanpp.com"]}
"""

import base64
import concurrent.futures
import html
import json
import re
import time
from urllib.parse import quote, unquote, urljoin, urlsplit

import requests


class Spider:
    hosts = ["https://www.ikanpp.com", "https://ikanpp.com"]
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    )
    categories = [
        {"type_id": "movie", "type_name": "电影"},
        {"type_id": "tv", "type_name": "电视剧"},
        {"type_id": "anime", "type_name": "动漫"},
        {"type_id": "variety", "type_name": "综艺"},
        {"type_id": "documentary", "type_name": "纪录片"},
        {"type_id": "short", "type_name": "短剧"},
    ]
    # 官网播放器的完整源列表（含优先级），详情会聚合全部可用源。
    sources = [
        {"name": "巨量资源", "api": "https://api.juliang.live/api/provide/vod", "priority": 1},
        {"name": "光速资源", "api": "https://api.guangsuapi.com/api.php/provide/vod", "priority": 2},
        {"name": "暴风资源", "api": "https://bfzyapi.com/api.php/provide/vod", "priority": 2},
        {"name": "无尽资源", "api": "https://api.wujinapi.com/api.php/provide/vod", "priority": 3},
        {"name": "最大资源", "api": "https://api.zuidapi.com/api.php/provide/vod", "priority": 4},
        {"name": "极速资源", "api": "https://jszyapi.com/api.php/provide/vod", "priority": 5},
        {
            "name": "新浪资源",
            "api": "https://api.xinlangapi.com/xinlangapi.php/provide/vod",
            "priority": 6,
        },
        {"name": "电影天堂", "api": "http://caiji.dyttzyapi.com/api.php/provide/vod", "priority": 7},
        {"name": "魔都资源", "api": "https://www.mdzyapi.com/api.php/provide/vod", "priority": 8},
        {"name": "360资源", "api": "https://360zy.com/api.php/provide/vod", "priority": 9},
        {"name": "1080JSON", "api": "https://api.1080zyku.com/inc/apijson.php", "priority": 10},
        {"name": "海豚资源", "api": "https://hhzyapi.com/api.php/provide/vod", "priority": 11},
        {"name": "虎牙资源", "api": "https://www.huyaapi.com/api.php/provide/vod", "priority": 12},
        {"name": "非凡资源", "api": "https://api.ffzyapi.com/api.php/provide/vod", "priority": 13},
        {"name": "速博资源", "api": "https://subocaiji.com/api.php/provide/vod", "priority": 14},
        {"name": "量子资源", "api": "http://cj.lziapi.com/api.php/provide/vod", "priority": 15},
        {"name": "如意资源", "api": "https://cj.rycjapi.com/api.php/provide/vod", "priority": 16},
        {"name": "优酷资源", "api": "https://api.ukuapi88.com/api.php/provide/vod", "priority": 17},
        {"name": "iKun资源", "api": "https://ikunzyapi.com/api.php/provide/vod", "priority": 18},
        {"name": "红牛资源", "api": "https://www.hongniuzy2.com/api.php/provide/vod", "priority": 20},
        {"name": "鲸鱼资源", "api": "https://jyzyapi.com/provide/vod", "priority": 21},
        {"name": "魔都影视", "api": "https://www.moduzy.com/api.php/provide/vod", "priority": 22},
        {"name": "魔都动漫", "api": "https://caiji.moduapi.cc/api.php/provide/vod", "priority": 23},
    ]
    fallback_types = {
        "movie": 1,
        "tv": 2,
        "anime": 3,
        "variety": 4,
        "documentary": 115,
        "short": 5,
    }
    card_pattern = re.compile(
        r"<a\b(?=[^>]*\bclass=[\"'][^\"']*cinema-poster-card)"
        r"(?=[^>]*\bhref=[\"']([^\"']+)[\"'])[^>]*>(.*?)</a>",
        re.I | re.S,
    )

    def __init__(self):
        self.session = requests.Session()
        self.hosts = list(self.hosts)
        self.sources = sorted(
            (dict(source) for source in self.sources), key=lambda item: item["priority"]
        )
        self._failed_sources = {}
        self._host_index = 0
        self.host = self.hosts[0]
        self.timeout = 20
        self._set_host(self.host)

    def _set_host(self, host):
        self.host = host.rstrip("/")
        self.session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": self.host + "/",
            }
        )

    def init(self, extend=""):
        if isinstance(extend, str):
            try:
                extend = json.loads(extend) if extend.strip() else {}
            except json.JSONDecodeError:
                extend = {"hosts": [extend]}
        if not isinstance(extend, dict):
            return
        values = extend.get("hosts") or extend.get("host") or extend.get("domain")
        if isinstance(values, str):
            values = re.split(r"[,，\s]+", values)
        if not isinstance(values, list):
            return
        custom = []
        for value in values:
            host = str(value or "").strip().rstrip("/")
            if not host:
                continue
            if not host.startswith(("http://", "https://")):
                host = "https://" + host
            if urlsplit(host).netloc and host not in custom:
                custom.append(host)
        if custom:
            self.hosts = custom + [host for host in self.hosts if host not in custom]
            self._host_index = 0
            self._set_host(self.hosts[0])

    def getName(self):
        return "爱看片片"

    def destroy(self):
        self.session.close()

    @staticmethod
    def _clean(value):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", value, flags=re.I | re.S)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", html.unescape(text)).strip()

    @staticmethod
    def _attr(text, name):
        match = re.search(r"\b" + re.escape(name) + r"\s*=\s*[\"']([^\"']*)", text, re.I)
        return html.unescape(match.group(1)).strip() if match else ""

    @staticmethod
    def _normalize_title(value):
        return re.sub(r"[\s·:：_\-—－()（）\[\]【】]", "", str(value or "")).lower()

    @staticmethod
    def _encode_token(data):
        raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @staticmethod
    def _decode_token(token):
        try:
            token += "=" * (-len(token) % 4)
            data = json.loads(base64.urlsafe_b64decode(token).decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (ValueError, UnicodeDecodeError, TypeError):
            return {}

    def _request(self, path, params=None):
        last_error = None
        for offset in range(len(self.hosts)):
            index = (self._host_index + offset) % len(self.hosts)
            self._set_host(self.hosts[index])
            try:
                response = self.session.get(
                    self.host + path,
                    params=params,
                    timeout=(8, self.timeout),
                )
                response.raise_for_status()
                response.encoding = "utf-8"
                text = response.text
                if len(text) < 100 or "cinema-poster-card" not in text:
                    raise ValueError("页面未包含影片数据")
                if "Attention Required! | Cloudflare" in text or "Why have I been blocked?" in text:
                    raise ValueError("站点触发了 Cloudflare 防护")
                final_host = urlsplit(response.url)
                if final_host.scheme in ("http", "https") and final_host.netloc:
                    detected = f"{final_host.scheme}://{final_host.netloc}"
                    self.hosts[index] = detected.rstrip("/")
                self._host_index = index
                self._set_host(self.hosts[index])
                return text
            except (requests.RequestException, ValueError) as exc:
                last_error = exc
        raise ValueError(f"所有可用域名均请求失败：{last_error}")

    def _pic(self, value):
        pic = html.unescape(str(value or "")).replace("\\/", "/").strip()
        if not pic:
            return ""
        if pic.startswith("//"):
            return "https:" + pic
        return urljoin(self.host + "/", pic)

    def _parse_videos(self, text):
        videos, seen = [], set()
        for match in self.card_pattern.finditer(text):
            href, body = match.group(1), match.group(2)
            if "/title/" not in href:
                continue
            image_match = re.search(r"<img\b[^>]*>", body, re.I)
            image = image_match.group(0) if image_match else ""
            title_match = re.search(r"<h3\b[^>]*>(.*?)</h3>", body, re.I | re.S)
            title = self._clean(title_match.group(1)) if title_match else ""
            if not title:
                title = self._attr(image, "alt")
            slug = unquote(href.split("/title/", 1)[1].split("?", 1)[0]).strip("/")
            slug_title = re.sub(r"^ik\d+-", "", slug, flags=re.I)
            if not title:
                title = slug_title
            if not title or not slug:
                continue
            key = (slug, title)
            if key in seen:
                continue
            seen.add(key)
            plain = self._clean(body)
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", plain)
            score_match = re.search(r"(?<!\d)(10\.0|\d\.\d)(?!\d)", plain)
            remarks_match = re.search(
                r"(更新至\s*第?\s*\d+\s*集|全\s*\d+\s*集|第\s*\d+\s*期|正片)", plain
            )
            pic = self._pic(self._attr(image, "src") or self._attr(image, "data-src"))
            token = self._encode_token(
                {
                    "title": title,
                    "alias": slug_title,
                    "pic": pic,
                    "year": year_match.group(1) if year_match else "",
                }
            )
            videos.append(
                {
                    "vod_id": token,
                    "vod_name": title,
                    "vod_pic": pic,
                    "vod_remarks": remarks_match.group(1).replace(" ", "") if remarks_match else "",
                    "vod_year": year_match.group(1) if year_match else "",
                    "vod_score": score_match.group(1) if score_match else "",
                }
            )
        return videos

    @staticmethod
    def _list_result(videos, page=1, pagecount=1, total=None):
        return {
            "list": videos,
            "page": page,
            "pagecount": pagecount,
            "limit": len(videos) if videos else 20,
            "total": len(videos) if total is None else total,
        }

    def homeContent(self, filter=False):
        # 本站各频道没有统一的筛选参数，不给所有分类套用虚假筛选。
        return {"class": [dict(category) for category in self.categories], "filters": {}}

    def homeVideoContent(self):
        try:
            videos = self._parse_videos(self._request("/"))
            if videos:
                return self._list_result(videos[:30])
        except ValueError:
            pass
        # Cloudflare、域名故障或页面结构变化时，使用官网同一聚合资源站兜底。
        return self._resource_list("movie", 1, include_type=False)

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        category = str(tid).strip() or "movie"
        if category not in {item["type_id"] for item in self.categories}:
            category = "movie"
        if page > 1:
            return self._resource_list(category, page)
        try:
            videos = self._parse_videos(self._request("/" + quote(category)))
            if videos:
                return self._list_result(videos, page=1)
        except ValueError:
            pass
        return self._resource_list(category, page)

    def _source_request(self, source, params):
        response = requests.get(
            source["api"],
            params=params,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
            timeout=(5, 10),
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        data = response.json()
        if not isinstance(data, dict) or not isinstance(data.get("list"), list):
            raise ValueError(f"{source['name']}接口返回格式错误")
        return data

    def _query_sources(self, keyword, page=1):
        # 失效源缓存 5 分钟，避免每次详情都等待超时。
        now = time.time()
        active = [
            source
            for source in self.sources
            if now - self._failed_sources.get(source["name"], 0) > 300
        ]
        if not active:
            active = list(self.sources)

        def query(source):
            try:
                data = self._source_request(
                    source, {"ac": "detail", "wd": keyword, "pg": page}
                )
                self._failed_sources.pop(source["name"], None)
                return source, data
            except (requests.RequestException, ValueError, json.JSONDecodeError):
                self._failed_sources[source["name"]] = time.time()
                return source, None

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(active)) as executor:
            return list(executor.map(query, active))

    @staticmethod
    def _best_item(items, title):
        if not items:
            return None
        target = Spider._normalize_title(title)
        for item in items:
            if isinstance(item, dict) and Spider._normalize_title(item.get("vod_name")) == target:
                return item
        return next((item for item in items if isinstance(item, dict)), None)

    def _resource_vod(self, source, item):
        title = str(item.get("vod_name") or "").strip()
        vod_id = item.get("vod_id")
        if not title or vod_id is None:
            return None
        token = self._encode_token(
            {
                "title": title,
                "source": source["name"],
                "id": str(vod_id),
                "pic": str(item.get("vod_pic") or ""),
                "year": str(item.get("vod_year") or ""),
            }
        )
        return {
            "vod_id": token,
            "vod_name": title,
            "vod_pic": str(item.get("vod_pic") or "").replace("\\/", "/"),
            "vod_remarks": str(item.get("vod_remarks") or ""),
            "vod_year": str(item.get("vod_year") or ""),
            "vod_area": str(item.get("vod_area") or ""),
            "vod_score": str(item.get("vod_score") or ""),
        }

    def _resource_list(self, category, page=1, include_type=True):
        params = {"ac": "list", "pg": page}
        if include_type:
            params["t"] = self.fallback_types.get(category, 1)
        now = time.time()
        ordered = sorted(
            self.sources,
            key=lambda item: now - self._failed_sources.get(item["name"], 0) <= 300,
        )
        last_error = None
        for source in ordered:
            try:
                data = self._source_request(source, params)
                self._failed_sources.pop(source["name"], None)
            except (requests.RequestException, ValueError, json.JSONDecodeError) as exc:
                self._failed_sources[source["name"]] = time.time()
                last_error = exc
                continue
            videos = [self._resource_vod(source, item) for item in data["list"] if isinstance(item, dict)]
            videos = [video for video in videos if video]
            if videos:
                try:
                    pagecount = max(1, int(data.get("pagecount") or 1))
                    total = int(data.get("total") or len(videos))
                except (TypeError, ValueError):
                    pagecount, total = 1, len(videos)
                return self._list_result(videos, page, pagecount, total)
        raise ValueError(f"资源站列表请求失败：{last_error}")

    def searchContent(self, key, quick=False, pg=1):
        try:
            page = max(1, int(pg))
        except (TypeError, ValueError):
            page = 1
        keyword = str(key or "").strip()
        if not keyword:
            return self._list_result([], page=page)
        # 并行查询，按优先级取到精确片名即返回，避免慢站拖过应用超时。
        now = time.time()
        active = [
            source
            for source in self.sources
            if now - self._failed_sources.get(source["name"], 0) > 300
        ]
        if not active:
            active = list(self.sources)
        target = self._normalize_title(keyword)
        fallback = None
        deadline = time.time() + 6.5
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(active))
        futures = [
            (
                source,
                executor.submit(self._search_source, source, keyword, page),
            )
            for source in active
        ]
        try:
            for source, future in futures:
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
                try:
                    data = future.result(timeout=remaining)
                except Exception:
                    continue
                if not data:
                    continue
                items = [item for item in data["list"] if isinstance(item, dict)]
                exact = [item for item in items if self._normalize_title(item.get("vod_name")) == target]
                videos = [self._resource_vod(source, item) for item in exact]
                videos = [video for video in videos if video]
                if videos:
                    return self._list_result(videos, page, 1, len(videos))
                if fallback is None:
                    videos = [self._resource_vod(source, item) for item in items]
                    videos = [video for video in videos if video]
                    if videos:
                        fallback = self._list_result(videos, page, 1, len(videos))
        finally:
            executor.shutdown(wait=False)
        return fallback or self._list_result([], page=page)

    def _search_source(self, source, keyword, page):
        try:
            data = self._source_request(
                source, {"ac": "detail", "wd": keyword, "pg": page}
            )
            self._failed_sources.pop(source["name"], None)
            return data
        except (requests.RequestException, ValueError, json.JSONDecodeError):
            self._failed_sources[source["name"]] = time.time()
            return None

    def _source_from_token(self, token):
        name = str(token.get("source") or "")
        for source in self.sources:
            if source["name"] == name:
                return source
        try:
            return self.sources[int(name)]
        except (TypeError, ValueError, IndexError):
            return None

    def _detail_from_source_id(self, token):
        source = self._source_from_token(token)
        if not source:
            return None
        try:
            data = self._source_request(
                source, {"ac": "detail", "ids": str(token.get("id") or "")}
            )
        except (requests.RequestException, ValueError, json.JSONDecodeError):
            return None
        item = self._best_item(data.get("list") or [], token.get("title") or "")
        return (source, item) if item else None

    @staticmethod
    def _play_groups(item):
        flags = str(item.get("vod_play_from") or "默认线路").split("$$$")
        groups = str(item.get("vod_play_url") or "").split("$$$")
        return flags, groups

    def _build_detail(self, vod_id, token, source_items):
        source_items = [(source, item) for source, item in source_items if item]
        if not source_items:
            raise ValueError("未找到可播放资源")
        primary_source, primary = source_items[0]
        play_from, play_url = [], []
        for source, item in source_items:
            flags, groups = self._play_groups(item)
            for index, group in enumerate(groups):
                episodes = []
                for number, value in enumerate(group.split("#")):
                    if not value.strip():
                        continue
                    if "$" in value:
                        name, url = value.rsplit("$", 1)
                    else:
                        name, url = ("正片" if len(groups) == 1 else f"第{number + 1}集"), value
                    url = html.unescape(url.strip()).replace("\\/", "/")
                    if not url:
                        continue
                    if url.startswith("//"):
                        url = "https:" + url
                    elif not url.startswith(("http://", "https://")):
                        url = urljoin(source["api"], url)
                    name = self._clean(name).replace("$", "").replace("#", "") or f"第{number + 1}集"
                    episodes.append(f"{name}${url}")
                if episodes:
                    flag = flags[index] if index < len(flags) and flags[index] else "默认线路"
                    flag = self._clean(flag).replace("$", "") or "默认线路"
                    play_from.append(f"{source['name']}-{flag}")
                    play_url.append("#".join(episodes))
        if not play_url:
            raise ValueError("影片暂时没有可播放线路")
        title = str(primary.get("vod_name") or token.get("title") or "未知标题")
        pic = str(primary.get("vod_pic") or token.get("pic") or "").replace("\\/", "/")
        result = {
            "vod_id": vod_id,
            "vod_name": title,
            "vod_pic": pic,
            "vod_remarks": str(primary.get("vod_remarks") or ""),
            "vod_year": str(primary.get("vod_year") or token.get("year") or ""),
            "vod_area": str(primary.get("vod_area") or ""),
            "vod_lang": str(primary.get("vod_lang") or ""),
            "vod_score": str(primary.get("vod_score") or ""),
            "vod_actor": str(primary.get("vod_actor") or ""),
            "vod_director": str(primary.get("vod_director") or ""),
            "vod_class": str(primary.get("vod_class") or primary.get("type_name") or ""),
            "vod_content": str(primary.get("vod_content") or primary.get("vod_blurb") or ""),
            "vod_play_from": "$$$".join(play_from),
            "vod_play_url": "$$$".join(play_url),
        }
        return {"list": [result]}

    def detailContent(self, ids):
        vod_id = ids[0] if isinstance(ids, (list, tuple)) else str(ids)
        token = self._decode_token(str(vod_id))
        title = str(token.get("title") or "").strip()
        if not title:
            raise ValueError("影片标识无效")
        # 先取搜索命中的源，再聚合官网其余资源站，保证线路完整。
        selected = None
        if token.get("id"):
            selected = self._detail_from_source_id(token)
        results = self._query_sources(title)
        source_items = [selected] if selected else []
        selected_source = selected[0] if selected else None
        for source, data in results:
            if not data or source is selected_source:
                continue
            item = self._best_item(data.get("list") or [], title)
            if item:
                source_items.append((source, item))
        if not source_items and token.get("alias") and token["alias"] != title:
            for source, data in self._query_sources(str(token["alias"])):
                if data:
                    item = self._best_item(data.get("list") or [], token["alias"])
                    if item:
                        source_items.append((source, item))
        # 精确匹配优先，其余同名片源保持优先级顺序。
        source_items.sort(
            key=lambda pair: (
                self._normalize_title(pair[1].get("vod_name")) != self._normalize_title(title),
                pair[0]["priority"],
            )
        )
        return self._build_detail(str(vod_id), token, source_items)

    def playerContent(self, flag, id, vipFlags=None):
        url = html.unescape(str(id or "").strip()).replace("\\/", "/")
        if not url.startswith(("http://", "https://")):
            raise ValueError("播放地址无效")
        direct = bool(re.search(r"\.(m3u8|mp4|mkv|flv)(?:$|[?#])", url, re.I))
        return {
            "parse": 0 if direct else 1,
            "playUrl": "",
            "url": url,
            "header": {"User-Agent": self.user_agent},
        }

    def playContent(self, flag, id, vipFlags=None):
        return self.playerContent(flag, id, vipFlags)
