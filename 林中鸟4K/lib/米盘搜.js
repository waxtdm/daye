var rule = {
    title: '米盘搜',
    host: 'https://misoso.cc/',
    hostJs: '',
    headers: {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36',
    },
    编码: 'utf-8',
    timeout: 5000,
    url: 'https://misoso.cc/search?q=fyclass&format=video&page=fypage',
    filter_url: '',
    detailUrl: '',
    searchUrl: 'https://misoso.cc/search?q=**&format=video&page=fypage',
    searchable: 1,
    quickSearch: 1,
    filterable: 1,
    class_name: '',
    class_url: '',
    proxy_rule: '',
    sniffer: false,
    isVideo: '',
    play_parse: true,
    parse_url: '',
    lazy: "js:\n        input = 'push://' + input;\n    ",
    limit: 9,
    double: false,
    // 推荐: '*',
    一级: 'js:\n        let html = fetch(input);\n        let list = pdfa(html, "body&&.semi-space-medium-vertical");\n        VODS = list.map(x => {\n            let remarks = pdfh(x, "div&&img&&alt");\n            // 过滤掉包含"迅雷云盘"的内容\n            if(remarks.includes("迅雷云盘")) return null;\n            return {\n                vod_name: pdfh(x, "div&&a&&title"),\n                vod_pic: \'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1748421892138/IMG_20250528_164428.jpg\',\n                vod_remarks: remarks,\n                vod_content: remarks,\n                vod_id: pdfh(x, "div&&a&&href")\n            }\n        }).filter(x => x !== null);\n    ',
    二级: {
        title: 'h1&&Text',
        img: 'img&&src',
        desc: '.card-text:eq(2)&&Text;;;;',
        content: 'body&&.semi-space-loose-vertical&&a&&href',
        tabs: "js:TABS = ['米盘搜']",
        lists: "js:\n            LISTS = [];\n            let lists1 = pdfa(html, 'body&&.semi-space-loose-vertical').map(it => {\n                let _tt = pdfh(it, 'span&&title');\n                let _uu = pdfh(it, 'a&&href');\n                return _tt + '$' + _uu;\n            });\n            LISTS.push(lists1);\n        ",
    },
    搜索: 'js:\n        let html = fetch(input);\n        let list = pdfa(html, "body&&.semi-space-medium-vertical");\n        VODS = list.map(x => {\n            let remarks = pdfh(x, "div&&img&&alt");\n            // 过滤掉包含"迅雷云盘"的内容\n            if(remarks.includes("迅雷云盘")) return null;\n            return {\n                vod_name: pdfh(x, "div&&a&&title"),\n                vod_pic: \'https://fs-im-kefu.7moor-fs1.com/ly/4d2c3f00-7d4c-11e5-af15-41bf63ae4ea0/1748421892138/IMG_20250528_164428.jpg\',\n                vod_remarks: remarks,\n                vod_content: remarks,\n                vod_id: pdfh(x, "div&&a&&href")\n            }\n        }).filter(x => x !== null);\n    ',
    cate_exclude: '首页|留言|APP|下载|资讯|新闻|动态',
    tab_exclude: '猜你|喜欢|下载|剧情|榜|评论',
    类型: '影视',
    homeUrl: 'https://misoso.cc/',
    二级访问前: '',
    encoding: 'utf-8',
    search_encoding: '',
    图片来源: '',
    图片替换: '',
    play_json: [],
    pagecount: {},
    tab_remove: [],
    tab_order: [],
    tab_rename: {},
}