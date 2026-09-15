import csv, json, os, re, sys
from cwa_pids import cwa_links

# BUILD_TARGET=artifact (default) -> photo URLs point at Claude Artifact's
# hosted blob assets (/_blob/<id>), used when publishing to the Artifact.
# BUILD_TARGET=pages -> photo URLs are local relative paths under
# images/mountains/, used for the GitHub Pages mirror in docs/.
TARGET = os.environ.get('BUILD_TARGET', 'artifact')
OUT_FILE = os.environ.get('BUILD_OUT', 'data.json' if TARGET == 'artifact' else 'docs/data.json')

_PA = json.load(open('photo_assets.json', encoding='utf-8'))
PHOTO_ASSETS = _PA['mountains']
PHOTO_ASSETS_THUMB = _PA.get('mountains_thumb', {})
LOCAL_PHOTOS = json.load(open('docs/photo_map.local.json', encoding='utf-8')) if TARGET == 'pages' else {}
LOCAL_PHOTOS_THUMB = json.load(open('docs/photo_thumb_map.local.json', encoding='utf-8')) if TARGET == 'pages' else {}
RACE_MEDIA = json.load(open('race_media.json', encoding='utf-8'))
RACE_MEDIA_LOCAL = json.load(open('docs/race_media.local.json', encoding='utf-8')) if TARGET == 'pages' else {}

def photo_url(name):
    if TARGET == 'pages':
        return LOCAL_PHOTOS.get(name)
    aid = PHOTO_ASSETS.get(name)
    return ('/_blob/' + aid) if aid else None

def photo_thumb_url(name):
    if TARGET == 'pages':
        return LOCAL_PHOTOS_THUMB.get(name) or LOCAL_PHOTOS.get(name)
    aid = PHOTO_ASSETS_THUMB.get(name)
    return ('/_blob/' + aid) if aid else photo_url(name)

def race_media_urls(date):
    if TARGET == 'pages':
        entry = RACE_MEDIA_LOCAL.get(date, {})
        return entry.get('photo'), entry.get('cert')
    entry = RACE_MEDIA.get(date, {})
    photo = ('/_blob/' + entry['photo']) if entry.get('photo') else None
    cert = ('/_blob/' + entry['cert']) if entry.get('cert') else None
    return photo, cert

def read_csv(path):
    with open(path, encoding='utf-8') as f:
        return list(csv.reader(f))

def clean(s):
    return (s or '').strip().replace('：', ':')

def rank_fmt(s):
    # normalise "1466 / 4820" / "1466／4820" -> "1466/4820" (some sheet rows have stray spaces
    # or a full-width slash around the "/", which renders with uneven spacing)
    s = clean(s).replace('／', '/')
    return re.sub(r'\s*/\s*', '/', s)

def num(s):
    s = clean(s).replace(',', '')
    if s in ('', '-'):
        return None
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        return None

# ---------- 路跑賽事 (roadrace) ----------
rows = read_csv('raw-sheet-export/roadrace.csv')
races = []
in_wei = False
for r in rows:
    if not any(clean(c) for c in r):
        continue
    if clean(r[0]) == 'Wei':
        in_wei = True
        continue
    if clean(r[0]) == 'Vicky':
        break
    if clean(r[0]) == '排序':
        continue
    if not in_wei:
        continue
    order, date, name, event, group, rank_total, rank_pct, group_rank, gender_rank, group_pct, official_time, personal_time, pace, shoes, note = (r + ['']*15)[:15]
    race_photo, race_cert = race_media_urls(clean(date))
    races.append({
        'order': num(order),
        'date': clean(date),
        'name': clean(name),
        'event': clean(event),
        'group': clean(group),
        'rankTotal': rank_fmt(rank_total),
        'rankPct': clean(rank_pct),
        'groupRank': rank_fmt(group_rank),
        'groupPct': clean(group_pct),
        'officialTime': clean(official_time),
        'personalTime': clean(personal_time),
        'pace': clean(pace),
        'shoes': clean(shoes),
        'note': clean(note),
        'upcoming': not clean(rank_total) and not clean(personal_time),
        'photoUrl': race_photo,
        'certUrl': race_cert,
    })
races.sort(key=lambda x: x['order'] or 0, reverse=True)

# ---------- 爬過的山 (climbed) ----------
rows = read_csv('raw-sheet-export/climbed.csv')
climbed = []
region_fix = {
    ('桃山', '2026/09/09'): '台中市',
    ('志佳陽大山', '2025/11/08'): '台中市',
    ('陽明山東西大縱走', '2025/03/21'): '台北市',
    ('武陵三秀\n池有、品田、桃山', '2024/07/19'): '台中市',
    ('合歡西峰', '2024/05/06'): '南投縣',
    ('合歡東峰', '2020/06/23'): '南投縣',
    ('合歡主峰', '2020/06/22'): '南投縣',
    ('石門山', '2019/06/08'): '南投縣',
}
for r in rows[1:]:
    if not clean(r[0]) or clean(r[0]).startswith('總累積'):
        continue
    name, date, region, title, code, myrank, style, dist, gain, time, speed, shangHe, route, mystery = (r + ['']*14)[:14]
    if not clean(name):
        continue
    region = clean(region) or region_fix.get((name, clean(date)), '')
    climbed.append({
        'name': clean(name).replace('\n', ' '),
        'date': clean(date),
        'region': region,
        'title': clean(title).replace('\n', ' / '),
        'code': [c.strip() for c in clean(code).split('\n') if c.strip()],
        'myRank': [c.strip() for c in clean(myrank).split('\n') if c.strip()],
        'style': clean(style),
        'distanceKm': num(dist),
        'gainM': num(gain),
        'totalTime': clean(time),
        'speedKmh': num(speed),
        'shangHe': num(shangHe),
        'route': clean(route).replace('\n', ' '),
        'photoUrl': photo_url(clean(name).replace('\n', ' ')),
        'photoThumbUrl': photo_thumb_url(clean(name).replace('\n', ' ')),
        'cwaLinks': cwa_links(clean(name).replace('\n', ' ')),
    })
climbed.sort(key=lambda x: x['date'], reverse=True)

# ---------- 想爬的山 (wishlist) ----------
rows = read_csv('raw-sheet-export/wantclimb.csv')
wishlist = []
wishlist_done = []
section = None

def est_hours(ref_hours):
    """上河文化參考時間 × 0.7（依個人配速估算），四捨五入到半小時"""
    hrs = round(ref_hours * 0.7 * 2) / 2
    return ('約 %g 小時' % hrs)

overlay = {
    '大、小霸尖山': {'elevation': '大霸尖山 3,490m／小霸尖山 3,419m', 'estTime': est_hours(18), 'region': '新竹縣 / 苗栗縣'},
    '聖稜線小O型': {'elevation': '最高點品田山 3,528m', 'estTime': est_hours(17), 'region': '台中市 / 新竹縣'},
    '聖稜線O型': {'elevation': '最高點雪山主峰 3,886m', 'estTime': est_hours(20), 'region': '台中市 / 新竹縣'},
    '郡大山': {'elevation': '3,278m', 'estTime': est_hours(12), 'region': '南投縣'},
    '小關山': {'elevation': '3,248m', 'estTime': est_hours(7), 'region': '高雄市'},
    '海諾南山': {'elevation': '3,173m', 'estTime': est_hours(9), 'region': '高雄市'},
    '白姑大山': {'elevation': '3,341m', 'estTime': est_hours(15), 'region': '南投縣 / 台中市'},
    '屏風山': {'elevation': '3,248m', 'estTime': est_hours(11), 'region': '花蓮縣'},
    '畢祿山': {'elevation': '3,370m', 'estTime': est_hours(11), 'region': '花蓮縣 / 南投縣'},
    '羊頭山': {'elevation': '3,033m', 'estTime': est_hours(5.5), 'region': '花蓮縣 / 南投縣'},
    '塔關山': {'elevation': '3,219m', 'estTime': est_hours(5), 'region': '高雄市'},
    '關山嶺山': {'elevation': '3,174m', 'estTime': est_hours(2.5), 'region': '高雄市'},
    '庫哈諾辛山': {'elevation': '3,114m', 'estTime': est_hours(6), 'region': '高雄市'},
    '嘉明湖': {'elevation': '向陽山 3,601m／三叉山 3,495m／嘉明湖畔 約3,150m', 'estTime': est_hours(15.5), 'region': '台東縣'},
    '玉山北峰': {'elevation': '3,855m', 'estTime': est_hours(11), 'region': '南投縣'},
    '喀拉業山': {'elevation': '3,133m', 'estTime': est_hours(11), 'region': '台中市'},
    '奇萊南華': {'elevation': '奇萊南峰 3,357m／南華山 3,182m', 'estTime': est_hours(12), 'region': '花蓮縣 / 南投縣'},
}
# 入園申請核實結果（查了雪霸/玉山/太魯閣國家公園官網與林務局公告後校正，
# 原表單有幾筆誤植）：
#   郡大山　　　位於丹大野生動物重要棲息環境，只需入山證，不需入園證 → 清空
#   塔關山／關山嶺山　屬特別景觀區，只需入山證，不需入園證 → 清空
#   庫哈諾辛山　位於生態保護區，需入園證 → 補上
#   玉山北峰　　在玉山國家公園內，需入園證＋入山證 → 補上
#   喀拉業山（喀拉葉山，原表單誤打）位於雪霸國家公園內，需入園證 → 補上
#   奇萊南華　　在太魯閣國家公園生態保護區內，需入園證 → 補上
#   嘉明湖　　　嘉明湖國家步道本身不需入園證，但向陽山屋/單日名額競爭激烈、
#               需提前申請，仍加註提醒
permit_override = {
    '郡大山': '',
    '塔關山': '',
    '關山嶺山': '',
    '庫哈諾辛山': '入園申請',
    '玉山北峰': '入園申請',
    '喀拉業山': '入園申請',
    '奇萊南華': '入園申請',
}
permit_note = {
    '嘉明湖': '不需入園證，但向陽山屋／單日名額競爭激烈，需提前上「臺灣登山申請一站式服務網」申請入山證＋向陽名額',
}
NAME_FIX = {'喀拉葉山': '喀拉業山'}  # 原表單錯字校正
for r in rows:
    name = NAME_FIX.get(clean(r[0]), clean(r[0]))
    if name == '待完成':
        section = 'todo'
        continue
    if name == '已完成':
        section = 'done'
        continue
    if not name:
        continue
    if section == 'todo':
        route, weather, apply_, parking, drive_time, trailhead, stay, dist, gain, note, elevation, esttime = (r[1:13] + ['']*12)[:12]
        ov = overlay.get(name, {})
        need_permit = permit_override[name] if name in permit_override else clean(apply_)
        note_text = clean(note)
        if name in permit_note:
            note_text = (note_text + '；' if note_text else '') + permit_note[name]
        wishlist.append({
            'name': name,
            'route': clean(route).replace('\n', ' '),
            'needPermit': need_permit,
            'parking': clean(parking),
            'driveTime': clean(drive_time),
            'trailhead': clean(trailhead),
            'stay': clean(stay),
            'distance': clean(dist),
            'gain': clean(gain),
            'note': note_text,
            'elevation': clean(elevation) or ov.get('elevation', ''),
            'estTime': clean(esttime) or ov.get('estTime', ''),
            'region': ov.get('region', ''),
            'photoUrl': photo_url(name),
            'photoThumbUrl': photo_thumb_url(name),
            'cwaLinks': cwa_links(name),
        })
    elif section == 'done':
        wishlist_done.append(name.replace('\n', ' '))

# ---------- 陽明山大縱走 (yms) ----------
rows = read_csv('raw-sheet-export/yms.csv')
header = rows[0]
dates = [clean(d) for d in header[1:] if clean(d)]
n_attempts = len(dates)
checkpoints = []
i = 1
while i < len(rows):
    label = clean(rows[i][0])
    if not label or label in ('Total', '備註'):
        break
    times = (rows[i][1:1+n_attempts] + ['']*n_attempts)[:n_attempts]
    next_label = clean(rows[i+1][0]) if i+1 < len(rows) else ''
    if next_label.startswith('⬆') or 'time+' in next_label:
        splits = (rows[i+1][1:1+n_attempts] + ['']*n_attempts)[:n_attempts]
        i += 2
    else:
        splits = ['']*n_attempts
        i += 1
    checkpoints.append({
        'name': label,
        'times': [clean(t) for t in times],
        'splits': [clean(s) for s in splits],
    })

total_row = None
note_row = None
for r in rows:
    if clean(r[0]) == 'Total':
        total_row = (r[1:1+n_attempts] + ['']*n_attempts)[:n_attempts]
    if clean(r[0]) == '備註':
        note_row = (r[1:1+n_attempts] + ['']*n_attempts)[:n_attempts]

yms = []
for idx, d in enumerate(dates):
    yms.append({
        'date': d,
        'totalTime': clean(total_row[idx]) if total_row else '',
        'note': clean(note_row[idx]) if note_row else '',
        'checkpoints': [{'name': c['name'], 'time': clean(c['times'][idx]), 'split': clean(c['splits'][idx])} for c in checkpoints],
        'dnf': not clean(total_row[idx]) if total_row else False,
    })
yms.sort(key=lambda x: x['date'], reverse=True)

# ---------- 登山物品檢查 template ----------
rows = read_csv('raw-sheet-export/checklist.csv')
cats = ['衣物包', '單攻包', '當天確認']
template_items = []
for r in rows[1:]:
    for ci, cat in enumerate(cats):
        v = clean(r[ci]) if ci < len(r) else ''
        if v:
            template_items.append({'text': v, 'category': cat})

data = {
    'syncedAt': '2026-09-15',
    'races': races,
    'climbed': climbed,
    'wishlist': wishlist,
    'wishlistDone': wishlist_done,
    'yms': yms,
    'checklistTemplate': template_items,
}

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print('races', len(races))
print('climbed', len(climbed))
print('wishlist', len(wishlist))
print('wishlistDone', len(wishlist_done))
print('yms', len(yms))
print('template items', len(template_items))
