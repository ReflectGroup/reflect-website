#!/usr/bin/env python3
"""Build the Insights section (blog) of reflectgroup.com.au from Markdown sources.

Sources:  insights-src/YYYY-MM-DD-slug.md   front matter: title, summary (optional: slug)
Config:   insights-src/_config.json         {"mailerlite": {"account": "...", "form": "..."}}  (subscribe form shown only when set)
Output:   insights/index.html, insights/<slug>/index.html, insights/feed.xml; sitemap.xml updated.

Only articles dated on or before today (Sydney time) are published, unless --all is given (local preview).
Usage:    python3 tools/build_insights.py [--all] [--today YYYY-MM-DD]
"""
import sys, os, re, json, html, datetime, glob
from zoneinfo import ZoneInfo
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = os.path.join(ROOT, 'insights-src'), os.path.join(ROOT, 'insights')
SITE = 'https://www.reflectgroup.com.au'
AUTHOR = 'Petar Djolic'

def parse(path):
    raw = open(path, encoding='utf8').read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', raw, re.S)
    meta, body = {}, raw
    if m:
        for line in m.group(1).splitlines():
            if ':' in line:
                k, v = line.split(':', 1); meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    base = os.path.basename(path)[:-3]
    meta.setdefault('date', base[:10]); meta.setdefault('slug', base[11:])
    meta['date_obj'] = datetime.date.fromisoformat(meta['date'])
    meta['html'] = markdown.markdown(body, extensions=['extra', 'sane_lists', 'smarty'])
    words = len(re.findall(r'\w+', body)); meta['minutes'] = max(1, round(words / 220))
    return meta

def fdate(d): return f"{d.day} {d.strftime('%B %Y')}"

HEAD = '''<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}"><meta property="og:site_name" content="Reflect Group"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}"><meta property="og:image" content="{site}/images/og-insights.jpg"><meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Reflect Group · Insights" href="/insights/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@200;300;400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300&display=swap">
<style>
:root{{--paper:#faf8f4;--paper-2:#f1ece3;--ink:#2b2926;--ink-2:#5f5750;--mute:#857868;--bronze:#8a7557;--line:#c9b9a0;--body:'Manrope',system-ui,sans-serif;--display:'Newsreader',Georgia,serif;color-scheme:light}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-weight:300;line-height:1.65;-webkit-font-smoothing:antialiased}}
.wrap{{max-width:780px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}}
header.top{{padding:1.6rem 0;display:flex;align-items:center;justify-content:space-between;gap:1rem}}
.brand{{display:inline-flex;align-items:center;gap:.7rem;text-decoration:none;color:inherit;border:0}}
.brand canvas{{width:40px;height:40px;display:block}}
.brand b{{font-weight:300;font-size:1.05rem;line-height:1.05;letter-spacing:.01em}}
.brand b small{{display:block;font-size:.62em;color:var(--mute);letter-spacing:.1em;text-transform:uppercase;margin-top:.15rem}}
.toplinks a{{font-size:.72rem;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-2);border:0;margin-left:1.2rem}}
.sheet{{background:var(--paper-2);border-top:1px solid var(--bronze);border-bottom:1px solid var(--bronze);border-radius:clamp(18px,2.4vw,32px);box-shadow:0 1px 2px rgba(43,41,38,.04),0 10px 30px -8px rgba(43,41,38,.14);padding:clamp(2.6rem,6vw,4rem) 0;margin:.6rem 0}}
.eyebrow{{font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--bronze);font-weight:500}}
h1{{font-family:var(--display);font-weight:400;font-size:clamp(2.1rem,5vw,3.4rem);line-height:1.08;letter-spacing:-.01em;margin:.7rem 0 1rem;text-wrap:balance}}
.lede{{font-family:var(--display);font-size:clamp(1.15rem,2vw,1.35rem);line-height:1.45;color:var(--ink-2);margin:0;padding-left:1.1rem;border-left:1px solid var(--bronze);max-width:60ch}}
.meta{{font-size:.78rem;color:var(--mute);margin-top:1.4rem}}
article.body{{padding:clamp(2.4rem,5vw,3.4rem) 0 1rem}}
article.body h2{{font-family:var(--display);font-weight:400;font-size:1.6rem;line-height:1.15;margin:2.4rem 0 .7rem}}
article.body h3{{font-size:.78rem;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:var(--bronze);margin:1.8rem 0 .4rem}}
article.body p,article.body li{{color:var(--ink-2);font-size:1.02rem;max-width:66ch}}
article.body ul,article.body ol{{padding-left:1.2rem}} article.body li{{margin:.3rem 0}}
article.body blockquote{{margin:1.8rem 0;padding:1.2rem 1.4rem;background:var(--paper-2);border-left:2px solid var(--bronze);border-radius:0 14px 14px 0;font-family:var(--display);font-size:1.2rem;color:var(--ink)}}
article.body blockquote p{{color:var(--ink);margin:0}}
article.body table{{border-collapse:collapse;margin:1.4rem 0;font-size:.92rem;width:100%}}
article.body th,article.body td{{border-bottom:1px solid var(--line);padding:.55rem .6rem;text-align:left;color:var(--ink-2)}} article.body th{{color:var(--ink);font-weight:500}}
a{{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}}a:hover{{border-color:var(--bronze)}}
.author{{display:flex;gap:1rem;align-items:center;margin:2.6rem 0 0;padding:1.3rem 1.4rem;background:var(--paper-2);border:1px solid var(--line);border-radius:16px}}
.author canvas{{width:52px;height:52px;flex:none}} .author p{{margin:0;font-size:.9rem;color:var(--ink-2)}} .author b{{font-weight:500;color:var(--ink)}}
.sub{{margin:1.2rem 0 0;padding:1.6rem 1.5rem;background:var(--ink);color:#e6dfd3;border-radius:18px}}
.sub h2{{font-family:var(--display);font-weight:400;font-size:1.45rem;color:#faf8f4;margin:.3rem 0 .4rem}} .sub .eyebrow{{color:#d6b98a}} .sub p{{margin:0 0 1rem;font-size:.92rem;color:#e6dfd3}}
.sub form{{display:flex;gap:.6rem;flex-wrap:wrap}} .sub input[type=email]{{flex:1 1 220px;padding:.85rem 1rem;border-radius:999px;border:1px solid #6b5740;background:#34312d;color:#faf8f4;font:inherit;font-size:.95rem}}
.sub button{{padding:.85rem 1.4rem;border-radius:999px;border:0;background:linear-gradient(90deg,#8a7557,#c9a97a 50%,#8a7557);background-size:250% 100%;color:#faf8f4;font:inherit;font-size:.74rem;letter-spacing:.2em;text-transform:uppercase;cursor:pointer}}
.sub .fine{{font-size:.74rem;color:#b3a898;margin:.8rem 0 0}} .sub .fine a{{color:#d6b98a;border-color:#6b5740}}
.cta{{display:inline-flex;align-items:center;gap:.6rem;margin-top:1.4rem;text-decoration:none;font-size:.76rem;letter-spacing:.2em;text-transform:uppercase;color:var(--paper);background:var(--bronze);padding:.95rem 1.6rem;border-radius:999px;border:0}}
.list{{list-style:none;margin:0;padding:0;display:grid;gap:1rem}}
.list li a{{display:block;padding:1.4rem 1.5rem 1.5rem;background:var(--paper);border:1px solid var(--line);border-radius:16px;box-shadow:0 1px 2px rgba(43,41,38,.04),0 10px 24px -12px rgba(43,41,38,.14);transition:transform .45s cubic-bezier(.2,.7,.2,1),box-shadow .45s ease,border-color .45s ease}}
.list li a:hover{{transform:translateY(-4px);border-color:var(--bronze);box-shadow:0 2px 4px rgba(43,41,38,.05),0 18px 36px -12px rgba(43,41,38,.22)}}
.list h2{{font-family:var(--display);font-weight:400;font-size:1.55rem;line-height:1.15;margin:.45rem 0 .4rem;color:var(--ink)}}
.list p{{margin:0;color:var(--ink-2);font-size:.95rem}}
.more{{margin-top:2.4rem}} .more h3{{font-size:.72rem;letter-spacing:.2em;text-transform:uppercase;color:var(--bronze);font-weight:500;margin:0 0 .9rem}}
footer{{padding:2rem 0 3rem;font-size:.78rem;color:var(--mute)}} footer a{{color:inherit}}
:focus-visible{{outline:2px solid var(--bronze);outline-offset:3px}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>
</head>
<body>
<header class="wrap top"><a class="brand" href="/"><canvas class="rgmark" width="80" height="80" aria-hidden="true"></canvas><b>Reflect<small>Group</small></b></a><nav class="toplinks"><a href="/insights/">Insights</a><a href="/#contact">Contact</a></nav></header>
'''

FOOT = '''<footer class="wrap"><p>&copy; {year} Reflect Group Pty Ltd &middot; ABN 33 647 782 947 &middot; <a href="/legal">Privacy and terms</a> &middot; <a href="/insights/feed.xml">RSS</a></p></footer>
<script src="/mark.js"></script>
<script>if(window.reflectMark) document.querySelectorAll('canvas.rgmark').forEach(c=>reflectMark(c));</script>
</body>
</html>
'''

def subscribe_block(cfg):
    ml = (cfg or {}).get('mailerlite') or {}
    if not ml.get('account') or not ml.get('form'):
        return ''
    action = f"https://assets.mailerlite.com/jsonp/{ml['account']}/forms/{ml['form']}/subscribe"
    return f'''<section class="sub" aria-labelledby="subT">
  <div class="eyebrow">Insights by email</div>
  <h2 id="subT">One article a week, on cost management and conversion strategy.</h2>
  <p>Published each Monday. No other mail, and every email carries a one-click unsubscribe.</p>
  <form action="{action}" method="post" target="_blank">
    <input type="email" name="fields[email]" required placeholder="Email address" aria-label="Email address" autocomplete="email">
    <input type="hidden" name="ml-submit" value="1"><input type="hidden" name="anticsrf" value="true">
    <button type="submit">Subscribe</button>
  </form>
  <p class="fine">By subscribing you agree to receive the Reflect Group Insights email. See <a href="/legal">privacy and terms</a>.</p>
</section>'''

def main():
    args = sys.argv[1:]
    show_all = '--all' in args
    today = datetime.datetime.now(ZoneInfo('Australia/Sydney')).date()
    if '--today' in args: today = datetime.date.fromisoformat(args[args.index('--today') + 1])
    cfg_path = os.path.join(SRC, '_config.json')
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    posts = [parse(p) for p in sorted(glob.glob(os.path.join(SRC, '*.md')))]
    posts = [p for p in posts if show_all or p['date_obj'] <= today]
    posts.sort(key=lambda p: p['date_obj'], reverse=True)
    os.makedirs(OUT, exist_ok=True)
    import shutil
    keep = {p['slug'] for p in posts}
    for d in os.listdir(OUT):
        if os.path.isdir(os.path.join(OUT, d)) and d not in keep: shutil.rmtree(os.path.join(OUT, d))
    sub = subscribe_block(cfg); year = today.year
    esc = html.escape

    # index
    items = '\n'.join(f'''  <li><a href="/insights/{p['slug']}/"><div class="eyebrow">{fdate(p['date_obj'])} &middot; {p['minutes']} min read</div><h2>{esc(p['title'])}</h2><p>{esc(p.get('summary',''))}</p></a></li>''' for p in posts)
    empty = '' if posts else '<p style="color:var(--ink-2)">The first article will be published shortly.</p>'
    idx = HEAD.format(title='Insights · Reflect Group', desc='Articles on cost management, quantity surveying, estimating and tender strategy for builders, subcontractors and developers.', url=f'{SITE}/insights/', ogtype='website', site=SITE)
    idx += f'''<main>
<section class="sheet"><div class="wrap">
  <div class="eyebrow">Insights</div>
  <h1>Cost management and conversion strategy, one article at a time.</h1>
  <p class="lede">Practical writing for builders, subcontractors and developers on measuring, pricing and winning work: what goes into a bill, how a tender is qualified, and where a margin is won or lost.</p>
</div></section>
<div class="wrap" style="padding:2.4rem 16px 1rem">
<ul class="list">
{items}
</ul>{empty}
{sub}
</div>
</main>
''' + FOOT.format(year=year)
    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf8').write(idx)

    # articles
    for i, p in enumerate(posts):
        d = os.path.join(OUT, p['slug']); os.makedirs(d, exist_ok=True)
        url = f"{SITE}/insights/{p['slug']}/"
        others = [q for q in posts if q is not p][:3]
        more = ''
        if others:
            more = '<div class="more"><h3>More insights</h3><ul class="list">' + ''.join(f'''<li><a href="/insights/{q['slug']}/"><div class="eyebrow">{fdate(q['date_obj'])}</div><h2>{esc(q['title'])}</h2></a></li>''' for q in others) + '</ul></div>'
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": p['title'], "description": p.get('summary', ''), "datePublished": p['date'], "author": {"@type": "Person", "name": AUTHOR}, "publisher": {"@type": "Organization", "name": "Reflect Group Pty Ltd", "url": SITE}, "mainEntityOfPage": url})
        page = HEAD.format(title=f"{esc(p['title'])} · Reflect Group", desc=esc(p.get('summary', '')), url=url, ogtype='article', site=SITE)
        page += f'''<script type="application/ld+json">{ld}</script>
<main>
<section class="sheet"><div class="wrap">
  <div class="eyebrow"><a href="/insights/" style="border:0;color:inherit">Insights</a> &middot; {fdate(p['date_obj'])}</div>
  <h1>{esc(p['title'])}</h1>
  <p class="lede">{esc(p.get('summary',''))}</p>
  <div class="meta">{AUTHOR}, Managing Director &middot; {p['minutes']} min read</div>
</div></section>
<div class="wrap">
<article class="body">
{p['html']}
</article>
<div class="author"><canvas class="rgmark" width="104" height="104" aria-hidden="true"></canvas><p><b>{AUTHOR}</b>, Managing Director of Reflect Group, a quantity surveying and estimating practice serving builders, subcontractors, developers and architects. <a href="/#contact">Request a fee proposal</a>.</p></div>
{sub}
{more}
</div>
</main>
''' + FOOT.format(year=year)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf8').write(page)

    # feed
    def rfc822(dt): return datetime.datetime.combine(dt, datetime.time(7, 0), ZoneInfo('Australia/Sydney')).strftime('%a, %d %b %Y %H:%M:%S %z')
    items = ''.join(f'''<item><title>{esc(p['title'])}</title><link>{SITE}/insights/{p['slug']}/</link><guid isPermaLink="true">{SITE}/insights/{p['slug']}/</guid><pubDate>{rfc822(p['date_obj'])}</pubDate><description>{esc(p.get('summary',''))}</description><content:encoded><![CDATA[{p['html']}]]></content:encoded></item>''' for p in posts)
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>Reflect Group · Insights</title><link>{SITE}/insights/</link><description>Cost management and conversion strategy for builders, subcontractors and developers.</description><language>en-au</language>{items}</channel></rss>
'''
    open(os.path.join(OUT, 'feed.xml'), 'w', encoding='utf8').write(feed)

    # sitemap
    urls = [f'{SITE}/', f'{SITE}/legal'] + ([f'{SITE}/insights/'] if posts else []) + [f"{SITE}/insights/{p['slug']}/" for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
    print(f'built {len(posts)} article(s) for {today}; subscribe form: {"on" if sub else "off"}')

if __name__ == '__main__':
    main()
