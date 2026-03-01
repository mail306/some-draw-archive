#!/usr/bin/env python3
"""
build.py - Generate enriched exhibition & work detail pages for some-draw.page
Reads Notion export data (CSV/Markdown/images) from Google Drive,
copies & resizes images, and generates HTML pages.
"""

import csv
import os
import re
import shutil
import subprocess
import html as html_mod
from pathlib import Path
from urllib.parse import unquote

# === Paths ===
SITE_DIR = Path(__file__).resolve().parent
DATA_ROOT = Path(
    "/Users/mikaiwai/Library/CloudStorage/GoogleDrive-mail@some-draw.page"
    "/マイドライブ/進行中/WebSite2026/homepage_some-draw/岩 井 美 佳"
)
EXHIBITIONS_DIR = DATA_ROOT / "e x h i b i t i o n s"
WORKS_MD_DIR = DATA_ROOT / "w o r k s" / "w o r k s"
MAIN_CSV = DATA_ROOT / "e x h i b i t i o n s 2b54178872de473db6bf184e781b0755.csv"

# Output image directories
IMG_WORKS_DIR = SITE_DIR / "images" / "works"
IMG_EX_DIR = SITE_DIR / "images" / "exhibitions"

# === Exhibition HTML slug -> Notion folder name ===
EXHIBITION_MAP = {
    "houmaku": "個展「胞膜 houmaku」",
    "flowers-journey2024": "個展「岩井美佳 展 -みちる花 FLOWER'S JOURNEY-」",
    "artfairtokyo2023": "アートフェア東京 2023",
    "souvin": "個展「染む記憶 線刻糊防染による記憶の表現」",
    "doctor2022": "金沢美術工芸大学 第23回 大学院博士後期課程研究発表展",
    "100colors": "金沢市民芸術村3工房合同企画 岩井美佳「100色の絞り染めに挑戦！」",
    "doctor2021": "金沢美術工芸大学博士課程 学内展示「線刻糊防染による記憶の表現」",
    "artbase": "個展「染む・記憶」",
    "art-nagoya-2020": "ART NAGOYA 2020",
    "assenblemoments": "個展「#assenble_moments」",
    "butokan": "「染め・時間の堆積」展",
    "portreport": "金沢美術工芸大学 平成30年度 博士後期課程1年 研究制作展「port Report」",
    "artsplanet": "銀河音楽室",
    "toiyastudio2017": "問 × 美 2017",
    "visual-sonic-2016": "VISUAL SONIC 2016 Inner Flower,Inner Happening",
    "real": "個展「浮遊するリアル」",
}

# work title -> existing thumbnail filename (in images/)
WORK_THUMB_MAP = {}

# === Templates to exclude ===
# Note: "テンプレ" catches both "テンプレート" and "テンプレ-ト" (long dash variant)
TEMPLATE_KEYWORDS = ["テンプレ", "無題", "作品管理"]

MAX_IMG_WIDTH = 1600


def is_template(name):
    return any(kw in name for kw in TEMPLATE_KEYWORDS)


def resolve_exhibition_folder(folder_name):
    """Find the actual directory on disk matching folder_name (handles Unicode)."""
    if not EXHIBITIONS_DIR.exists():
        return None
    # Try direct path first
    direct = EXHIBITIONS_DIR / folder_name
    if direct.is_dir():
        return direct
    # Scan and match by substring (first 10 chars should be enough)
    key = folder_name[:15]
    for entry in os.listdir(EXHIBITIONS_DIR):
        full = EXHIBITIONS_DIR / entry
        if full.is_dir() and (key in entry or entry in folder_name):
            return full
    return None


def slugify(text):
    """Create URL-safe slug from text."""
    text = text.strip()
    # Remove 《》
    text = re.sub(r'[《》]', '', text)
    # Replace Japanese/special chars with ascii approximations
    text = text.lower()
    text = re.sub(r'[\s　]+', '-', text)
    text = re.sub(r'[−–—]', '-', text)
    text = re.sub(r'[ー]', '-', text)
    text = re.sub(r"['\",;:!?。、（）()「」『』【】\[\]{}]", '', text)
    text = re.sub(r'[/\\]', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-')
    # Keep Japanese characters but remove other problematic chars
    text = re.sub(r'[^\w\-]', '', text, flags=re.UNICODE)
    return text or 'untitled'


def normalize_title(title):
    """Normalize whitespace for title matching."""
    # Replace full-width space with regular space, collapse multiple spaces
    return re.sub(r'[\s　]+', ' ', title).strip()


def build_work_thumb_map():
    """Build mapping from work titles in WORKS_ORDER to their thumbnail files."""
    for thumb, title in WORKS_ORDER:
        WORK_THUMB_MAP[title] = thumb
        WORK_THUMB_MAP[normalize_title(title)] = thumb


# ============================================================
# Step 1: Parse data
# ============================================================

def parse_main_csv():
    """Parse main exhibitions CSV, return list of exhibition dicts."""
    exhibitions = []
    with open(MAIN_CSV, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get('展覧会タイトル', '').strip()
            if not title or is_template(title):
                continue
            # Clean multiline titles
            title = ' '.join(title.split())
            exhibitions.append({
                'title': title,
                'period': row.get('期間', '').strip(),
                'venue': row.get('会場', '').strip(),
                'venue_address': row.get('会場住所', '').strip(),
                'type': row.get('個展 or グループ展', '').strip(),
                'notes': row.get('備考', '').strip(),
                'description': row.get('概要', '').strip(),
            })
    return exhibitions


def parse_work_markdown(md_path):
    """Parse a single work markdown file, return dict of metadata + images."""
    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')

    work = {
        'title': '',
        'size': '',
        'technique': '',
        'material': '',
        'year': '',
        'collection': '',
        'description': '',
        'main_image': '',
        'images': [],
        'md_path': md_path,
    }

    # Title from H1
    for line in lines:
        if line.startswith('# '):
            work['title'] = line[2:].strip()
            break

    # Metadata from key: value lines at top
    for line in lines:
        line_s = line.strip()
        if line_s.startswith('サイズ（H×W×D）:') or line_s.startswith('サイズ（H×W×D）:'):
            work['size'] = line_s.split(':', 1)[1].strip()
        elif line_s.startswith('作品写真:'):
            raw = line_s.split(':', 1)[1].strip()
            work['main_image'] = unquote(raw)
        elif line_s.startswith('技法:'):
            work['technique'] = line_s.split(':', 1)[1].strip()
        elif line_s.startswith('素材:'):
            work['material'] = line_s.split(':', 1)[1].strip()
        elif line_s.startswith('制作年:'):
            work['year'] = line_s.split(':', 1)[1].strip()
        elif line_s.startswith('収蔵先:'):
            work['collection'] = line_s.split(':', 1)[1].strip()
        elif line_s.startswith('所在:'):
            val = line_s.split(':', 1)[1].strip()
            if val and val != '岩井持ち':
                work['collection'] = val

    # Description from 概要 line
    desc_match = re.search(r'概\s*要\s*[:：]\s*(.+)', text)
    if desc_match:
        work['description'] = desc_match.group(1).strip()

    # Embedded images from markdown ![alt](path)
    md_dir = md_path.parent
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', text):
        img_path_raw = unquote(m.group(2))
        # Resolve relative to markdown file's directory
        img_full = (md_dir / img_path_raw).resolve()
        if img_full.exists() and img_full.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            work['images'].append(str(img_full))

    return work


def parse_all_works():
    """Parse all work markdown files, return dict of title -> work data."""
    works = {}
    if not WORKS_MD_DIR.exists():
        print(f"  WARNING: Works MD dir not found: {WORKS_MD_DIR}")
        return works
    for md_file in WORKS_MD_DIR.glob("*.md"):
        if is_template(md_file.name):
            continue
        try:
            w = parse_work_markdown(md_file)
            if w['title']:
                works[w['title']] = w
        except Exception as e:
            print(f"  WARNING: Failed to parse {md_file.name}: {e}")
    return works


def parse_exhibition_works_csv(csv_path):
    """Parse an exhibition-specific works CSV, return list of work title strings."""
    titles = []
    try:
        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('作品タイトル', '').strip()
                if title and not is_template(title):
                    titles.append(title)
    except Exception as e:
        print(f"  WARNING: Failed to parse {csv_path}: {e}")
    return titles


def find_exhibition_works_csv(ex_folder):
    """Find the works CSV inside an exhibition folder (not in template subdirs)."""
    if not ex_folder.exists():
        return None
    for f in ex_folder.iterdir():
        if f.is_file() and f.suffix == '.csv' and not is_template(f.name) and '_all' not in f.name:
            return f
    return None


def find_exhibition_gallery_images(ex_folder):
    """Find gallery images directly in an exhibition folder (not in sub-workdirs)."""
    images = []
    if not ex_folder.exists():
        return images
    for f in ex_folder.iterdir():
        if f.is_file() and f.suffix.lower() in ('.jpg', '.jpeg', '.png'):
            images.append(f)
    return sorted(images, key=lambda p: p.name)


def build_exhibition_data(exhibitions, all_works):
    """Enrich exhibition records with works list and gallery images."""
    for slug, folder_name in EXHIBITION_MAP.items():
        ex_folder = resolve_exhibition_folder(folder_name)
        # Find matching exhibition record
        ex_record = None
        for ex in exhibitions:
            if ex['title'] == folder_name or folder_name.startswith(ex['title'][:10]):
                ex_record = ex
                break
        if not ex_record:
            # Try substring match
            for ex in exhibitions:
                if ex['title'][:15] in folder_name or folder_name[:15] in ex['title']:
                    ex_record = ex
                    break
        if not ex_record:
            ex_record = {'title': folder_name, 'period': '', 'venue': '',
                         'venue_address': '', 'type': '', 'notes': '', 'description': ''}
            exhibitions.append(ex_record)

        ex_record['slug'] = slug
        ex_record['folder'] = ex_folder

        if ex_folder:
            # Find works CSV
            works_csv = find_exhibition_works_csv(ex_folder)
            if works_csv:
                ex_record['work_titles'] = parse_exhibition_works_csv(works_csv)
            else:
                ex_record['work_titles'] = []

            # Find gallery images
            ex_record['gallery_images'] = find_exhibition_gallery_images(ex_folder)
        else:
            print(f"  WARNING: No folder found for '{slug}' ({folder_name[:30]}...)")
            ex_record['work_titles'] = []
            ex_record['gallery_images'] = []

    return exhibitions


# ============================================================
# Step 2: Image copy & resize
# ============================================================

def resize_image(src, dst, max_width=MAX_IMG_WIDTH):
    """Copy image and resize using sips if wider than max_width."""
    shutil.copy2(src, dst)
    try:
        result = subprocess.run(
            ['sips', '-g', 'pixelWidth', str(dst)],
            capture_output=True, text=True
        )
        for line in result.stdout.split('\n'):
            if 'pixelWidth' in line:
                width = int(line.split(':')[1].strip())
                if width > max_width:
                    subprocess.run(
                        ['sips', '--resampleWidth', str(max_width), str(dst)],
                        capture_output=True
                    )
                break
    except Exception as e:
        print(f"  WARNING: sips resize failed for {dst}: {e}")


def copy_work_images(all_works):
    """Copy work detail images to images/works/."""
    IMG_WORKS_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for title, work in all_works.items():
        work_slug = slugify(title)
        work['slug'] = work_slug
        work['detail_images'] = []

        for i, img_path in enumerate(work['images']):
            img_path = Path(img_path)
            if not img_path.exists():
                continue
            ext = img_path.suffix.lower()
            if ext not in ('.jpg', '.jpeg', '.png'):
                continue
            fname = f"{work_slug}_{i+1:02d}{ext}"
            dst = IMG_WORKS_DIR / fname
            if not dst.exists():
                resize_image(img_path, dst)
                count += 1
            work['detail_images'].append(f"images/works/{fname}")

    print(f"  Copied {count} work images to images/works/")


def copy_exhibition_images(exhibitions):
    """Copy exhibition gallery images to images/exhibitions/."""
    IMG_EX_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for ex in exhibitions:
        slug = ex.get('slug')
        if not slug:
            continue
        gallery = ex.get('gallery_images', [])
        ex['web_gallery'] = []
        for i, img_path in enumerate(gallery):
            ext = img_path.suffix.lower()
            fname = f"{slug}_{i+1:02d}{ext}"
            dst = IMG_EX_DIR / fname
            if not dst.exists():
                resize_image(img_path, dst)
                count += 1
            ex['web_gallery'].append(f"images/exhibitions/{fname}")

    print(f"  Copied {count} exhibition images to images/exhibitions/")


# ============================================================
# Step 3: HTML generation helpers
# ============================================================

HEAD_TEMPLATE = '''<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">\
<meta name="viewport" content="width=device-width,initial-scale=1.0">\
<title>{title} | IWAI Mika</title>\
<link rel="preconnect" href="https://fonts.googleapis.com">\
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Noto+Serif+JP:wght@200;300;400;500&display=swap" rel="stylesheet">\
<link rel="stylesheet" href="{css_path}">
'''

NAV_TEMPLATE = '''<nav class="nav" id="nav">\
<a href="{home}" class="nav-logo">I W A I &nbsp; M i k a</a>\
<button class="nav-toggle" id="navToggle" aria-label="Menu"><span></span><span></span><span></span></button></nav>\
<div class="menu-overlay" id="menuOverlay"><ul class="menu-list">\
<li><a href="{works}" data-close>w o r k s</a></li>\
<li><a href="https://indd.adobe.com/view/e21b312c-38f5-4ff5-abfa-8757282df8ef" target="_blank">p o r t f o l i o</a></li>\
<li><a href="https://www.instagram.com/iwai_some_draw/" target="_blank">I n s t a g r a m _ w o r k s</a></li>\
<li><a href="https://www.instagram.com/iwaimika_sketch/" target="_blank">I n s t a g r a m _ d r a w i n g s</a></li>\
</ul></div>
'''

FOOTER_TEMPLATE = '''<footer class="footer">\
<nav class="footer-nav"><a href="{works}">w o r k s</a><a href="{home}">t o p</a></nav>\
<p class="footer-copy">&copy; 2023 IWAI Mika All Rights Reserved.</p>\
<div class="footer-social"><a href="https://www.instagram.com/iwai_some_draw/" target="_blank" aria-label="Instagram">\
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">\
<rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><circle cx="12" cy="12" r="5"/>\
<circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/></svg></a></div></footer>
'''

SCRIPT_TEMPLATE = '''<script>\
const tg=document.getElementById("navToggle"),ov=document.getElementById("menuOverlay");\
tg.addEventListener("click",()=>{tg.classList.toggle("active");ov.classList.toggle("active");\
document.body.style.overflow=ov.classList.contains("active")?"hidden":""});\
document.querySelectorAll("[data-close]").forEach(l=>l.addEventListener("click",()=>{\
tg.classList.remove("active");ov.classList.remove("active");document.body.style.overflow=""}));\
const ro=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){\
e.target.classList.add("visible");ro.unobserve(e.target)}})},\
{threshold:0.08,rootMargin:"0px 0px -40px 0px"});\
document.querySelectorAll(".reveal").forEach(el=>ro.observe(el));</script>
'''

LIGHTBOX_SCRIPT = '''<script>\
(function(){const lb=document.createElement("div");lb.className="lightbox";\
lb.innerHTML='<span class="lightbox-close">&times;</span><img>';\
document.body.appendChild(lb);const lbImg=lb.querySelector("img");\
document.querySelectorAll("[data-lightbox]").forEach(el=>{\
el.style.cursor="pointer";el.addEventListener("click",()=>{\
lbImg.src=el.dataset.lightbox||el.src;lb.classList.add("active");\
document.body.style.overflow="hidden"})});\
lb.addEventListener("click",()=>{lb.classList.remove("active");\
document.body.style.overflow=""})})();</script>
'''

EX_PAGE_STYLE = '''<style>\
.ex-hero{position:relative;padding-top:6rem}\
.ex-hero-img{width:100%;max-width:900px;margin:0 auto;display:block;padding:2rem}\
.ex-hero-img img{width:100%;height:auto}\
.ex-body{max-width:700px;margin:0 auto;padding:2rem 2rem 4rem;text-align:center}\
.ex-body h1{font-family:var(--font-body);font-weight:300;font-size:clamp(1.2rem,3vw,1.8rem);letter-spacing:.1em;line-height:1.8;margin-bottom:2rem}\
.ex-meta{display:flex;flex-direction:column;gap:.8rem;margin-bottom:2rem}\
.ex-meta-item{display:flex;gap:1.5rem;justify-content:center;font-size:.85rem}\
.ex-label{color:var(--text-light);min-width:3em;text-align:right}\
.ex-notes{font-size:.8rem;color:var(--text-light);line-height:1.8;margin-top:2rem;padding-top:2rem;border-top:1px solid var(--border)}\
.back-link{display:inline-block;margin-top:3rem;font-family:var(--font-display);font-size:.85rem;letter-spacing:.3em;color:var(--accent);border-bottom:1px solid var(--accent);padding-bottom:2px}\
</style>
'''


def h(text):
    """HTML-escape text."""
    return html_mod.escape(str(text)) if text else ''


# ============================================================
# Step 4: Generate work detail pages
# ============================================================

def generate_work_page(work, all_works):
    """Generate a single work detail HTML page."""
    slug = work.get('slug', slugify(work['title']))
    out_path = SITE_DIR / "works" / f"{slug}.html"

    title_h = h(work['title'])
    detail_images = work.get('detail_images', [])

    # Build metadata rows
    meta_rows = ''
    for label, val in [
        ('制作年', work.get('year', '')),
        ('サイズ', work.get('size', '')),
        ('技法', work.get('technique', '')),
        ('素材', work.get('material', '')),
        ('収蔵', work.get('collection', '')),
    ]:
        if val:
            meta_rows += (
                f'<div class="work-detail-row">'
                f'<span class="work-detail-label">{h(label)}</span>'
                f'<span>{h(val)}</span></div>'
            )

    # Main image (first detail image or thumbnail)
    main_img = ''
    if detail_images:
        main_img = f'../{detail_images[0]}'
    else:
        # Fall back to existing thumbnail
        thumb = WORK_THUMB_MAP.get(work['title'], '')
        if thumb:
            main_img = f'../images/{thumb}'

    # Gallery of additional images
    gallery_html = ''
    extra_imgs = detail_images[1:] if len(detail_images) > 1 else []
    if extra_imgs:
        items = ''
        for img in extra_imgs:
            items += (
                f'<div class="work-gallery-item reveal">'
                f'<img src="../{img}" alt="{title_h}" loading="lazy" '
                f'data-lightbox="../{img}"></div>'
            )
        gallery_html = f'<div class="work-gallery">{items}</div>'

    description_html = ''
    if work.get('description'):
        description_html = f'<p class="work-detail-desc">{h(work["description"])}</p>'

    page = HEAD_TEMPLATE.format(title=work['title'], css_path='../style.css')
    page += '''<style>\
.work-hero{position:relative;padding-top:6rem}\
.work-hero-img{width:100%;max-width:900px;margin:0 auto;display:block;padding:2rem}\
.work-hero-img img{width:100%;height:auto}\
.work-body{max-width:700px;margin:0 auto;padding:2rem 2rem 4rem;text-align:center}\
.work-body h1{font-family:var(--font-body);font-weight:300;font-size:clamp(1.2rem,3vw,1.8rem);letter-spacing:.1em;line-height:1.8;margin-bottom:2rem}\
.back-link{display:inline-block;margin-top:3rem;font-family:var(--font-display);font-size:.85rem;letter-spacing:.3em;color:var(--accent);border-bottom:1px solid var(--accent);padding-bottom:2px}\
</style>
'''
    page += '</head><body>\n'
    page += NAV_TEMPLATE.format(home='../index.html', works='../works.html')

    # Hero image
    if main_img:
        page += (
            f'<div class="work-hero"><div class="work-hero-img">'
            f'<img src="{main_img}" alt="{title_h}" data-lightbox="{main_img}">'
            f'</div></div>\n'
        )

    # Body
    page += f'<div class="work-body"><h1>{title_h}</h1>\n'
    if meta_rows:
        page += f'<div class="work-detail-meta">{meta_rows}</div>\n'
    if description_html:
        page += description_html + '\n'

    # Gallery
    if gallery_html:
        page += gallery_html + '\n'

    page += '<a href="../works.html" class="back-link">&larr; b a c k</a>\n'
    page += '</div>\n'

    page += FOOTER_TEMPLATE.format(works='../works.html', home='../index.html')
    page += SCRIPT_TEMPLATE
    page += LIGHTBOX_SCRIPT
    page += '</body></html>'

    out_path.write_text(page, encoding='utf-8')
    return slug


def generate_all_work_pages(all_works):
    """Generate all work detail pages."""
    works_dir = SITE_DIR / "works"
    works_dir.mkdir(exist_ok=True)
    count = 0
    for title, work in all_works.items():
        slug = work.get('slug', slugify(title))
        # Double-check template exclusion on the slug level
        if is_template(title) or is_template(slug):
            continue
        try:
            generate_work_page(work, all_works)
            count += 1
        except Exception as e:
            print(f"  WARNING: Failed to generate page for '{title}': {e}")
    # Clean up any template pages that might have been generated previously
    for p in works_dir.glob("*.html"):
        if is_template(p.stem):
            p.unlink()
    print(f"  Generated {count} work detail pages in works/")


# ============================================================
# Step 5: Generate enhanced exhibition pages
# ============================================================

def generate_exhibition_page(ex, all_works):
    """Generate an enhanced exhibition HTML page."""
    slug = ex['slug']
    title = ex['title']
    title_h = h(title)
    out_path = SITE_DIR / "exhibitions" / f"{slug}.html"

    # Existing hero image
    # Map slug to existing image filename from index.html
    ex_img_map = {
        'houmaku': 'ex_houmaku.jpg',
        'flowers-journey2024': 'ex_flowers_journey.jpg',
        'artfairtokyo2023': 'ex_artfair2023.jpg',
        'souvin': 'ex_souvin.jpg',
        'doctor2022': 'ex_doctor2022.jpg',
        '100colors': 'ex_100colors.jpg',
        'doctor2021': 'ex_doctor2021.jpg',
        'artbase': 'ex_artbase.jpg',
        'art-nagoya-2020': 'ex_artnagoya.jpg',
        'assenblemoments': 'ex_assenble.jpg',
        'butokan': 'ex_butokan.jpg',
        'portreport': 'ex_portreport.jpg',
        'artsplanet': 'ex_artsplanet.jpg',
        'toiyastudio2017': 'ex_toiya.jpg',
        'visual-sonic-2016': 'ex_visualsonic.jpg',
        'real': 'ex_real.jpg',
    }
    hero_img = ex_img_map.get(slug, f'ex_{slug}.jpg')

    page = HEAD_TEMPLATE.format(title=title, css_path='../style.css')
    page += EX_PAGE_STYLE
    page += '</head><body>\n'
    page += NAV_TEMPLATE.format(home='../index.html', works='../works.html')

    # Hero
    page += (
        f'<div class="ex-hero"><div class="ex-hero-img">'
        f'<img src="../images/{hero_img}" alt="{title_h}">'
        f'</div></div>\n'
    )

    # Body
    page += f'<div class="ex-body"><h1>{title_h}</h1>\n'

    # Metadata
    page += '<div class="ex-meta">'
    if ex.get('period'):
        page += (
            f'<div class="ex-meta-item"><span class="ex-label">期間</span>'
            f'<span>{h(ex["period"])}</span></div>'
        )
    if ex.get('venue'):
        page += (
            f'<div class="ex-meta-item"><span class="ex-label">会場</span>'
            f'<span>{h(ex["venue"])}</span></div>'
        )
    if ex.get('type'):
        page += (
            f'<div class="ex-meta-item"><span class="ex-label">形式</span>'
            f'<span>{h(ex["type"])}</span></div>'
        )
    page += '</div>\n'

    # Description
    if ex.get('description'):
        page += f'<div class="ex-description reveal"><p>{h(ex["description"])}</p></div>\n'

    # Notes (備考)
    if ex.get('notes'):
        notes_text = ex['notes'].replace('\n', '<br>')
        page += f'<div class="ex-notes reveal">{notes_text}</div>\n'

    page += '</div>\n'  # end ex-body

    # Gallery section
    web_gallery = ex.get('web_gallery', [])
    if web_gallery:
        page += '<section class="section ex-gallery-section">\n'
        page += '<h2 class="section-title reveal">G a l l e r y</h2>\n'
        page += '<div class="ex-gallery">\n'
        for img in web_gallery:
            page += (
                f'<div class="ex-gallery-item reveal">'
                f'<img src="../{img}" alt="{title_h}" loading="lazy" '
                f'data-lightbox="../{img}"></div>\n'
            )
        page += '</div></section>\n'

    # Exhibited works section
    work_titles = ex.get('work_titles', [])
    matched_works = []
    for wt in work_titles:
        if wt in all_works:
            matched_works.append(all_works[wt])
        else:
            # Try fuzzy match
            for k, v in all_works.items():
                if wt in k or k in wt:
                    matched_works.append(v)
                    break

    if matched_works:
        page += '<section class="section ex-works-section">\n'
        page += '<h2 class="section-title reveal">E x h i b i t e d &nbsp; W o r k s</h2>\n'
        page += '<div class="ex-works-grid">\n'
        for w in matched_works:
            w_slug = w.get('slug', slugify(w['title']))
            # Find thumbnail
            thumb = WORK_THUMB_MAP.get(w['title'], '') or WORK_THUMB_MAP.get(normalize_title(w['title']), '')
            thumb_src = f'../images/{thumb}' if thumb else ''
            if not thumb_src and w.get('detail_images'):
                thumb_src = f'../{w["detail_images"][0]}'
            w_title_h = h(w['title'])
            page += (
                f'<a class="card reveal" href="../works/{w_slug}.html">'
                f'<div class="card-image">'
            )
            if thumb_src:
                page += f'<img src="{thumb_src}" alt="{w_title_h}" loading="lazy">'
            page += f'</div><div class="card-title">{w_title_h}</div></a>\n'
        page += '</div></section>\n'

    # Back link (outside ex-body, in its own container)
    page += '<div style="text-align:center;padding:0 2rem 4rem">'
    page += '<a href="../index.html" class="back-link">&larr; b a c k</a></div>\n'

    page += FOOTER_TEMPLATE.format(works='../works.html', home='../index.html')
    page += SCRIPT_TEMPLATE
    if web_gallery:
        page += LIGHTBOX_SCRIPT
    page += '</body></html>'

    out_path.write_text(page, encoding='utf-8')


def generate_all_exhibition_pages(exhibitions, all_works):
    """Generate all enhanced exhibition pages."""
    count = 0
    for ex in exhibitions:
        if not ex.get('slug'):
            continue
        try:
            generate_exhibition_page(ex, all_works)
            count += 1
        except Exception as e:
            print(f"  WARNING: Failed to generate exhibition '{ex.get('slug')}': {e}")
    print(f"  Generated {count} exhibition pages")


# ============================================================
# Step 6: Update works.html
# ============================================================


# Ordered list of works as they appear in the original works.html
# Each entry: (thumbnail_filename, display_title)
WORKS_ORDER = [
    ("w_houmaku_series.jpg", "「胞膜のシリーズについて」"),
    ("w_sketch_tulip02.jpg", "《sketch -TULIP- 02》"),
    ("w_sketch_yukitsubaki.jpg", "《sketch -雪の日、椿-》"),
    ("w_magnolia.jpg", "《満ちる花 -MAGNOLIA-》"),
    ("w_omokage_sky.jpg", "《面影 -SKY-》"),
    ("w_astrantia.jpg", "《満ちる花 -ASTRANTIA-》"),
    ("w_calla_lily.jpg", "《満ちる花 -CALLA LILY-》"),
    ("w_sketch_tulip01.jpg", "《sketch -TULIP- 01》"),
    ("w_tulip02.jpg", "《満ちる花-TULIP- 02》"),
    ("w_omokage_water.jpg", "《面影 -WATER-》"),
    ("w_omokage_tulip01.jpg", "《面影 -TULIP- 01》"),
    ("w_sketch_sarusuberi.jpg", "《sketch -さるすべり-》"),
    ("w_poppy.jpg", "《満ちる花 -POPPY-》"),
    ("w_tulip.jpg", "《満ちる花 -TULIP-》"),
    ("w_sakura.jpg", "《 櫻 》"),
    ("w_mitsu.jpg", "《 満 つ 》"),
    ("w_flowercells_coral.jpg", "《flower cells -coral and blue colors-》"),
    ("w_flowercells_red.jpg", "《flower cells -red hydrangea-》"),
    ("w_flowercells_blue.jpg", "《flower cells -blue hydrangea-》"),
    ("w_flowercells_camellia.jpg", "《flower cells -camellia-》"),
    ("w_kokuoku11.jpg", "刻憶202211"),
    ("w_kokuoku06.jpg", "刻憶06ー木蓮ー"),
    ("w_kokuoku05.jpg", "刻憶05ー木蓮ー"),
    ("w_mizuasobi.jpg", "みずあそび"),
    ("w_poppy2.jpg", "ポピー"),
    ("w_ajisai.jpg", "紫陽花"),
    ("w_kokuoku04.jpg", "刻憶04 –芍薬−"),
    ("w_kokuoku03.jpg", "刻憶03 −木蓮−"),
    ("w_halipuu.jpg", "つなぐの森ハリプー、装飾布"),
    ("w_kokuoku02.jpg", "刻憶02 −ポピー−"),
    ("w_kokuoku01.jpg", "刻憶01 −ポピー−"),
    ("w_line03.jpg", "Line Growth order 03 −木蓮−"),
    ("w_line02.jpg", "Line Growth order 02 −tree and flower−"),
    ("w_sketch2021a.jpg", "sketch 202012-202104"),
    ("w_sketch2021b.jpg", "sketch 202101-202103"),
    ("w_tree02.jpg", "tree 20210308"),
    ("w_tree01.jpg", "tree 20210127"),
    ("w_dyedweeping02.jpg", "dyed-weeping-line02"),
    ("w_dyedweeping01.jpg", "dyed-weeping-line01"),
    ("w_boumaku08.jpg", "望膜08"),
    ("w_observation.jpg", "observation"),
    ("w_uncontrol.jpg", "uncontrol"),
    ("w_boumaku07.jpg", "望膜07 あじさい"),
    ("w_glue.jpg", "Glue Growth order -flower-"),
    ("w_kasabuta03.jpg", "やわらかな瘡蓋 03"),
    ("w_tokiwokiku.jpg", "時を聴く"),
    ("w_apiece02.jpg", "A piece of Days 02"),
    ("w_apiece01.jpg", "A piece of Days 01"),
    ("w_irokara.jpg", "色から空へ 空から色へ"),
]


def generate_works_html(all_works):
    """Regenerate works.html from scratch with links to detail pages."""
    out = SITE_DIR / "works.html"

    page = HEAD_TEMPLATE.format(title='w o r k s', css_path='style.css')
    page += '''<style>\
.page-header{padding:8rem 2rem 3rem;text-align:center}\
.page-header h1{font-family:var(--font-display);font-weight:400;font-size:1.2rem;letter-spacing:.5em}\
.page-header p{font-size:.8rem;color:var(--text-light);margin-top:1rem;line-height:1.8;max-width:700px;margin-left:auto;margin-right:auto}\
.work-card{overflow:hidden;background:var(--white)}\
.work-card .card-image{position:relative;aspect-ratio:4/3;overflow:hidden}\
.work-card .card-image img{width:100%;height:100%;object-fit:cover}\
.work-card .card-title{padding:1.2rem 1.4rem;font-size:.85rem;font-weight:300;line-height:1.6;letter-spacing:.04em}\
</style>\n'''
    page += '</head><body>\n'
    page += NAV_TEMPLATE.format(home='index.html', works='works.html')
    page += (
        '<header class="page-header"><h1>w o r k s</h1>'
        '<p>染織作家 / Textile Artist<br>'
        '記憶の手ざわりを頼りに、モチーフの有する「しなやかな生命力」を染め、縫い留める。<br>'
        'Depicts the resilient vitality inherent in motifs, utilizing textile dyeing and embroidery techniques.'
        '</p></header>\n'
    )
    page += '<section class="section" style="padding-top:2rem"><div class="card-grid">'

    linked = 0
    for thumb, title in WORKS_ORDER:
        title_h = h(title)
        # Find matching work for link (try exact, then normalized, then substring)
        norm_title = normalize_title(title)
        work = all_works.get(title)
        if not work:
            for k, v in all_works.items():
                if normalize_title(k) == norm_title:
                    work = v
                    break
        if not work:
            for k, v in all_works.items():
                if title in k or k in title:
                    work = v
                    break
        if work:
            slug = work.get('slug', slugify(work['title']))
            page += (
                f'<a class="work-card reveal" href="works/{slug}.html">'
                f'<div class="card-image">'
                f'<img src="images/{thumb}" alt="{title_h}" loading="lazy">'
                f'</div>'
                f'<div class="card-title">{title_h}</div></a>\n'
            )
            linked += 1
        else:
            page += (
                f'<div class="work-card reveal">'
                f'<div class="card-image">'
                f'<img src="images/{thumb}" alt="{title_h}" loading="lazy">'
                f'</div>'
                f'<div class="card-title">{title_h}</div></div>\n'
            )

    page += '</div></section>\n'
    page += FOOTER_TEMPLATE.format(works='works.html', home='index.html')
    page += SCRIPT_TEMPLATE
    page += '</body></html>'

    out.write_text(page, encoding='utf-8')
    print(f"  Regenerated works.html: {linked} linked, {len(WORKS_ORDER) - linked} unlinked cards")


# ============================================================
# Main
# ============================================================

def main():
    print("=== build.py: Enriching some-draw.page ===\n")

    # Step 1: Parse data
    print("[1/6] Parsing data...")
    build_work_thumb_map()
    print(f"  Found {len(WORK_THUMB_MAP)} existing work thumbnails")

    exhibitions = parse_main_csv()
    print(f"  Parsed {len(exhibitions)} exhibitions from CSV")

    all_works = parse_all_works()
    print(f"  Parsed {len(all_works)} works from markdown files")

    # Assign slugs to works
    for title, work in all_works.items():
        work['slug'] = slugify(title)

    # Enrich exhibitions with folder data
    exhibitions = build_exhibition_data(exhibitions, all_works)
    ex_with_slug = [e for e in exhibitions if e.get('slug')]
    print(f"  Mapped {len(ex_with_slug)} exhibitions to folders")

    # Step 2: Copy images
    print("\n[2/6] Copying images...")
    copy_work_images(all_works)
    copy_exhibition_images(ex_with_slug)

    # Step 3: CSS is handled separately (added to style.css)
    print("\n[3/6] CSS styles should be in style.css (manual step)")

    # Step 4: Generate work detail pages
    print("\n[4/6] Generating work detail pages...")
    generate_all_work_pages(all_works)

    # Step 5: Generate enhanced exhibition pages
    print("\n[5/6] Generating exhibition pages...")
    generate_all_exhibition_pages(ex_with_slug, all_works)

    # Step 6: Update works.html
    print("\n[6/6] Updating works.html...")
    generate_works_html(all_works)

    print("\n=== Build complete! ===")
    print("Run: python3 -m http.server 8000")
    print("Then open: http://localhost:8000")


if __name__ == '__main__':
    main()
