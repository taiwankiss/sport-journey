"""Build docs/index.html (GitHub Pages variant) from index.html (Artifact variant).

Differences from index.html:
  - Full HTML5 document shell (<!doctype>/<html>/<head>/<body>) with a
    viewport meta tag — the Artifact platform injects this automatically
    at publish time, but GitHub Pages serves the file as-is, so it needs
    its own or mobile browsers render at a wide desktop layout viewport
    and zoom out (tiny illegible text).
  - Hero banner points at the local images/banner.jpg instead of the
    Claude Artifact blob URL.

Run after every edit to index.html that should also ship to the GitHub
Pages mirror: `python3 make_docs_html.py`
"""
import re

BANNER_BLOB_RE = re.compile(r'url\("/_blob/[a-f0-9]+"\)')

src = open('index.html', encoding='utf-8').read()

# swap the hero banner to the local relative path
out = BANNER_BLOB_RE.sub('url("images/banner.jpg")', src, count=1)

# wrap in a full HTML5 document shell
out = out.replace(
    '<title>山徑運動誌</title>',
    '<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    '<title>山徑運動誌</title>',
    1,
)
out = out.replace('</style>\n\n<div class="hero">', '</style>\n</head>\n<body>\n\n<div class="hero">', 1)
assert out.rstrip().endswith('</script>'), 'expected file to end with </script>'
out = out.rstrip() + '\n</body>\n</html>\n'

open('docs/index.html', 'w', encoding='utf-8').write(out)
print('wrote docs/index.html (%d bytes)' % len(out))
