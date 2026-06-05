#!/usr/bin/env python3
"""Reconstruit les pages produits de setup.ludoc.net en version moderne et epuree."""
import re, html, pathlib

SRC = pathlib.Path("_scrape")
OUT = pathlib.Path(".")

PAGES = {
    "materiel-camera":     ("Caméra",      "Mon matériel"),
    "materiel-son":        ("Son",         "Mon matériel"),
    "materiel-lumiere":    ("Lumière",     "Mon matériel"),
    "materiel-machinerie": ("Machinerie",  "Mon matériel"),
    "bureau-materiel":     ("Matériel",    "Mon bureau"),
    "bureau-accessoires":  ("Accessoires", "Mon bureau"),
    "bureau-meubles":      ("Meubles",     "Mon bureau"),
    "bureau-lumiere":      ("Lumière",     "Mon bureau"),
    "bureau-atelier":      ("Atelier",     "Mon bureau"),
}

TOKEN = re.compile(
    r'<h1>(.*?)</h1>'
    r'|<a href="([^"]+)" class="Product"[^>]*>\s*<img src="([^"]+)">\s*'
    r'<div class="ProductText"><h2>(.*?)</h2><h3>(.*?)</h3>',
    re.S)
BANNER = re.compile(r'Banner"[^>]*background-image:\s*url\(([^)]+)\)')

def https(u):
    return u.strip().replace("http://", "https://")

def parse(text):
    banner = BANNER.search(text)
    banner = https(banner.group(1)) if banner else ""
    sections, cur = [], None
    for m in TOKEN.finditer(text):
        if m.group(1) is not None:
            cur = {"title": html.unescape(m.group(1).strip()), "items": []}
            sections.append(cur)
        else:
            if cur is None:
                cur = {"title": "", "items": []}
                sections.append(cur)
            cur["items"].append({
                "link": m.group(2).strip(),
                "img": https(m.group(3)),
                "cat": html.unescape(m.group(4).strip()),
                "name": html.unescape(m.group(5).strip()),
            })
    return banner, [s for s in sections if s["items"]]

def card(it):
    return f'''        <a class="prod" href="{html.escape(it['link'])}" target="_blank" rel="noopener nofollow">
          <div class="prod-img"><img src="{html.escape(it['img'])}" alt="{html.escape(it['name'])}" loading="lazy"></div>
          <div class="prod-info">
            <span class="prod-cat">{html.escape(it['cat'])}</span>
            <span class="prod-name">{html.escape(it['name'])}</span>
          </div>
        </a>'''

def section(s):
    cards = "\n".join(card(it) for it in s["items"])
    head = f'      <h2 class="sec-title">{html.escape(s["title"])}</h2>\n' if s["title"] else ""
    return f'''    <section class="sec">
{head}      <div class="prod-grid">
{cards}
      </div>
    </section>'''

TPL = '''<!DOCTYPE html>
<html lang="fr-FR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — Le Setup de Ludoc</title>
  <meta name="description" content="{title} — le matériel utilisé par Ludoc, vidéaste documentaire & YouTube.">
  <meta name="robots" content="index, follow">
  <link rel="icon" href="https://setup.ludoc.net/img/ludoc.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Montserrat:wght@600;700;800&display=swap" rel="stylesheet">
  <link href="style.css" rel="stylesheet">
</head>
<body>
  <div class="bg-orbs" aria-hidden="true"><span class="orb orb-1"></span><span class="orb orb-2"></span><span class="orb orb-3"></span></div>

  <header class="page-hero"{hero_style}>
    <div class="page-hero-overlay">
      <a class="back" href="index.html">← Retour au menu</a>
      <p class="eyebrow">{parent}</p>
      <h1>{title}</h1>
    </div>
  </header>

  <main class="wrap">
{body}
  </main>

  <footer class="site-footer">
    <p>© <span id="year"></span> Ludoc — Le Setup. Certains liens sont affiliés.</p>
  </footer>
  <script>document.getElementById('year').textContent = new Date().getFullYear();</script>
</body>
</html>
'''

def main():
    for slug, (title, parent) in PAGES.items():
        text = (SRC / f"{slug}.html").read_text(encoding="utf-8", errors="replace")
        banner, sections = parse(text)
        body = "\n".join(section(s) for s in sections)
        hero_style = f' style="--banner:url(\'{banner}\')"' if banner else ""
        out = TPL.format(title=html.escape(title), parent=html.escape(parent),
                         body=body, hero_style=hero_style)
        (OUT / f"{slug}.html").write_text(out, encoding="utf-8")
        n = sum(len(s["items"]) for s in sections)
        print(f"{slug}.html  ->  {len(sections)} sections, {n} produits")

if __name__ == "__main__":
    main()
