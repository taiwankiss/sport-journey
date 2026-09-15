import urllib.request, json, urllib.parse, time, os, sys

HEADERS = {'User-Agent':'WeiTrailJournal/1.0 (personal hiking log site; contact: s923446@gmail.com)'}
OUT_DIR = 'photos'
os.makedirs(OUT_DIR, exist_ok=True)

def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)

def summary(title, lang='zh'):
    url = f'https://{lang}.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(title)
    try:
        d = get_json(url)
        if d.get('type') == 'disambiguation':
            return None
        orig = (d.get('originalimage') or {}).get('source')
        thumb = (d.get('thumbnail') or {}).get('source')
        return orig or thumb
    except Exception:
        return None

# key -> list of candidate wikipedia titles to try in order (zh wikipedia)
CANDIDATES = {
 '五寮尖山': ['五寮尖'],
 '八仙山': ['八仙山'],
 '劍龍稜': ['無耳茶壺山','劍龍稜'],
 '加里山': ['加里山 (台灣)','加里山'],
 '北得拉曼 內鳥嘴山': ['內鳥嘴山','北得拉曼'],
 '合歡主峰': ['合歡山'],
 '合歡北峰': ['合歡山北峰'],
 '合歡東峰': ['合歡山東峰'],
 '合歡西峰': ['合歡山西峰'],
 '唐麻丹山': ['唐麻丹山'],
 '基隆雙塔': ['基隆山'],
 '塔曼山': ['塔曼山'],
 '大坑（五號-忘幽亭）': ['頭嵙山'],
 '奇萊主北': ['奇萊主山北峰','奇萊主山'],
 '小觀音山群峰': ['小觀音山'],
 '屋我尾（大雪山）': ['屋我尾山','大雪山 (台灣)'],
 '志佳陽大山': ['志佳陽大山'],
 '明舉山康樂O形': ['康樂山 (新北市)','明舉山'],
 '東卯山': ['東卯山'],
 '桃山': ['桃山 (台灣)','桃山'],
 '桃源谷步道(大里-大溪)': ['灣坑頭山','桃源谷'],
 '武陵三秀 池有、品田、桃山': ['品田山'],
 '水社大山': ['水社大山'],
 '波津加山': ['波津加山'],
 '烏來三山': ['拔刀爾山'],
 '燦光寮古道': ['燦光寮山'],
 '玉山主峰 (兩天一夜)': ['玉山'],
 '瑪礁古道': ['坪頂古圳步道','瑪礁古道'],
 '白毛山': ['白毛山 (台中市)','白毛山'],
 '石牛山': ['石牛山 (桃園市)','石牛山'],
 '石門山': ['石門山 (南投縣)','石門山 (台灣)'],
 '石門山主、中峰': ['石門山 (南投縣)'],
 '興福寮-向天池': ['向天池 (台北市)','大屯山'],
 '苗圃上七星': ['七星山'],
 '苗圃上七星山': ['七星山'],
 '草嶺古道': ['草嶺古道'],
 '西巒大山': ['西巒大山'],
 '觀音尖山': ['觀音山 (新北市)'],
 '貓囒山': ['貓囒山'],
 '金字碑大粗坑': ['牡丹山','金字碑古道'],
 '陽明山東西大縱走': ['七星山'],
 '雪山主東': ['雪山 (台灣)'],
 '雪山東峰': ['雪山東峰'],
 '雲森瀑布': ['雲森瀑布'],
 '馬崙山': ['馬崙山'],
 '馬那邦山': ['馬那邦山'],
 '高島縱走(第二登山口)': ['島田山'],
 '魚路古道': ['魚路古道'],
 # wishlist
 '喀拉葉山': ['喀拉業山'],
 '嘉明湖': ['嘉明湖'],
 '塔關山': ['塔關山'],
 '大、小霸尖山': ['大霸尖山'],
 '奇萊南華': ['奇萊主山南峰','南華山 (台灣)'],
 '小關山': ['小關山'],
 '屏風山': ['屏風山 (花蓮縣)','屏風山 (台灣)'],
 '庫哈諾辛山': ['庫哈諾辛山'],
 '海諾南山': ['海諾南山'],
 '玉山北峰': ['玉山北峰'],
 '畢祿山': ['畢祿山'],
 '白姑大山': ['白姑大山'],
 '羊頭山': ['羊頭山 (花蓮縣)','羊頭山'],
 '聖稜線O型': ['聖稜線','雪山 (台灣)'],
 '聖稜線小O型': ['聖稜線','品田山'],
 '郡大山': ['郡大山'],
 '關山嶺山': ['關山嶺山'],
}

def main():
    results = {}
    names = list(CANDIDATES.keys())
    for name in names:
        found = None
        for cand in CANDIDATES[name]:
            time.sleep(0.35)
            url = summary(cand)
            if url:
                found = (cand, url)
                break
        results[name] = found
        print(name, '->', found)
    json.dump(results, open('photo_urls.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
