"""HemenOyna çok dilli sürümler: /<dil>/ altında her dil için katalog.
Kullanım: python3 build_lang.py games.json SITE_KLASORU [dil1,dil2,...]
"""
import json, sys, os, re, html, shutil, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n import LANGS, RTL, NATIVE, HREFLANG, UI, genre_name

SRC, SITE_DIR = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3].split(",") if len(sys.argv) > 3 else LANGS
BASE = "https://hemen-oyna.com"
SITE = "HemenOyna"
ADSTERRA_KEY = "3997af85d4829bbacda7b2484c989903"
TODAY = datetime.date.today().isoformat()
MENU = ["arcade", "puzzle", "action", "racing", "car", "sports", "girls", "multiplayer", "shooting", "kids"]

esc = lambda s: html.escape(str(s or ""), quote=True)
slug = lambda s: re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")

data = json.load(open(SRC))
G, seen = [], set()
for g in data["segments"][0]["hits"]:
    if g["slug"] in seen or "clid=" not in (g.get("gameURL") or ""):
        continue
    seen.add(g["slug"])
    g["img"] = (g.get("images") or [""])[0]
    g["langs"] = {l.split("-")[0] for l in (g.get("supportedLanguages") or [])}
    G.append(g)

by_genre = {}
for g in G:
    for ge in g.get("genres") or []:
        by_genre.setdefault(ge, []).append(g)

# Ortak dosyalar
CSS = """*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,"Noto Sans",sans-serif;background:#0b0c1d;color:#e8e9f3}
a{color:inherit;text-decoration:none}header{position:sticky;top:0;z-index:5;background:#12132b;border-bottom:1px solid #23254a;padding:10px 14px;display:flex;gap:12px;align-items:center}
.logo{font-weight:800;font-size:22px;color:#41f0ff;white-space:nowrap}.logo b{color:#ff4fc8}
form.s{flex:1;min-width:0;display:flex}form.s input{flex:1;min-width:0;padding:9px 12px;border-radius:10px;border:1px solid #2c2f5e;background:#0b0c1d;color:#fff;font-size:15px}
nav.c{display:flex;gap:6px;overflow-x:auto;padding:10px 14px;background:#0e0f24;scrollbar-width:none}nav.c a{white-space:nowrap;padding:6px 12px;border-radius:999px;background:#1b1d3d;font-size:14px}
main{max-width:1200px;margin:0 auto;padding:14px}h1{font-size:24px;margin:8px 0 14px}h2{font-size:19px;margin:22px 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{background:#15173a;border-radius:12px;overflow:hidden}.card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;background:#222}
.card span{display:block;padding:8px;font-size:14px;line-height:1.25;height:3.2em;overflow:hidden}
.feat{display:flex;gap:16px;align-items:center;background:linear-gradient(135deg,#1a1050,#0b2a3a);border-radius:16px;padding:16px;margin-bottom:8px;flex-wrap:wrap}
.feat img{width:140px;border-radius:12px}.feat h2{margin:0 0 6px;color:#41f0ff}.btn{display:inline-block;background:#41f0ff;color:#071018;font-weight:700;padding:10px 18px;border-radius:10px;margin-top:8px}
.game{width:100%;max-width:960px;display:block;margin:0 auto;aspect-ratio:16/10;max-height:75vh;border:0;border-radius:12px;background:#000}.game.v{aspect-ratio:9/16;max-width:460px}
.ad{display:flex;justify-content:center;margin:12px 0;min-height:50px}.desc{color:#c3c5dc;line-height:1.55;font-size:15px;white-space:pre-line}
.tags a{display:inline-block;margin:3px 4px 3px 0;padding:4px 10px;border-radius:999px;background:#1b1d3d;font-size:13px}
footer{text-align:center;color:#8a8db0;font-size:13px;padding:30px 14px}footer a{text-decoration:underline}
#langs{display:flex;flex-wrap:wrap;gap:6px 12px;justify-content:center;margin:0 auto 14px;max-width:900px}#langs a{text-decoration:none;color:#c3c5dc}
"""
# Dil seçici: bulunduğun sayfanın diğer dillerdeki karşılığına götürür
JS = """(function(){var L=%s,N=%s,p=location.pathname,m=p.match(/^\\/(en|es|pt|de|fr|ru|it|id|pl|zh|hi|ja|ar|fa)\\/(game|category)\\/([^\\/]+)\\//),t=p.match(/^\\/(oyun|kategori)\\/([^\\/]+)\\//);
var kind=null,s=null;if(m){kind=m[2];s=m[3]}else if(t){kind=t[1]=='oyun'?'game':'category';s=t[2]}
var d=document.getElementById('langs');if(!d)return;var h='';L.forEach(function(l){var u;
if(l=='tr'){u=kind?('/'+(kind=='game'?'oyun':'kategori')+'/'+s+'/'):'/'}else{u='/'+l+'/'+(kind?kind+'/'+s+'/':'')}
h+='<a href="'+u+'">'+N[l]+'</a>'});d.innerHTML=h})();""" % (json.dumps(["tr"] + LANGS), json.dumps(NATIVE, ensure_ascii=False))
os.makedirs(os.path.join(SITE_DIR, "assets"), exist_ok=True)
open(os.path.join(SITE_DIR, "assets", "site.css"), "w").write(CSS)
open(os.path.join(SITE_DIR, "assets", "langs.js"), "w").write(JS)


def galt(sl):
    return ("".join(f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{BASE}/{l}/game/{sl}/">' for l in LANGS)
            + f'<link rel="alternate" hreflang="tr" href="{BASE}/oyun/{sl}/"><link rel="alternate" hreflang="x-default" href="{BASE}/en/game/{sl}/">')


def build(lang):
    T = UI[lang]
    OUT = os.path.join(SITE_DIR, lang)
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    GN = lambda c: genre_name(c, lang)
    cats = [c for c in sorted(by_genre, key=lambda k: -len(by_genre[k])) if GN(c) and len(by_genre[c]) >= 12]
    menu = "".join(f'<a href="/{lang}/category/{slug(c)}/">{GN(c)}</a>' for c in MENU if c in cats)
    # bu dili destekleyen oyunlar önce
    order = sorted(G, key=lambda g: 0 if lang in g["langs"] else 1)
    hl = HREFLANG.get(lang, lang)
    dirattr = ' dir="rtl"' if lang in RTL else ""

    def page(title, desc, body, path, head=""):
        return (f'<!DOCTYPE html><html lang="{hl}"{dirattr}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{BASE}{path}">'
                f'<meta property="og:title" content="{esc(title)}"><meta property="og:url" content="{BASE}{path}"><link rel="stylesheet" href="/assets/site.css">{head}</head><body>'
                f'<header><a class="logo" href="/{lang}/">Hemen<b>Oyna</b></a><form class="s" action="/{lang}/search/"><input name="q" placeholder="{esc(T["search"])}" aria-label="{esc(T["search_h"])}"></form></header>'
                f'<nav class="c"><a href="/{lang}/">{T["popular"]}</a>{menu}</nav><main>{body}</main>'
                f'<footer><div id="langs"></div>{SITE} · {T["foot"]} · <a href="/gizlilik/">{T["privacy"]}</a><br>{T["partner"]}</footer>'
                f'<script src="/assets/langs.js" defer></script><script data-goatcounter="https://yorunge.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script></body></html>')

    def card(g):
        return f'<a class="card" href="/{lang}/game/{g["slug"]}/"><img loading="lazy" src="{esc(g["img"])}" alt="{esc(g["title"])}"><span>{esc(g["title"])}</span></a>'

    def write(path, content):
        full = os.path.join(OUT, path.strip("/"), "index.html")
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w", encoding="utf-8").write(content)

    urls = [f"/{lang}/"]
    alts = "".join(f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{BASE}/{l}/">' for l in LANGS) + f'<link rel="alternate" hreflang="tr" href="{BASE}/">'
    feat = (f"<div class='feat'><img src='/yorunge.png' alt='Yörünge'><div><h2>Yörünge: Neon Orbit</h2>{esc(T['feat'])}"
            f"<br><a class='btn' href='/yorunge/?src=hemenoyna-{lang}'>{esc(T['play_now'])}</a></div></div>")
    body = f"<h1>{esc(T['h1'])}</h1>{feat}<h2>{T['popular_h']}</h2><div class='grid'>" + "".join(card(g) for g in order[:48]) + "</div>"
    for c in MENU[:5]:
        if c in cats:
            body += (f"<h2><a href='/{lang}/category/{slug(c)}/'>{esc(T['cat_h'].format(c=GN(c)))} ›</a></h2><div class='grid'>"
                     + "".join(card(g) for g in by_genre[c][:12]) + "</div>")
    write("/", page(f"{SITE} — {T['site_title']}", T["meta"], body, f"/{lang}/", alts))

    for c in cats:
        lst = sorted(by_genre[c], key=lambda g: 0 if lang in g["langs"] else 1)
        write(f"/category/{slug(c)}/", page(f"{T['cat_title'].format(c=GN(c))} | {SITE}", T["cat_meta"].format(n=len(lst), c=GN(c)),
              f"<h1>{esc(T['cat_h'].format(c=GN(c)))}</h1><div class='grid'>" + "".join(card(g) for g in lst[:240]) + "</div>", f"/{lang}/category/{slug(c)}/"))
        urls.append(f"/{lang}/category/{slug(c)}/")

    for g in G:
        genres = [x for x in (g.get("genres") or []) if GN(x)]
        gs = ", ".join(GN(x) for x in genres[:3]) or T["fun"]
        vertical = (g.get("screenOrientation") or {}).get("vertical") and not (g.get("screenOrientation") or {}).get("horizontal")
        rel = []
        for x in genres:
            for o in by_genre.get(x, []):
                if o is not g and o not in rel:
                    rel.append(o)
                if len(rel) >= 8:
                    break
            if len(rel) >= 8:
                break
        d = T["game_desc"].format(t=g["title"], g=gs)
        tags = "".join(f"<a href='/{lang}/category/{slug(x)}/'>{GN(x)}</a>" for x in genres if x in cats)
        ld = json.dumps({"@context": "https://schema.org", "@type": "VideoGame", "name": g["title"], "url": f"{BASE}/{lang}/game/{g['slug']}/",
                         "image": g["img"], "description": d, "inLanguage": hl, "genre": [GN(x) for x in genres],
                         "gamePlatform": ["Web", "Android", "iOS"], "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}},
                        ensure_ascii=False, separators=(",", ":"))
        about = f"<h2>{T['about']}</h2><p class='desc'>{esc((g.get('description') or '')[:1200])}</p>" if lang == "en" else ""
        body = (f"<h1>{esc(T['game_h'].format(t=g['title']))}</h1>"
                f"<iframe class='game{' v' if vertical else ''}' src='{esc(g['gameURL'])}' allow='autoplay; fullscreen; gamepad' allowfullscreen loading='lazy' title='{esc(g['title'])}'></iframe>"
                f'<div class="ad"><script>atOptions={{"key":"{ADSTERRA_KEY}","format":"iframe","height":50,"width":320,"params":{{}}}};</script><script src="https://bauval.org/22/{ADSTERRA_KEY}"></script></div>'
                f"<p class='desc'>{esc(d)}</p><div class='tags'>{tags}</div>"
                f"<h2>{T['how']}</h2><p class='desc'>{esc(g.get('howToPlayText') or '')}</p>{about}"
                f"<h2>{T['similar']}</h2><div class='grid'>" + "".join(card(o) for o in rel) + "</div>")
        write(f"/game/{g['slug']}/", page(f"{T['game_title'].format(t=g['title'])} | {SITE}", d, body, f"/{lang}/game/{g['slug']}/",
              f'<meta property="og:image" content="{esc(g["img"])}"><script type="application/ld+json">{ld}</script>' + galt(g["slug"])))
        urls.append(f"/{lang}/game/{g['slug']}/")

    os.makedirs(os.path.join(OUT, "search"), exist_ok=True)
    idx = [[g["slug"], g["title"], g["img"], " ".join(GN(x) for x in (g.get("genres") or []) if GN(x))] for g in order]
    json.dump(idx, open(os.path.join(OUT, "search", "games.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    sj = ("<h1 id=h>" + esc(T["search_h"]) + "</h1><div class=grid id=r></div><script>"
          "const T=" + json.dumps({"r": T["results"], "n": T["noresult"], "h": T["search_h"]}, ensure_ascii=False) + ";"
          "const q=(new URLSearchParams(location.search).get('q')||'').trim().toLowerCase();"
          f"fetch('/{lang}/search/games.json').then(r=>r.json()).then(L=>{{const R=q?L.filter(x=>(x[1]+' '+x[3]).toLowerCase().includes(q)):L.slice(0,60);"
          "document.getElementById('h').textContent=q?T.r.replace('{n}',R.length).replace('{q}',q):T.h;"
          f"document.getElementById('r').innerHTML=R.slice(0,200).map(x=>`<a class=card href=\"/{lang}/game/${{x[0]}}/\"><img loading=lazy src=\"${{x[2]}}\" alt=\"\"><span>${{x[1].replace(/</g,'&lt;')}}</span></a>`).join('')||'<p>'+T.n+'</p>';"
          "document.querySelector('form.s input').value=q;});</script>")
    write("/search/", page(f"{T['search_h']} — {SITE}", T["search_h"], sj, f"/{lang}/search/", '<meta name="robots" content="noindex">'))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
    sm.append("</urlset>")
    open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
    print(lang, "sayfa:", len(urls), "kategori:", len(cats))


for l in ONLY:
    build(l)
