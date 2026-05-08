import sys
import json
import re
import random
import os
import time
from urllib.parse import quote, urlencode
from requests import Session, adapters
from urllib3.util.retry import Retry

sys.path.append('..')
from base.spider import Spider

# ==================== 配置 ====================
CACHE_DIR = "/storage/emulated/0/Download/KuwoMusic/music/测试"
CACHE_ENABLED = True
QUALITY_PRIORITY = ["lossless", "jymaster", "hires", "exhigh", "standard"]
COVER_MAX_SIZE_KB = 200
# =================================================

class Spider(Spider):
    def init(self, extend=""):
        self.host = "https://music.163.com"
        self.api_base = "https://ncm.zhenxin.me"
        
        self.play_apis = [
            {"url": "https://api.cenguigui.cn/api/netease/music_v1.php", "type": "cenguigui"},
            {"url": "https://api.66mz8.com/api/163.php", "type": "66mz8"},
            {"url": "https://api.uomg.com/api/163music", "type": "uomg"},
            {"url": "https://api.52hyjs.com/api/163music", "type": "52hyjs"},
            {"url": "https://api.93zbh.com/163", "type": "93zbh"},
            {"url": "https://api.yiyibot.cn/api/163", "type": "yiyibot"},
        ]
        
        self.cache_enabled = CACHE_ENABLED
        self.cache_dir = CACHE_DIR
        self._init_cache_dir()
        
        self.cover_max_size_kb = COVER_MAX_SIZE_KB
        
        self.quality_map = {
            "lossless": {"name": "无损", "code": "lossless", "br": 999000},
            "hires": {"name": "Hi-Res", "code": "hires", "br": 921600},
            "exhigh": {"name": "极高", "code": "exhigh", "br": 320000},
            "standard": {"name": "标准", "code": "standard", "br": 128000}
        }
        
        self.quality_priority = []
        for q in QUALITY_PRIORITY:
            if q in self.quality_map:
                self.quality_priority.append(self.quality_map[q])
        
        self.session = Session()
        adapter = adapters.HTTPAdapter(
            max_retries=Retry(total=3, backoff_factor=0.5),
            pool_connections=20, pool_maxsize=50
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": self.host + "/",
            "Accept": "application/json, text/plain, */*",
        }
        self.session.headers.update(self.headers)
        
        self.cache_metadata = self._load_cache_metadata()
        print("网易云音乐插件初始化完成")

    def getName(self):
        return "网易云音乐"
    
    def isVideoFormat(self, url):
        return bool(re.search(r'\.(m3u8|mp4|mp3|m4a|flv)(\?|$)', url or "", re.I))
    
    def manualVideoCheck(self):
        return False
    
    def destroy(self):
        try:
            self.session.close()
        except:
            pass

    def _init_cache_dir(self):
        if not self.cache_enabled:
            return
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except:
                self.cache_enabled = False
    
    def _get_safe_filename(self, name):
        """生成安全文件名"""
        illegal_chars = r'[<>:"/\\|?*]'
        name = re.sub(illegal_chars, '', name)
        name = name.strip('. ')
        if len(name) > 200:
            name = name[:200]
        if not name:
            name = str(int(time.time()))
        return name
    
    def _get_audio_extension(self, url):
        if not url:
            return "mp3"
        if '.flac' in url.lower():
            return "flac"
        elif '.m4a' in url.lower():
            return "m4a"
        return "mp3"
    
    def _get_cache_paths(self, name, song_id):
        safe_name = self._get_safe_filename(name)
        return {
            "audio_mp3": os.path.join(self.cache_dir, f"{safe_name}.mp3"),
            "audio_flac": os.path.join(self.cache_dir, f"{safe_name}.flac"),
            "cover": os.path.join(self.cache_dir, f"{safe_name}.jpg"),
            "lrc": os.path.join(self.cache_dir, f"{safe_name}.lrc")
        }
    
    def _load_cache_metadata(self):
        f = os.path.join(self.cache_dir, "缓存索引.json")
        if os.path.exists(f):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    return json.load(fp)
            except:
                pass
        return {}
    
    def _save_cache_metadata(self):
        if not self.cache_enabled:
            return
        f = os.path.join(self.cache_dir, "缓存索引.json")
        try:
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(self.cache_metadata, fp, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _get_cached_lrc(self, song_id):
        if not self.cache_enabled:
            return None
        if song_id in self.cache_metadata:
            p = self.cache_metadata[song_id].get("lrc_path", "")
            if p and os.path.exists(p):
                try:
                    with open(p, 'r', encoding='utf-8') as f:
                        return f.read()
                except:
                    pass
        return None

    def _format_count(self, count):
        try:
            count = int(count)
            if count > 100000000:
                return f"{round(count / 100000000, 1)}亿"
            elif count > 10000:
                return f"{round(count / 10000, 1)}万"
            return str(count)
        except:
            return str(count)

    def _fetch(self, url, method="GET", data=None, headers=None, timeout=10):
        try:
            h = self.headers.copy()
            if headers:
                h.update(headers)
            if method == "POST":
                r = self.session.post(url, data=data, headers=h, timeout=timeout)
            else:
                r = self.session.get(url, headers=h, timeout=timeout)
            r.encoding = "utf-8"
            return r.text
        except Exception as e:
            print(f"请求失败 [{url[:60]}]: {e}")
            return "{}"

    def _fetch_json(self, url, timeout=10):
        try:
            text = self._fetch(url, timeout=timeout)
            if text:
                return json.loads(text)
        except:
            pass
        return None

    # ==================== 歌词 ====================
    def _get_lyrics_by_song_id(self, song_id):
        if not song_id or not str(song_id).isdigit():
            return ""
        try:
            url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"
            data = self._fetch_json(url)
            lrc = data.get("lrc", {}).get("lyric", "") if data else ""
            if lrc and len(lrc) > 20:
                return self._clean_lyrics(lrc)
        except:
            pass
        try:
            data = self._fetch_json(f"{self.api_base}/lyric?id={song_id}")
            lrc = data.get("lrc", {}).get("lyric", "") if data else ""
            if lrc and len(lrc) > 20:
                return self._clean_lyrics(lrc)
        except:
            pass
        return ""
    
    def _clean_lyrics(self, lrc):
        if not lrc:
            return ""
        lines = lrc.split('\n')
        out = []
        for line in lines:
            line = line.strip()
            if re.match(r'^\[\d{2}:\d{2}', line) or re.match(r'^\[(ti|ar|al|by):', line, re.I):
                out.append(line)
        return '\n'.join(out)

    # ==================== 播放 ====================
    def _get_song_url(self, song_id):
        try:
            for quality in self.quality_priority:
                data = self._fetch_json(f"{self.api_base}/song/url?id={song_id}&br={quality['code']}")
                if data and "data" in data and data["data"]:
                    for item in data["data"]:
                        url = item.get("url", "")
                        if url and len(url) > 50:
                            return url, self._get_audio_extension(url)
        except:
            pass
        for api in self.play_apis:
            try:
                if api["type"] == "cenguigui":
                    url = f"{api['url']}?id={song_id}&type=json&level=lossless"
                elif api["type"] == "66mz8":
                    url = f"{api['url']}?url=https://music.163.com/song/{song_id}"
                elif api["type"] == "uomg":
                    url = f"{api['url']}?url=https://music.163.com/song?id={song_id}&type=json"
                else:
                    url = f"{api['url']}?id={song_id}"
                data = self._fetch_json(url)
                if data:
                    d = data.get("data", {})
                    play_url = None
                    if isinstance(d, dict):
                        play_url = d.get("url") or d.get("musicUrl")
                    if play_url and len(play_url) > 50:
                        return play_url, self._get_audio_extension(play_url)
            except:
                continue
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3", "mp3"

    # ==================== 首页 ====================
    def homeContent(self, filter):
        classes = [
            {"type_name": "歌单分类", "type_id": "hot_playlist"},
            {"type_name": "排行榜", "type_id": "toplist"},
            {"type_name": "歌手分类", "type_id": "artist_cat"}
        ]
        
        filters = {
            "artist_cat": [
                {"key": "area", "name": "地区", "value": [{"n": n, "v": v} for n,v in [
                    ("全部", "-1"), ("华语", "7"), ("欧美", "96"), ("韩国", "16"), ("日本", "8")
                ]]},
                {"key": "genre", "name": "性别", "value": [{"n": n, "v": v} for n,v in [
                    ("全部", "-1"), ("男歌手", "1"), ("女歌手", "2"), ("组合", "3")
                ]]},
                {"key": "letter", "name": "字母", "value": [{"n": "全部", "v": "-1"}] + 
                    [{"n": chr(i), "v": chr(i).upper()} for i in range(65, 91)] + [{"n": "#", "v": "0"}]}
            ],
            "hot_playlist": [
                {"key": "cat", "name": "类型", "value": [{"n": "全部", "v": "全部"}] + [{"n": c, "v": c} for c in [
                    "华语", "欧美", "日语", "韩语", "流行", "摇滚", "民谣", "电子", "说唱"
                ]]},
                {"key": "order", "name": "排序", "value": [{"n": "推荐", "v": "hot"}, {"n": "最新", "v": "new"}]}
            ]
        }
        
        videos = []
        
        try:
            data = self._fetch_json(f"{self.host}/api/toplist")
            if data and "list" in data:
                for it in data["list"][:8]:
                    videos.append({
                        "vod_id": f"toplist_{it['id']}",
                        "vod_name": it.get("name", ""),
                        "vod_pic": (it.get("coverImgUrl", "") or "") + "?param=300y300",
                        "vod_remarks": it.get("updateFrequency", "排行榜")
                    })
        except:
            pass
        
        try:
            data = self._fetch_json(f"{self.host}/api/playlist/hot")
            if data and "tags" in data:
                tag = data["tags"][0]["name"]
                playlists = self._fetch_json(f"{self.host}/api/playlist/list?cat={quote(tag)}&limit=10")
                if playlists and "playlists" in playlists:
                    for it in playlists["playlists"]:
                        videos.append({
                            "vod_id": f"playlist_{it['id']}",
                            "vod_name": it.get("name", ""),
                            "vod_pic": (it.get("coverImgUrl", "") or "") + "?param=300y300",
                            "vod_remarks": f"播放: {self._format_count(it.get('playCount', 0))}"
                        })
        except:
            pass
        
        return {"class": classes, "filters": filters, "list": videos}
    
    def homeVideoContent(self):
        return {"list": []}

    # ==================== 分类 ====================
    def categoryContent(self, tid, pg, filter, extend):
        pg = int(pg or 1)
        limit = 30
        videos = []
        
        try:
            if tid == "toplist":
                data = self._fetch_json(f"{self.host}/api/toplist")
                if data and "list" in data:
                    for it in data["list"]:
                        videos.append({
                            "vod_id": f"toplist_{it['id']}",
                            "vod_name": it.get("name", ""),
                            "vod_pic": (it.get("coverImgUrl", "") or "") + "?param=300y300",
                            "vod_remarks": it.get("updateFrequency", "")
                        })
                    
            elif tid == "hot_playlist":
                cat = extend.get("cat", "全部") if extend else "全部"
                order = extend.get("order", "hot") if extend else "hot"
                offset = (pg - 1) * limit
                if cat == "全部":
                    url = f"{self.host}/api/playlist/list?order={order}&limit={limit}&offset={offset}"
                else:
                    url = f"{self.host}/api/playlist/list?cat={quote(cat)}&order={order}&limit={limit}&offset={offset}"
                data = self._fetch_json(url)
                if data and "playlists" in data:
                    for it in data["playlists"]:
                        videos.append({
                            "vod_id": f"playlist_{it['id']}",
                            "vod_name": it.get("name", ""),
                            "vod_pic": (it.get("coverImgUrl", "") or "") + "?param=300y300",
                            "vod_remarks": f"播放: {self._format_count(it.get('playCount', 0))}"
                        })
                    
            elif tid == "artist_cat":
                offset = (pg - 1) * limit
                area = extend.get("area", "-1") if extend else "-1"
                genre = extend.get("genre", "-1") if extend else "-1"
                letter = extend.get("letter", "-1") if extend else "-1"
                url = f"{self.host}/api/artist/list?type={genre}&area={area}&limit={limit}&offset={offset}"
                if letter != "-1" and letter != "0":
                    url += f"&initial={letter.upper()}"
                data = self._fetch_json(url)
                if data and "artists" in data:
                    for artist in data["artists"]:
                        img_url = artist.get("picUrl", "") or artist.get("img1v1Url", "")
                        if img_url and not img_url.startswith("http"):
                            img_url = "https:" + img_url
                        videos.append({
                            "vod_id": f"artist_{artist['id']}",
                            "vod_name": artist.get("name", ""),
                            "vod_pic": f"{img_url}?param=300y300" if img_url else "",
                            "vod_remarks": f"歌曲:{artist.get('musicSize', 0)} | 专辑:{artist.get('albumSize', 0)}"
                        })
        except Exception as e:
            print(f"categoryContent错误 [{tid}]: {e}")
        
        return {"list": videos, "page": pg, "pagecount": 9999 if videos else 0, "limit": limit, "total": 999999}

    # ==================== 详情 ====================
    def detailContent(self, ids):
        did = ids[0] if isinstance(ids, list) else ids
        
        if "@" in did:
            parts = did.split("@")
            sid = parts[4] if len(parts) >= 5 and parts[4] else ""
            return self._build_single_song(parts, sid)
        
        vod = {"vod_id": did, "vod_name": "", "vod_pic": "", "vod_content": "", "vod_play_from": "", "vod_play_url": ""}
        songs = []
        
        try:
            if did.startswith("playlist_") or did.startswith("toplist_"):
                pid = did.replace("playlist_", "").replace("toplist_", "")
                data = self._fetch_json(f"{self.host}/api/v3/playlist/detail?id={pid}&n=500")
                if data and "playlist" in data:
                    playlist = data["playlist"]
                    vod["vod_name"] = playlist.get("name", "歌单/排行榜")
                    vod["vod_pic"] = (playlist.get("coverImgUrl", "")) + "?param=500y500"
                    vod["vod_content"] = playlist.get("description", "")
                    track_ids = [t["id"] for t in playlist.get("trackIds", [])]
                    if track_ids:
                        for i in range(0, min(len(track_ids), 500), 200):
                            b = track_ids[i:i+200]
                            d = self._fetch_json(f"{self.host}/api/song/detail?ids=[{','.join(map(str,b))}]")
                            if d and "songs" in d:
                                songs.extend(d["songs"])
            elif did.startswith("artist_"):
                aid = did.replace("artist_", "")
                data = self._fetch_json(f"{self.host}/api/artist/top/song?id={aid}")
                if data and "songs" in data:
                    songs = data["songs"]
                    info = self._fetch_json(f"{self.host}/api/artist/detail?id={aid}")
                    if info and "data" in info:
                        a = info["data"]["artist"]
                        vod["vod_name"] = a.get("name", "") + "的热门歌曲"
                        vod["vod_pic"] = (a.get("picUrl", "") or a.get("img1v1Url", "")) + "?param=500y500"
        except Exception as e:
            print(f"detailContent错误: {e}")
        
        if songs:
            self._build_play_urls(vod, songs)
        return {"list": [vod]}
    
    def _build_play_urls(self, vod, songs):
        qualities = [["标准", "standard"], ["极高", "exhigh"], ["无损", "lossless"], ["Hi-Res", "hires"]]
        play_from = []
        play_urls = []
        for q_name, q_code in qualities:
            play_from.append(q_name)
            eps = []
            for s in songs:
                artists = [ar.get("name", "") for ar in s.get("ar", [])]
                name = f"{s.get('name','')} - {'/'.join(artists)}"
                eps.append(f"{name}${s.get('id','')}|{q_code}")
            play_urls.append("#".join(eps))
        play_from.append("📥 下载")
        eps2 = []
        for s in songs:
            artists = [ar.get("name", "") for ar in s.get("ar", [])]
            name = f"{s.get('name','')} - {'/'.join(artists)}"
            eps2.append(f"{name}${s.get('id','')}|download")
        play_urls.append("#".join(eps2))
        vod["vod_play_from"] = "$$$".join(play_from)
        vod["vod_play_url"] = "$$$".join(play_urls)
    
    def _build_single_song(self, parts, sid):
        vod = {"vod_id": parts[0], "vod_name": parts[1], "vod_pic": "", "vod_remarks": parts[2], "vod_actor": parts[3], "vod_year": parts[7] if len(parts) > 7 else ""}
        songs = [{"id": parts[0], "name": parts[1], "artist": parts[2]}]
        if sid:
            try:
                d = self._fetch_json(f"{self.host}/api/artist/top/song?id={sid}")
                if d and "songs" in d:
                    for s in d["songs"]:
                        if str(s.get("id","")) != parts[0]:
                            ar = "/".join([a.get("name","") for a in s.get("ar",[])])
                            songs.append({"id": str(s.get("id","")), "name": s.get("name",""), "artist": ar})
                            if len(songs) >= 10: break
            except:
                pass
        qualities = [["标准", "standard"], ["极高", "exhigh"], ["无损", "lossless"], ["Hi-Res", "hires"]]
        play_from = []
        play_urls = []
        for q_name, q_code in qualities:
            play_from.append(q_name)
            eps = [f"{s['name']} - {s['artist']}${s['id']}|{q_code}" for s in songs]
            play_urls.append("#".join(eps))
        play_from.append("📥 下载")
        eps2 = [f"{s['name']} - {s['artist']}${s['id']}|download" for s in songs]
        play_urls.append("#".join(eps2))
        vod["vod_play_from"] = "$$$".join(play_from)
        vod["vod_play_url"] = "$$$".join(play_urls)
        return {"list": [vod]}

    # ==================== 搜索 ====================
    def searchContent(self, key, quick, pg="1"):
        pg = int(pg or 1)
        offset = (pg - 1) * 30
        videos = []
        try:
            params = {"s": key, "type": 1, "offset": offset, "limit": 30}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            text = self._fetch(f"{self.host}/api/cloudsearch/pc", "POST", urlencode(params), headers)
            if text:
                data = json.loads(text)
                if "result" in data and "songs" in data["result"]:
                    for s in data["result"]["songs"]:
                        ar_names = "/".join([ar["name"] for ar in s.get("ar", [])])
                        id_parts = [str(s["id"]), s["name"], ar_names, ar_names,
                            str(s["ar"][0]["id"]) if s.get("ar") else "",
                            str(s["al"]["id"]) if s.get("al") else "",
                            s["al"]["name"] if s.get("al") else "",
                            str(s.get("publishTime",0)//1000)[:4], str(s.get("mv",0))]
                        videos.append({"vod_id": "@".join(id_parts), "vod_name": s["name"],
                            "vod_pic": (s.get("al",{}).get("picUrl","")) + "?param=300y300",
                            "vod_remarks": ar_names})
        except Exception as e:
            print(f"搜索失败: {e}")
        return {"list": videos, "page": pg}

    # ==================== 播放器 ====================
    def playerContent(self, flag, id, vipFlags):
        parts = id.split("|")
        raw = parts[0] if len(parts) > 0 else ""
        action = parts[1] if len(parts) > 1 else "play"
        
        # 解析：从"歌曲名 - 歌手$ID"中提取
        song_id = raw
        song_display = raw
        
        if "$" in raw:
            name_part, song_id = raw.rsplit("$", 1)
            song_display = name_part.strip()
        
        song_id = song_id.strip()
        
        # 如果song_display还是纯数字，从API获取歌名
        if song_display == song_id or not song_display:
            try:
                data = self._fetch_json(f"{self.api_base}/song/detail?ids={song_id}")
                if data and "songs" in data and data["songs"]:
                    s = data["songs"][0]
                    name = s.get("name", "")
                    artists = s.get("ar", [])
                    if artists:
                        ar_names = "/".join([ar.get("name", "") for ar in artists])
                        song_display = f"{name} - {ar_names}"
                    else:
                        song_display = name
            except:
                pass
        
        print(f"song_display={song_display}, song_id={song_id}")
        
        # 获取封面
        pic = ""
        try:
            data = self._fetch_json(f"{self.api_base}/song/detail?ids={song_id}")
            if data and "songs" in data and data["songs"]:
                s = data["songs"][0]
                pic = s.get("al", {}).get("picUrl", "")
                if pic and not pic.startswith("http"):
                    pic = "https:" + pic
        except:
            pass
        
        # 歌词
        lrc_str = self._get_lyrics_by_song_id(song_id)
        
        # 下载
        if action == "download":
            print(f"📥 下载: {song_display}")
            play_url, ext = self._get_song_url(song_id)
            if not play_url:
                return {"parse": 0, "url": "", "header": "", "pic": pic, "lrc": "", "msg": "❌ 获取播放地址失败"}
            
            # 用中文名生成路径
            paths = self._get_cache_paths(song_display, song_id)
            audio_path = paths["audio_flac"] if ext == "flac" else paths["audio_mp3"]
            temp_path = os.path.join(self.cache_dir, f"tmp_{song_id}.tmp")
            
            try:
                r = self.session.get(play_url, stream=True, timeout=120)
                with open(temp_path, 'wb') as f:
                    for chunk in r.iter_content(8192):
                        if chunk: f.write(chunk)
                if os.path.exists(audio_path): os.remove(audio_path)
                os.rename(temp_path, audio_path)
                print(f"✓ 音频: {os.path.basename(audio_path)}")
            except:
                if os.path.exists(temp_path): os.remove(temp_path)
                return {"parse": 0, "url": "", "header": "", "pic": pic, "lrc": "", "msg": "❌ 下载失败"}
            
            # 封面
            cover_path = None
            if pic and pic.startswith("http"):
                try:
                    r = self.session.get(pic, timeout=15)
                    if r.status_code == 200 and len(r.content) > 100:
                        cover_path = paths["cover"]
                        with open(cover_path, 'wb') as f:
                            f.write(r.content)
                        print(f"✓ 封面: {os.path.basename(cover_path)}")
                except:
                    pass
            
            # 歌词保存
            if lrc_str:
                try:
                    with open(paths["lrc"], 'w', encoding='utf-8') as f:
                        f.write(lrc_str)
                except:
                    pass
            
            # 保存缓存
            self.cache_metadata[song_id] = {
                "song_id": song_id, "song_name": song_display,
                "audio_path": audio_path, "cover_path": cover_path, "lrc_path": paths["lrc"] if lrc_str else None,
                "format": ext, "cached_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_cache_metadata()
            
            return {"parse": 0, "url": f"file://{audio_path}", "header": json.dumps(self.headers),
                "pic": cover_path if cover_path else pic, "lrc": lrc_str, "msg": f"✅ {song_display}"}
        
        # 正常播放 - 检查缓存后走网络
        if self.cache_enabled and song_id in self.cache_metadata:
            m = self.cache_metadata[song_id]
            if m.get("audio_path") and os.path.exists(m["audio_path"]):
                cp = m.get("cover_path", "")
                return {"parse": 0, "url": f"file://{m['audio_path']}", "header": json.dumps(self.headers),
                    "pic": f"file://{cp}" if cp and os.path.exists(cp) else pic, "lrc": lrc_str}
        
        play_url, _ = self._get_song_url(song_id)
        return {"parse": 0, "url": play_url or "", "header": json.dumps(self.headers), "pic": pic, "lrc": lrc_str}

spider = Spider