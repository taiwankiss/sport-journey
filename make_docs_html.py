"""Build docs/index.html (GitHub Pages variant) from index.html (Artifact variant).

Differences from index.html:
  - Full HTML5 document shell (<!doctype>/<html>/<head>/<body>) with a
    viewport meta tag — the Artifact platform injects this automatically
    at publish time, but GitHub Pages serves the file as-is, so it needs
    its own or mobile browsers render at a wide desktop layout viewport
    and zoom out (tiny illegible text).
  - Hero banner points at the local images/banner.jpg instead of the
    Claude Artifact blob URL.
  - Real favicon / apple-touch-icon / web-manifest links (the Artifact
    platform's `favicon` param is emoji-only, so the custom PNG icon can
    only be wired up for this standalone GitHub Pages copy).

Run after every edit to index.html that should also ship to the GitHub
Pages mirror: `python3 make_docs_html.py`
"""
import re

BANNER_BLOB_RE = re.compile(r'url\("/_blob/[a-f0-9]+"\)')
TITLE_RE = re.compile(r'<title>.*?</title>')

ICON_LINKS = '''<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.png">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#14100E">'''

src = open('index.html', encoding='utf-8').read()

# swap the hero banner to the local relative path
out = BANNER_BLOB_RE.sub('url("images/banner.jpg")', src, count=1)

# wrap in a full HTML5 document shell + favicon/manifest links, right after <title>
m = TITLE_RE.search(out)
assert m, 'expected a <title> tag'
out = (
    out[:m.start()]
    + '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    + m.group(0) + '\n' + ICON_LINKS
    + out[m.end():]
)
out = out.replace('</style>\n\n<div class="hero">', '</style>\n</head>\n<body>\n\n<div class="hero">', 1)
assert out.rstrip().endswith('</script>'), 'expected file to end with </script>'
out = out.rstrip() + '\n</body>\n</html>\n'

open('docs/index.html', 'w', encoding='utf-8').write(out)
print('wrote docs/index.html (%d bytes)' % len(out))
