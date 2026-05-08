/*
@header({
  searchable: 1,
  filterable: 1,
  quickSearch: 1,
  title: 'bbys',
  lang: 'cat'
})
*/

import {Crypto, _} from 'assets://js/lib/cat.js';

let host = 'https://bbys.app';
let device_id = '';
const pkg = 'com.sunshine.tv';
const ver = '6';
const device_id_cache_key = 'com.sunshine.tv_bbys_cache_v4';

async function init(cfg) {
    if (typeof cfg.ext === 'string' && cfg.ext.startsWith('http')) {
        host = cfg.ext.trim().replace(/\/$/, '');
    }
}

async function home(filter) {
    const hd = await getHeaders();
    const resp = await req(`${host}/api.php/app/index/home`, { headers: hd });
    const json = JSON.parse(resp.content);

    const classes = _.map(json.data.categories, (i) => ({
        type_id: i.type_name,
        type_name: i.type_name
    }));

    let filters = {};
    for (let c of classes) {
        // 修复：确保 filters 的 key 与 type_id 严格对应
        filters[c.type_id] = await buildFilter(c.type_id, hd);
    }
  
  	const videos = [];
    for (const cat of json.data.categories) {
        videos.push(...arr2vods(cat.videos));
    }

    return JSON.stringify({
        class: classes,
        filters: filters, 
      	list: videos
    });
}

async function homeVod() {
    return JSON.stringify({ list: [] });
}

async function category(tid, pg, filter, extend) {
    const hd = await getHeaders();
    pg = pg || 1;
    extend = extend || {};

    let params = {
        type_name: tid,
        page: pg,
        sort: extend.sort || 'time',
        class: extend.class || '',
        area: extend.area || '',
        year: extend.year || ''
    };

    let query = Object.keys(params)
        .map(k => `${k}=${encodeURIComponent(params[k])}`)
        .join('&');

    const url = `${host}/api.php/app/filter/vod?${query}`;
    const resp = await req(url, { headers: hd });
    const json = JSON.parse(resp.content);

    return JSON.stringify({
        list: arr2vods(json.data || []),
        page: parseInt(pg),
        pagecount: json.totalpage || 999,
        limit: 20,
        total: (json.totalpage || 999) * 20
    });
}

/**
 * 核心修复：根据截图要求强制加入“爱情、古装、武侠”等标签
 */
async function buildFilter(type, hd) {
    // 1. 静态预设常用的类型、地区和年份
    const staticClasses = ["爱情", "古装", "武侠", "历史", "家庭", "喜剧", "动作", "科幻", "悬疑", "恐怖", "战争", "剧情"];
    const areas = ["大陆", "香港", "台湾", "美国", "日本", "韩国", "英国", "泰国"];
    const years = ["2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"];

    let filterData = [
        { 
            key: "class", 
            name: "类型", 
            value: [{ n: "全部", v: "" }].concat(staticClasses.map(i => ({ n: i, v: i }))) 
        },
        { 
            key: "area", 
            name: "地区", 
            value: [{ n: "全部", v: "" }].concat(areas.map(i => ({ n: i, v: i }))) 
        },
        { 
            key: "year", 
            name: "年份", 
            value: [{ n: "全部", v: "" }].concat(years.map(y => ({ n: y, v: y }))) 
        },
        { 
            key: "sort", 
            name: "排序", 
            value: [
                { n: "最新", v: "time" },
                { n: "人气", v: "hits" },
                { n: "评分", v: "score" },
                { n: "年份", v: "year" }
            ]
        }
    ];

    try {
        // 2. 依然保留动态获取逻辑，用来补充静态列表中没涵盖的特殊标签
        let url = `${host}/api.php/app/filter/vod?type_name=${encodeURIComponent(type)}&page=1`;
        const resp = await req(url, { headers: hd });
        const json = JSON.parse(resp.content);
        const list = json.data || [];
        
        let dynamicClasses = new Set();
        list.forEach(v => {
            if (v.vod_class) v.vod_class.split(',').forEach(c => {
                let name = c.trim();
                if (name && !staticClasses.includes(name)) dynamicClasses.add(name);
            });
        });

        dynamicClasses.forEach(c => {
            filterData[0].value.push({ n: c, v: c });
        });
    } catch (e) {}
    
    return filterData;
}

// --- 以下功能保持不变，确保播放与搜索正常 ---

async function detail(id) {
    const hd = await getHeaders();
    const resp = await req(`${host}/api.php/app/vod/get_detail?vod_id=${id}`, { headers: hd });
    const json = JSON.parse(resp.content);
    const data = json.data[0];
    let play_froms = data.vod_play_from.split('$$$');
    let play_urls = data.vod_play_url.split('$$$');
    let new_urls = [];
    for (let i = 0; i < play_froms.length; i++) {
        let from = play_froms[i];
        let items = play_urls[i].split('#');
        let formatted_items = _.map(items, (item) => {
            let [name, url] = item.split('$');
            return `${name}$${from}@1@${url}`;
        });
        new_urls.push(formatted_items.join('#'));
    }
    return JSON.stringify({
        list: [{
            vod_id: data.vod_id.toString(),
            vod_name: data.vod_name,
            vod_pic: data.vod_pic,
            type_name: data.type_name,
            vod_year: data.vod_year,
            vod_remarks: data.vod_remarks,
            vod_actor: data.vod_actor,
            vod_director: data.vod_director,
            vod_content: data.vod_content,
            vod_play_from: data.vod_play_from,
            vod_play_url: new_urls.join('$$$'),
        }]
    });
}

async function search(wd, quick, pg) {
    const hd = await getHeaders();
    const url = `${host}/api.php/app/search/index?wd=${encodeURIComponent(wd)}&page=${pg}&limit=15`;
    const resp = await req(url, { headers: hd });
    const json = JSON.parse(resp.content);
    return JSON.stringify({ list: arr2vods(json.data), page: parseInt(pg) });
}

async function play(flag, vid, flags) {
    const parts = vid.split('@');
    const play_from = parts[0];
    const need_parse = parts[1];
    const raw_url = parts[2] || vid;
    let url = '';
    if (need_parse === '1') {
        try {
            const hd = await getHeaders();
            const apiUrl = `${host}/api.php/app/decode/url/?url=${encodeURIComponent(raw_url)}&vodFrom=${play_from}`;
            const resp = await req(apiUrl, { headers: hd, timeout: 30000 });
            const json = JSON.parse(resp.content);
            if (json.data && json.data.startsWith('http')) url = json.data;
        } catch (e) {}
    }
    if (!url) url = raw_url;
    return JSON.stringify({
        parse: 0,
        url: url,
        header: { 
            'User-Agent': 'com.sunshine.tv/1.2.0 (Linux;Android 15) AndroidXMedia3/1.4.1',
            'Referer': host
        }
    });
}

function arr2vods(arr) {
    return _.map(arr, (i) => ({
        vod_id: i.vod_id.toString(),
        vod_name: i.vod_name,
        vod_pic: i.vod_pic,
        vod_remarks: i.vod_remarks,
        type_name: (i.type_name || '') + (i.vod_class ? ' ' + i.vod_class : ''),
        vod_year: i.vod_year
    }));
}

function randomStr(len, chars = '0123456789abcdef') {
    let str = '';
    for (let i = 0; i < len; i++) str += chars[_.random(0, chars.length - 1)];
    return str;
}

async function getHeaders() {
    const timestamp = Date.now().toString();
    const nonce = randomStr(16, '0123456789');
    if (!device_id) {
        device_id = await local.get('cache', device_id_cache_key);
        if (!device_id) {
            device_id = randomStr(16);
            await local.set('cache', device_id_cache_key, device_id);
        }
    }
    const signStr = `finger=SF-C3B2B41F6EFFFF9869176CF68F6790E8F07506FC88632C94B4F5F0430D5498CA&id=${pkg}&nonce=${nonce}&sk=SK-thanks&time=${timestamp}&v=${ver}`;
    const sign = Crypto.SHA256(signStr).toString().toUpperCase();
    return {
        'User-Agent': 'okhttp/4.12.0',
        'x-aid': pkg,
        'x-ave': ver,
        'x-time': timestamp,
        'x-nonc': nonce,
        'x-sign': sign,
        'x-device-id': device_id,
        'x-device-brand': 'OnePlus',
        'x-device-model': 'PJZ110'
    };
}

export default { init, home, homeVod, category, detail, search, play };