/*
@header({
  searchable: 1,
  filterable: 0,
  quickSearch: 0,
  title: '夸克影院'
})
*/

var rule = {
	title: '夸克影院',
	host: 'https://www.qkmov.cc', //发布页http://www.taoju.vip
	searchable: 1,
	quickSearch: 0,
	filterable: 0,
	url: '/type/fyclass-fypage.html',
	class_name: "电影&电视剧&动漫&综艺",
	class_url: "20&21&22&23",
	searchUrl: '/search/-------------.html?wd=**',
	play_parse: true,
	limit: 6,
	推荐:'*',
    一级:'.col-md-6.col-sm-4.col-xs-3;a&&title;a&&data-original;.pic-text&&Text;a&&href',
	二级: async function () {
        let {input,pdfa,pdfh,pd} = this;
        input = input.replace(/video/g, 'play').replace(/.html/g, '-1-1.html')
        let html = await request(input);
        let VOD = {};
        VOD.vod_name = pdfh(html, '.stui-content__detail .title&&Text');
        VOD.vod_content = pdfh(html, '.detail&&Text');
        let playlist = pdfa(html, '.cloud-links a')
        let  play_urls = []
        let  play_from = []
        playlist.map((item) => {                    
             play_urls.push(pdfh(item,'a&&title') + '$' + pdfh(item,'a&&href'));
             play_from.push(pdfh(item,'a&&title'))                       
            });             
        VOD.vod_play_from =play_from.join('$$$');         
        VOD.vod_play_url = play_urls.join('#');
        return VOD
    },
	lazy:async function (){
        let {input} = this;
        if(/pan.quark.cn/.test(input)){
            return {parse: 0,jx: 0,url: 'push://' + input}       
        }else{
            return {parse: 1,jx: 0,url: input}
        }
    },
	搜索: async function () {
        let {input,pdfa,pdfh,pd} = this;
        let html = await request(input);
        let d = [];
        let data = pdfa(html, '.stui-vodlist__media li');
        data.forEach((it) => {
            d.push({
                title: pdfh(it, '.thumb a&&title'),
                pic_url: pd(it, '.thumb a&&data-original'),
                desc: pdfh(it, '.pic-text&&Text'),
                url: pd(it, '.thumb a&&href'),
                content: pdfh(it, '.hl-item-content&&p:eq(0)&&Text'),
            })
        });
        return setResult(d)
    }
}