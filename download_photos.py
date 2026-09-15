import json, urllib.request, urllib.parse, os, time, re

HEADERS = {'User-Agent':'WeiTrailJournal/1.0 (personal hiking log site; contact: s923446@gmail.com)'}
OUT_DIR = 'photos'
os.makedirs(OUT_DIR, exist_ok=True)

def filename_from_url(url):
    path = urllib.parse.urlparse(url).path
    # commons file urls end in /<Filename.ext> (possibly after /thumb/x/xx/Filename.ext/NNNpx-Filename.ext)
    parts = path.split('/')
    last = parts[-1]
    if re.match(r'^\d+px-', last):
        last = re.sub(r'^\d+px-', '', last)
    return urllib.parse.unquote(last)

def safe_slug(name):
    # keep unicode (CJK) chars; only strip filesystem-unsafe punctuation
    name = re.sub(r'[\\/:*?"<>|,()（）、\s]+', '_', name)
    return name.strip('_')

results = json.load(open('photo_urls.json', encoding='utf-8'))
manifest = {}
for name, val in results.items():
    if not val:
        continue
    cand, url = val
    fn = filename_from_url(url)
    dl_url = 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(fn) + '?width=1000'
    slug = safe_slug(name)
    ext = os.path.splitext(fn)[1].lower()
    if ext not in ('.jpg', '.jpeg', '.png'):
        ext = '.jpg'
    out_path = os.path.join(OUT_DIR, slug + ext)
    try:
        req = urllib.request.Request(dl_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
            final_url = r.geturl()
        with open(out_path, 'wb') as f:
            f.write(data)
        manifest[name] = {'file': out_path, 'bytes': len(data), 'source_file': fn, 'commons_title': cand, 'final_url': final_url}
        print(f'{name} -> {out_path} ({len(data)/1024:.0f} KB)')
    except Exception as e:
        print(f'{name} FAILED: {e}')
    time.sleep(0.3)

json.dump(manifest, open('photo_manifest.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('done', len(manifest))
