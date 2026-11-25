"""HemenOyna: Playgama Partners kataloğundan statik Türkçe oyun sitesi üretir.
Kullanım: python3 build_site.py games.json CIKTI_KLASORU
"""
import json, sys, os, re, html, shutil, datetime

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = "https://muslihancihan223-bot.github.io"
SITE = "HemenOyna"
ADSTERRA_KEY = "3997af85d4829bbacda7b2484c989903"
GOAT = "yorunge"
TODAY = datetime.date.today().isoformat()

GENRE_TR = {
    "arcade": "Arcade", "3d": "3D", "puzzle": "Bulmaca", "action": "Aksiyon", "simulation": "Simülasyon",
    "matching": "Eşleştirme", "logic": "Mantık", "skill": "Beceri", "adventure": "Macera", "brain": "Zekâ",
    "obby": "Obby", "shooting": "Nişancı", "management": "Yönetim", "idle": "Idle", "strategy": "Strateji",
    "cozy": "Rahatlatıcı", "driving": "Sürüş", "physics": "Fizik", "merge": "Birleştirme", "car": "Araba",
    "survival": "Hayatta Kalma", "animals": "Hayvan", "multiplayer": "Çok Oyunculu", "racing": "Yarış",
    "tycoon": "Tycoon", "funny": "Komik", "running": "Koşu", "platform": "Platform", "clicker": "Tıklama",
    "girls": "Kız", "food": "Yemek", "cooking": "Yemek Yapma", "sports": "Spor", "football": "Futbol",
    "soccer": "Futbol", "card": "Kart", "board": "Masa", "word": "Kelime", "math": "Matematik",
    "educational": "Eğitici", "kids": "Çocuk", "horror": "Korku", "zombie": "Zombi", "war": "Savaş",
    "fighting": "Dövüş", "io": ".io", "dress-up": "Giydirme", "makeup": "Makyaj", "match-3": "Üçlü Eşleştirme",
    "mahjong": "Mahjong", "solitaire": "Solitaire", "chess": "Satranç", "bubble-shooter": "Balon Patlatma",
    "tetris": "Tetris", "sandbox": "Sandbox", "minecraft": "Minecraft", "parkour": "Parkur", "basketball": "Basketbol",
    "motorbike": "Motor", "stickman": "Çöp Adam", "ball": "Top", "casual": "Basit", "mobile": "Mobil",
    "hypercasual": "Hiper Basit", "rpg": "RYO", "quiz": "Bilgi Yarışması", "drawing": "Çizim", "music": "Müzik",
    "christmas": "Yılbaşı", "halloween": "Cadılar Bayramı", "pixel": "Piksel", "ninja": "Ninja", "dinosaur": "Dinozor",
    "cat": "Kedi", "dog": "Köpek", "fishing": "Balık Tutma", "farm": "Çiftlik", "city": "Şehir", "space": "Uzay",
    "tower-defense": "Kule Savunma", "sniper": "Keskin Nişancı", "flight": "Uçuş", "bike": "Bisiklet",
    "escape": "Kaçış", "hidden-object": "Gizli Nesne", "jigsaw": "Yapboz", "coloring": "Boyama", "baby": "Bebek",
}
MENU = ["arcade", "puzzle", "action", "racing", "car", "sports", "girls", "multiplayer", "shooting",
        "simulation", "strategy", "brain", "kids", "io", "card", "horror"]


def slug_tr(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")


def esc(s):
    return html.escape(str(s or ""), quote=True)


data = json.load(open(SRC))
games = data["segments"][0]["hits"]
seen = set()
G = []
for g in games:
    if g["slug"] in seen or not g.get("gameURL") or "clid=" not in g["gameURL"]:
        continue
    seen.add(g["slug"])
    g["tr"] = any(l.startswith("tr") for l in (g.get("supportedLanguages") or []))
    g["img"] = (g.get("images") or [""])[0]
    g["icon"] = (g.get("images") or ["", ""])[1] if len(g.get("images") or []) > 1 else g["img"]
    G.append(g)
# Türkçe destekleyenler önce (katalog sırası = performans sırası korunur)
G.sort(key=lambda g: 0 if g["tr"] else 1)
by_genre = {}
for g in G:
    for ge in g.get("genres") or []:
        by_genre.setdefault(ge, []).append(g)

CATS = [c for c in sorted(by_genre, key=lambda k: -len(by_genre[k])) if c in GENRE_TR and len(by_genre[c]) >= 12]

CSS = """
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#0b0c1d;color:#e8e9f3}
a{color:inherit;text-decoration:none}header{position:sticky;top:0;z-index:5;background:#12132b;border-bottom:1px solid #23254a;padding:10px 14px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.logo{font-weight:800;font-size:22px;color:#41f0ff;letter-spacing:.5px}.logo b{color:#ff4fc8}
form.s{flex:1;min-width:0;display:flex}form.s input{min-width:0}form.s input{flex:1;padding:9px 12px;border-radius:10px;border:1px solid #2c2f5e;background:#0b0c1d;color:#fff;font-size:15px}
nav.c{display:flex;gap:6px;overflow-x:auto;padding:10px 14px;background:#0e0f24;scrollbar-width:none}nav.c a{white-space:nowrap;padding:6px 12px;border-radius:999px;background:#1b1d3d;font-size:14px}nav.c a:hover{background:#2a2d60}
main{max-width:1200px;margin:0 auto;padding:14px}h1{font-size:24px;margin:8px 0 14px}h2{font-size:19px;margin:22px 0 10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.card{background:#15173a;border-radius:12px;overflow:hidden;transition:transform .15s}.card:hover{transform:translateY(-3px)}
.card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;background:#222}.card span{display:block;padding:8px;font-size:14px;line-height:1.25;height:3.2em;overflow:hidden}
.tr{font-size:11px;background:#e30a17;color:#fff;border-radius:4px;padding:1px 5px;margin-left:4px;vertical-align:middle}
.feat{display:flex;gap:16px;align-items:center;background:linear-gradient(135deg,#1a1050,#0b2a3a);border-radius:16px;padding:16px;margin-bottom:8px;flex-wrap:wrap}
.feat img{width:140px;border-radius:12px}.feat h2{margin:0 0 6px;color:#41f0ff}.btn{display:inline-block;background:#41f0ff;color:#071018;font-weight:700;padding:10px 18px;border-radius:10px;margin-top:8px}
.game{width:100%;max-width:960px;display:block;margin:0 auto;aspect-ratio:16/10;max-height:75vh;border:0;border-radius:12px;background:#000}.game.v{aspect-ratio:9/16;max-width:460px;display:block;margin:0 auto}
.ad{display:flex;justify-content:center;margin:12px 0;min-height:50px}.desc{color:#c3c5dc;line-height:1.55;font-size:15px;white-space:pre-line}
.tags a{display:inline-block;margin:3px 4px 3px 0;padding:4px 10px;border-radius:999px;background:#1b1d3d;font-size:13px}
footer{text-align:center;color:#8a8db0;font-size:13px;padding:30px 14px}footer a{text-decoration:underline}
"""

GOAT_JS = ('<script data-goatcounter="https://%s.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>' % GOAT)


def ad_block():
    k = ADSTERRA_KEY
    return ('<div class="ad"><script>atOptions={"key":"%s","format":"iframe","height":50,"width":320,"params":{}};</script>'
            '<script src="https://bauval.org/22/%s"></script></div>') % (k, k)


def page(title, desc, body, path, extra_head=""):
    canon = BASE + path
    menu = "".join('<a href="/kategori/%s/">%s</a>' % (slug_tr(c), GENRE_TR[c]) for c in MENU if c in by_genre)
    return f"""<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta name="theme-color" content="#12132b">{extra_head}
<style>{CSS}</style></head><body>
<header><a class="logo" href="/">Hemen<b>Oyna</b></a>
<form class="s" action="/ara/"><input name="q" placeholder="Oyun ara…" aria-label="Oyun ara"></form></header>
<nav class="c"><a href="/">🔥 Popüler</a><a href="/turkce/">🇹🇷 Türkçe</a>{menu}<a href="/en/">🌍 English</a></nav>
<main>{body}</main>
<footer>{SITE} · İndirme yok, kayıt yok — tarayıcıda ücretsiz oyna · <a href="/gizlilik/">Gizlilik</a><br>Oyunlar Playgama ortaklığıyla sunulur.</footer>
{GOAT_JS}</body></html>"""


def card(g):
    badge = '<i class="tr">TR</i>' if g["tr"] else ""
    return (f'<a class="card" href="/oyun/{g["slug"]}/"><img loading="lazy" src="{esc(g["img"])}" alt="{esc(g["title"])}">'
            f'<span>{esc(g["title"])}{badge}</span></a>')


def write(path, content):
    full = os.path.join(OUT, path.strip("/"), "index.html") if not path.endswith(".html") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(content)


if os.path.isdir(OUT):
    for n in os.listdir(OUT):
        if n in (".git", "README.md"):
            continue
        p = os.path.join(OUT, n)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

urls = ["/", "/turkce/"]

# Ana sayfa
feat = ("<div class='feat'><img src='/yorunge.png' alt='Yörünge'><div><h2>Yörünge: Neon Orbit</h2>"
        "Tek dokunuşla yön değiştir, kırmızı lazerlerden kaç, altınları topla. Rekorunu kır!"
        "<br><a class='btn' href='https://muslihancihan223-bot.github.io/yorunge/?src=hemenoyna'>Hemen Oyna ▶</a></div></div>")
body = "<h1>Ücretsiz Online Oyunlar — İndirmeden Hemen Oyna</h1>" + feat
body += "<h2>🔥 Popüler Oyunlar</h2><div class='grid'>" + "".join(card(g) for g in G[:48]) + "</div>"
for c in MENU[:6]:
    if c in by_genre:
        body += (f"<h2><a href='/kategori/{slug_tr(c)}/'>{GENRE_TR[c]} Oyunları ›</a></h2><div class='grid'>"
                 + "".join(card(g) for g in by_genre[c][:12]) + "</div>")
write("/", page(f"{SITE} — Ücretsiz Online Oyunlar, İndirmeden Oyna",
                "Binlerce ücretsiz online oyun: arcade, bulmaca, araba, aksiyon, kız oyunları. İndirme ve kayıt yok, telefondan ve bilgisayardan hemen oyna.",
                body, "/"))

trg = [g for g in G if g["tr"]]
write("/turkce/", page(f"Türkçe Oyunlar — {SITE}", f"Türkçe dil desteği olan {len(trg)} ücretsiz online oyun. İndirmeden hemen oyna.",
                       f"<h1>Türkçe Oyunlar ({len(trg)})</h1><div class='grid'>" + "".join(card(g) for g in trg) + "</div>", "/turkce/"))

for c in CATS:
    s = slug_tr(c)
    lst = by_genre[c]
    write(f"/kategori/{s}/", page(f"{GENRE_TR[c]} Oyunları — Ücretsiz Oyna | {SITE}",
                                  f"{len(lst)} ücretsiz {GENRE_TR[c].lower()} oyunu. İndirme yok, tarayıcıda telefondan ve bilgisayardan hemen oyna.",
                                  f"<h1>{GENRE_TR[c]} Oyunları</h1><div class='grid'>" + "".join(card(g) for g in lst[:300]) + "</div>",
                                  f"/kategori/{s}/"))
    urls.append(f"/kategori/{s}/")

for i, g in enumerate(G):
    genres = [x for x in (g.get("genres") or []) if x in GENRE_TR]
    tr_g = ", ".join(GENRE_TR[x] for x in genres[:4]) or "eğlenceli"
    vertical = (g.get("screenOrientation") or {}).get("vertical") and not (g.get("screenOrientation") or {}).get("horizontal")
    rel = []
    for x in genres:
        for o in by_genre.get(x, []):
            if o is not g and o not in rel:
                rel.append(o)
            if len(rel) >= 12:
                break
        if len(rel) >= 12:
            break
    lang = "Türkçe dil desteği var. " if g["tr"] else ""
    tr_desc = (f"{g['title']} ücretsiz bir {tr_g.lower()} oyunudur. {lang}İndirme ve kayıt gerekmez; "
               f"telefonda, tablette ve bilgisayarda tarayıcıdan hemen oynayabilirsin.")
    tags = "".join(f"<a href='/kategori/{slug_tr(x)}/'>{GENRE_TR[x]}</a>" for x in genres if x in CATS)
    ld = json.dumps({"@context": "https://schema.org", "@type": "VideoGame", "name": g["title"], "url": f"{BASE}/oyun/{g['slug']}/",
                     "image": g["img"], "description": tr_desc, "genre": [GENRE_TR[x] for x in genres],
                     "gamePlatform": ["Web tarayıcı", "Android", "iOS"], "applicationCategory": "Game",
                     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "TRY"}}, ensure_ascii=False)
    body = (f"<h1>{esc(g['title'])} Oyna</h1>"
            f"<iframe class='game{' v' if vertical else ''}' src='{esc(g['gameURL'])}' allow='autoplay; fullscreen; gamepad' allowfullscreen loading='lazy' title='{esc(g['title'])}'></iframe>"
            + ad_block() +
            f"<p class='desc'>{esc(tr_desc)}</p><div class='tags'>{tags}</div>"
            f"<h2>Nasıl Oynanır?</h2><p class='desc'>{esc(g.get('howToPlayText') or '')}</p>"
            f"<h2>Oyun Hakkında</h2><p class='desc'>{esc((g.get('description') or '')[:1200])}</p>"
            f"<h2>Benzer Oyunlar</h2><div class='grid'>" + "".join(card(o) for o in rel) + "</div>")
    write(f"/oyun/{g['slug']}/", page(f"{g['title']} Oyna — Ücretsiz Online | {SITE}", tr_desc, body, f"/oyun/{g['slug']}/",
                                      f'<link rel="alternate" hreflang="tr" href="{BASE}/oyun/{g["slug"]}/"><link rel="alternate" hreflang="en" href="{BASE}/en/game/{g["slug"]}/"><meta property="og:image" content="{esc(g["img"])}"><script type="application/ld+json">{ld}</script>'))
    urls.append(f"/oyun/{g['slug']}/")

# Arama
idx = [[g["slug"], g["title"], g["img"], 1 if g["tr"] else 0, " ".join(GENRE_TR.get(x, x) for x in (g.get("genres") or []))] for g in G]
os.makedirs(os.path.join(OUT, "ara"), exist_ok=True)
json.dump(idx, open(os.path.join(OUT, "ara", "oyunlar.json"), "w"), ensure_ascii=False, separators=(",", ":"))
search_js = """<h1 id=h>Oyun ara</h1><div class=grid id=r></div><script>
const q=(new URLSearchParams(location.search).get('q')||'').trim().toLocaleLowerCase('tr');
const n=s=>s.toLocaleLowerCase('tr');
fetch('/ara/oyunlar.json').then(r=>r.json()).then(L=>{const R=q?L.filter(x=>n(x[1]+' '+x[4]).includes(q)):L.slice(0,60);
document.getElementById('h').textContent=q?`"${q}" için ${R.length} oyun`:'Oyun ara';
document.getElementById('r').innerHTML=R.slice(0,200).map(x=>`<a class=card href="/oyun/${x[0]}/"><img loading=lazy src="${x[2]}" alt=""><span>${x[1].replace(/</g,'&lt;')}${x[3]?'<i class=tr>TR</i>':''}</span></a>`).join('')||'<p>Sonuç bulunamadı.</p>';
document.querySelector('form.s input').value=q;});</script>"""
write("/ara/", page(f"Oyun Ara — {SITE}", "HemenOyna'da oyun ara.", search_js, "/ara/", '<meta name="robots" content="noindex">'))

write("/gizlilik/", page(f"Gizlilik — {SITE}", "Gizlilik politikası",
      "<h1>Gizlilik</h1><p class='desc'>HemenOyna kişisel bilgi toplamaz ve üyelik istemez. Ziyaret sayıları anonim olarak GoatCounter ile ölçülür. "
      "Oyunlar Playgama tarafından sunulur ve oyun içinde reklam gösterilebilir; sayfalarda Adsterra reklamları yer alabilir. "
      "Bu reklam sağlayıcıları kendi çerezlerini kullanabilir.</p>", "/gizlilik/"))

open(os.path.join(OUT, "404.html"), "w", encoding="utf-8").write(
    page(f"Sayfa bulunamadı — {SITE}", "Sayfa bulunamadı", "<h1>Sayfa bulunamadı</h1><p><a class=btn href='/'>Ana sayfaya dön</a></p>", "/404.html"))
open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
open(os.path.join(OUT, ".nojekyll"), "w").write("")
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += [f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in urls]
sm.append("</urlset>")
open(os.path.join(OUT, "sitemap.xml"), "w").write("\n".join(sm))
print("oyun:", len(G), "turkce:", len(trg), "kategori:", len(CATS), "url:", len(urls))
