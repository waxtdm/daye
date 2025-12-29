var rule = {
    类型: '百度短剧',
    title: '百度短剧',
    host: 'https://api.jkyai.top',
    url: '/API/bddjss.php?page=fypage&name=fyclass',
    searchUrl: '/API/bddjss.php?page=fypage&name=**',
    searchable: 1,
    quickSearch: 1,
    timeout: 5000,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    },
    class_name: '系统&重生&复仇&乡下&古代&穿越&战神&开局&逆袭&女帝&神医&总裁&萌宝&都市',
    class_url: '系统&重生&复仇&乡下&古代&穿越&战神&开局&逆袭&女帝&神医&总裁&萌宝&都市',
    play_parse: true,
    lazy: $js.toString(() => {
        let html = request(input);
        let json = JSON.parse(html);
        let qualities = json.data.qualities;
        let quality = qualities.find(q => q.quality === '1080p') || 
                     qualities.find(q => q.quality === 'sc') || 
                     qualities.find(q => q.quality === 'sd');
        input = { url: quality.download_url, parse: 0 };
    }),
    double: true,
    一级: $js.toString(() => {
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let data = json.data;
        data.forEach(it => {
            let id = 'https://api.cenguigui.cn/api/duanju/baidu/?id=' + it.id;
            d.push({
                url: id,
                title: it.title,
                year: it.type,
                desc: it.author,
                content: it.intro,
                img: it.cover,
            });
        });
        setResult(d);
    }),
    二级: $js.toString(() => {
        let urls = [];
        let html = request(input);
        let json = JSON.parse(html);
        let data = json.data;
        data.forEach(it => {
            let chapterName = it.title || "未知章节";
            let videoId = it.video_id;
            let playUrl = 'https://api.cenguigui.cn/api/duanju/baidu/?video_id=' + videoId;
            urls.push(chapterName + '$' + playUrl);
        });
        VOD = {
            vod_name: json.title,
            vod_pic: '',
            vod_actor: '',
            vod_type: '',
            vod_content: '',
            vod_play_from: '百度短剧',
            vod_play_url: urls.join('#')
        };
    }),
    搜索: $js.toString(() => {
        let d = [];
        let html = request(input);
        let json = JSON.parse(html);
        let data = json.data;
        data.forEach(it => {
            let id = 'https://api.cenguigui.cn/api/duanju/baidu/?id=' + it.id;
            d.push({
                url: id,
                title: it.title,
                year: it.type,
                desc: it.author,
                content: it.intro,
                img: it.cover,
            });
        });
        setResult(d);
    }),
};