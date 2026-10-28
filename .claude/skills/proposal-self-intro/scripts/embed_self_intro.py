#!/usr/bin/env python3
"""Embed the self-introduction (About me, SilkRoad 2040, Let's connect) into a proposal page.

Source of truth: 05_sales/profile/self-introduction.html (portable CSS between
/* embed:start */ and /* embed:end */, sections #person, #silk-road, #connect).

The proposal is edited in place (or written to --out). Everything the script adds is
fenced with self-intro markers, so --replace can strip it and re-embed after the
self-introduction changes.

Usage:
  python3 embed_self_intro.py --intro 05_sales/profile/self-introduction.html \
      --proposal <proposal index.html> --partner MorTech \
      [--bridge-en "..." --bridge-zh "..." --bridge-ja "..."] [--makers hide] [--replace]
"""
import argparse
import re
import sys

CSS_START, CSS_END = '/* self-intro:start */', '/* self-intro:end */'
SCROLL_MARK = '/* self-intro:scroll */'
IDS = ('about', 'silk-road', 'connect')
# Proposal tokens that mean the same thing as the intro's tokens.
SYNONYMS = {
    'core': ['accent'], 'core-ink': ['accent-ink'],
    'open': ['job2', 'second', 'teal'], 'open-ink': ['job2-ink', 'second-ink', 'teal-ink'],
    'next': ['fail', 'muted'],
}
# Class names both pages use on purpose (same role); anything else that overlaps is reported.
SHARED_OK = {'band', 'inner', 'head', 'eyebrow', 'lead', 'note', 'white', 'alt', 'en', 'zh', 'ja', 'n'}


def die(msg):
    sys.exit(f'embed_self_intro: {msg}')


def section(html, sid):
    m = re.search(r'<section class="band[^"]*" id="' + re.escape(sid) + r'">.*?</section>\n', html, re.S)
    if not m:
        die(f'section #{sid} not found in the intro')
    return m.group(0)


def root_tokens(css, dark=False):
    """Token name -> value from the light :root block (or the dark media block)."""
    if dark:
        m = re.search(r'@media \(prefers-color-scheme: dark\)\s*\{\s*:root:not\(\[data-theme="light"\]\)\s*\{(.*?)\}', css, re.S)
        return dict(re.findall(r'--([\w-]+)\s*:\s*([^;]+);', m.group(1))) if m else {}
    # every bare :root block (the publish skeleton adds one of its own before the page's)
    out = {}
    for body in re.findall(r'(?<![\w-]):root\s*\{(.*?)\}', css, re.S):
        out.update(re.findall(r'--([\w-]+)\s*:\s*([^;]+);', body))
    return out


def strip_previous(p):
    a, b = p.find(CSS_START), p.find(CSS_END)
    if a != -1 and b != -1:
        p = p[:a] + p[b + len(CSS_END):]
    for sid in IDS:
        p = re.sub(r'<section class="band[^"]*" id="' + sid + r'">.*?</section>\n\n?', '', p, flags=re.S)
    p = p.replace('    <div class="bridge-in" aria-hidden="true"></div>\n', '')
    p = re.sub(r'<script>' + re.escape(SCROLL_MARK) + r'.*?</script>\n?', '', p, flags=re.S)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--intro', required=True)
    ap.add_argument('--proposal', required=True)
    ap.add_argument('--out')
    ap.add_argument('--partner', required=True, help='Partner name as it should appear, e.g. MorTech')
    ap.add_argument('--bridge-en'); ap.add_argument('--bridge-zh'); ap.add_argument('--bridge-ja')
    ap.add_argument('--insert-before', help='id of the first content section after the cover (default: first section after </header>)')
    ap.add_argument('--contact-before', help='id of the appendix section (default: method, else the footer)')
    ap.add_argument('--makers', choices=['china', 'hide'], default='china', help='hide for non-China partners (N:N trade)')
    ap.add_argument('--replace', action='store_true', help='remove a previous embed first')
    a = ap.parse_args()

    intro = open(a.intro, encoding='utf-8').read()
    p = open(a.proposal, encoding='utf-8').read()
    report = []

    if CSS_START in p or 'id="silk-road"' in p:
        if not a.replace:
            die('the proposal already contains the self-introduction; pass --replace to re-embed')
        p = strip_previous(p)
        if 'id="silk-road"' in p:
            die('an older embed without markers is present; start from the pre-embed version of the proposal')
    for sid in IDS:
        if f'id="{sid}"' in p:
            die(f'the proposal already has an element with id="{sid}"')

    # ---- language root (.doc[data-lang] in the proposal series) ----
    m = re.search(r'\.([A-Za-z][\w-]*)\[data-lang="', p)
    root = m.group(1) if m else 'doc'

    # ---- portable CSS ----
    m = re.search(r'/\* embed:start[^*]*\*/(.*?)/\* embed:end \*/', intro, re.S)
    if not m:
        die('embed markers not found in the intro CSS')
    css = '\n'.join(l for l in m.group(1).strip('\n').split('\n') if not l.startswith('@media (min-width: 1000px)'))
    css = css.replace('.intro[data-lang=', f'.{root}[data-lang=')

    # ---- tokens: reuse the proposal's, map synonyms, scope the rest ----
    ptok = root_tokens(p)
    itok, itok_dark = root_tokens(intro), root_tokens(intro, dark=True)
    scoped_light, scoped_dark = [], []
    for t in sorted(set(re.findall(r'var\(--([\w-]+)\)', css))):
        if t in ptok:
            continue
        syn = next((s for s in SYNONYMS.get(t, []) if s in ptok), None)
        if syn:
            css = re.sub(r'var\(--' + re.escape(t) + r'\)', f'var(--{syn})', css)
            report.append(f'token --{t} -> --{syn}')
        elif t in itok:
            scoped_light.append(f'--{t}: {itok[t]};')
            if t in itok_dark:
                scoped_dark.append(f'--{t}: {itok_dark[t]};')
            report.append(f'token --{t} scoped to the embedded sections')
        else:
            report.append(f'WARNING token --{t} is undefined in both pages')
    scope = ', '.join('#' + i for i in IDS)
    token_css = ''
    if scoped_light:
        token_css = f'{scope} {{ {" ".join(scoped_light)} }}\n'
        if scoped_dark:
            dark_vals = ' '.join(scoped_dark)
            os_dark = ', '.join(':root:not([data-theme="light"]) #' + i for i in IDS)
            toggle_dark = ', '.join(':root[data-theme="dark"] #' + i for i in IDS)
            token_css += (f'@media (prefers-color-scheme: dark) {{ {os_dark} {{ {dark_vals} }} }}\n'
                          f'{toggle_dark} {{ {dark_vals} }}\n')

    # ---- layout numbers from the proposal ----
    m = re.search(r'\.inner\s*\{[^}]*max-width:\s*(\d+)px', p)
    inner = int(m.group(1)) if m else 1120
    m = re.search(r'@media \(max-width:\s*(\d+)px\)', p)
    bp = int(m.group(1)) if m else 860

    # ---- bridge copy ----
    partner = a.partner
    b_en = a.bridge_en or f'Step 1 is Japan.<br>We want to start it with {partner}.'
    b_zh = a.bridge_zh or f'第一步是日本。<br>我们希望和 {partner} 一起开始。'
    b_ja = a.bridge_ja or f'最初の一歩は日本です。<br>{partner}様と一緒に始めたいと考えています。'

    # ---- sections ----
    person = section(intro, 'person').replace('class="band" id="person"', 'class="band white" id="about"', 1)
    person = person.replace('<h1 class="name">', '<h2 class="name">', 1).replace('</span></h1>', '</span></h2>', 1)
    silk = section(intro, 'silk-road')
    connect = section(intro, 'connect').replace('class="band" id="connect"', 'class="band white" id="connect"', 1)
    if a.makers == 'hide':
        silk = re.sub(r'\s*<div class="phase"><h3><span class="ln mk"></span>.*?</ol></div>', '', silk, count=1, flags=re.S)
        silk = re.sub(r'\s*<path class="r r-src"[^>]*/>', '', silk)
        silk = re.sub(r'\s*<rect class="m-fill"[^>]*/>', '', silk)
        silk = re.sub(r'\s*<text class="num mk"[^>]*>CN</text>', '', silk)
        silk = silk.replace(' Makers in China.', '')
        silk = silk.replace('中国・ASEANのメーカーと買い手', 'メーカーと買い手')
        css += '\n.phases { grid-template-columns: repeat(3, minmax(0, 1fr)); }'
        report.append('makers (China) hidden')
    m = re.search(r'(\n\s*</div>\n  </div>\n</section>\n)$', silk)
    if not m:
        die('could not find the end of the SilkRoad section')
    bridge = (f'\n    <div class="bridge"><p><span class="en">{b_en}</span><span class="zh">{b_zh}</span>'
              f'<span class="ja">{b_ja}</span></p></div>')
    silk = silk[:m.start()] + '\n    </div>' + bridge + '\n  </div>\n</section>\n'

    # where to insert
    if a.insert_before:
        target = re.search(r'<section[^>]*id="' + re.escape(a.insert_before) + r'"[^>]*>', p)
    else:
        h = p.find('</header>')
        target = re.compile(r'<section[^>]*>').search(p, h if h != -1 else 0)
    if not target:
        die('could not find the section to insert before; pass --insert-before')
    next_tag = target.group(0)
    m = re.search(r'id="([^"]+)"', next_tag)
    if not m:
        die('the section after the cover needs an id; pass --insert-before')
    next_id = m.group(1)
    after = p[target.end():]
    if not after.startswith('\n  <div class="inner">\n'):
        die(f'#{next_id} does not start with <div class="inner">; add the bridge line by hand')
    p = (p[:target.start()] + person + '\n' + silk + '\n' + next_tag
         + '\n  <div class="inner">\n    <div class="bridge-in" aria-hidden="true"></div>\n'
         + after[len('\n  <div class="inner">\n'):])
    report.append(f'About me + SilkRoad 2040 inserted before #{next_id}')

    cid = a.contact_before or ('method' if 'id="method"' in p else None)
    if cid:
        t = re.search(r'<section[^>]*id="' + re.escape(cid) + r'"[^>]*>', p)
        if not t:
            die(f'#{cid} not found for the contact block')
        p = p[:t.start()] + connect + '\n' + p[t.start():]
        report.append(f'Let\'s connect inserted before #{cid}')
    else:
        f = p.find('<footer')
        if f == -1:
            die('no appendix or footer found; pass --contact-before')
        p = p[:f] + connect + '\n' + p[f:]
        report.append('Let\'s connect inserted before the footer')

    # ---- CSS block ----
    css_block = f'''{CSS_START}
/* About me + SilkRoad 2040 + Let's connect, from 05_sales/profile/self-introduction.html (proposal-self-intro skill) */
{token_css}{css}
.{root}[data-lang="zh"] .tag, .{root}[data-lang="ja"] .tag {{ letter-spacing: 0.06em; text-transform: none; }}
.{root} .name {{ font-family: var(--display-latin); }}
.{root}[data-lang="zh"] .name {{ font-family: "Newsreader", "Noto Serif SC", serif; }}
.{root}[data-lang="ja"] .name {{ font-family: "Newsreader", "Noto Serif JP", serif; }}
/* bridge: the route line runs from the SilkRoad band into the next section */
.band.silk {{ padding-bottom: 0; }}
.band.silk + #{next_id} {{ padding-top: 0; }}
.bridge {{ border-left: 3.5px solid var(--paper); padding: 8px 0 clamp(56px, 8vw, 96px) 22px; margin-top: 8px; }}
.bridge p {{ font-family: var(--display-latin); font-size: clamp(1.5rem, 3vw, 2.2rem); line-height: 1.3; color: var(--paper); max-width: 24em; }}
.{root}[data-lang="zh"] .bridge p {{ font-family: "Newsreader", "Noto Serif SC", serif; }}
.{root}[data-lang="ja"] .bridge p {{ font-family: "Newsreader", "Noto Serif JP", serif; }}
.bridge-in {{ height: clamp(56px, 8vw, 96px); border-left: 3.5px solid var(--ink); margin-bottom: calc(-1 * clamp(36px, 5vw, 56px) + 14px); }}
@media (min-width: {inner + 80}px) {{ .silkmap {{ margin-right: calc(({inner}px - 100vw) / 2); }} }}
@media (max-width: {bp}px) {{
  .phases {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .mapscroll svg {{ width: 680px; max-width: none; }}
  .silkmap .swipe {{ display: inline; }}
  .person {{ grid-template-columns: minmax(0, 1fr); }}
  .portrait {{ width: 104px; }}
}}
{CSS_END}
'''
    s_end = p.find('</style>')
    if s_end == -1:
        die('no <style> block in the proposal')
    # after the proposal's last </style> so the embedded rules win ties
    s_end = p.rfind('</style>')
    p = p[:s_end] + css_block + p[s_end:]

    # ---- map scroll starts at Japan on phones ----
    p = p.rstrip('\n') + ('\n<script>' + SCROLL_MARK + '\n(function () { var ms = document.querySelector(".mapscroll"); '
                          'if (ms) ms.scrollLeft = ms.scrollWidth; })();\n</script>\n')

    # ---- class collisions worth a look ----
    def classes(text):
        return set(re.findall(r'\.([A-Za-z][\w-]*)', re.sub(r'url\([^)]*\)|\d+\.\d+', '', text)))

    def unscoped(text):  # classes that open a selector, so they style the element wherever it sits
        out = set()
        for sel in re.findall(r'([^{}@;]+)\{', re.sub(r'/\*.*?\*/', '', text, flags=re.S)):
            for part in sel.split(','):
                first = re.split(r'[\s>+~]+', part.strip())[0]
                found = re.findall(r'\.([A-Za-z][\w-]*)', first)
                if len(found) == 1:  # .a.b only matches when both are present
                    out.update(found)
        return out
    prop_css = '\n'.join(re.findall(r'<style>(.*?)</style>', p.replace(css_block, ''), re.S))
    loose = unscoped(css) | unscoped(prop_css)
    clash = sorted(c for c in (classes(css) & classes(prop_css)) - SHARED_OK - {root} if c in loose)
    if clash:
        report.append('CHECK class names used by both pages: ' + ', '.join('.' + c for c in clash))

    open(a.out or a.proposal, 'w', encoding='utf-8').write(p)
    report.append('images to publish: img/yuhei.jpg, img/qr-wechat.png, img/qr-line.png, img/qr-whatsapp.png')
    print('\n'.join(report))


if __name__ == '__main__':
    main()
