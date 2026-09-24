import re
NOTE = '<span class="ja">※写真はイメージです（公開時はお店の写真に差し替えます）</span><span class="en">Sample photo — to be replaced with the shop’s own.</span>'
def block(s, start):
    """return (i, j) span of the element starting at the exact substring `start` (must begin with '<tag')."""
    i = s.index(start); tag = re.match(r'<(\w+)', start).group(1)
    depth = 0; pos = i
    pat = re.compile(r'<(/?)%s\b[^>]*?(/?)>' % tag)
    for m in pat.finditer(s, i):
        if m.group(1): depth -= 1
        elif not m.group(2): depth += 1
        if depth == 0: return i, m.end()
    raise ValueError('unclosed ' + start)
def replace_block(s, start, new):
    i, j = block(s, start); return s[:i] + new + s[j:]
def add_css(s, css):
    k = s.rindex('</style>'); return s[:k] + css + '\n' + s[k:]
def fig(cls='hphoto', src='hero.jpg'):
    return f'<figure class="{cls}"><img src="{src}" alt=""><figcaption>{NOTE}</figcaption></figure>'
def credit(s):
    return s.replace('Noto Emoji (Apache 2.0)', 'Unsplash (sample images)').replace('Illustrations: Unsplash', 'Photos: Unsplash')
