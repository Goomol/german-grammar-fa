#!/usr/bin/env python3
"""Build the single-file German grammar app from content/*.txt + template.html."""
import re, json, html, glob, base64, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
LEVELS = [
    ("A1.1", "A1.1", "شروع از صفر: معرفی خود، جمله‌های ساده، زمان حال، حرف تعریف و حالت مفعولی"),
    ("A1.2", "A1.2", "افعال وجهی، امر، گذشته (Perfekt)، حالت Dativ و حروف اضافه"),
    ("A2.1", "A2.1", "جمله‌واره‌ها (weil، dass، wenn)، حروف اضافه دوحالته، صرف صفت، مقایسه"),
    ("A2.2", "A2.2", "Präteritum، جمله موصولی، Konjunktiv II مؤدبانه، فعل‌های حرف‌اضافه‌دار، Passiv"),
    ("B1.1", "B1.1", "Plusquamperfekt، Genitiv، جمله‌های زمانی، um…zu، Passiv کامل، Konjunktiv II"),
    ("B1.2", "B1.2", "Konjunktiv II گذشته، حروف ربط دوبخشی، صفت‌های فعلی، واژه‌سازی، جایگاه nicht"),
    ("B2.1", "B2.1", "نقل قول غیرمستقیم، جایگزین‌های Passiv، صفت‌های فعلی گسترده، کاربرد ذهنی افعال وجهی"),
    ("B2.2", "B2.2", "سبک اسمی، حروف اضافه پیشرفته، es، ادات گفتاری، ترتیب واژه‌ها در سطح پیشرفته"),
    ("X", "ضمیمه", "جدول‌های مرجع: افعال بی‌قاعده، صرف‌ها، فعل‌های حرف‌اضافه‌دار"),
]
LEVEL_KEYS = [l[0] for l in LEVELS]

CALLOUTS = {
    "tip": ("ترفند", "lightbulb"),
    "fa": ("مقایسه با فارسی", "translate"),
    "warn": ("دام رایج", "warning"),
    "note": ("نکته", "info"),
    "rule": ("قاعده", "rule"),
    "remember": ("یادآوری از درس‌های قبل", "history"),
}

ARABIC = re.compile(r'[؀-ۿ]')
LATIN = re.compile(r'[A-Za-zÄÖÜäöüß]')


ICONS = {
 "lightbulb": "M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z",
 "translate": "M12.87 15.07l-2.54-2.51.03-.03A17.52 17.52 0 0 0 14.07 6H17V4h-7V2H8v2H1v1.99h11.17C11.5 7.92 10.44 9.75 9 11.35 8.07 10.32 7.3 9.19 6.69 8h-2c.73 1.63 1.73 3.17 2.98 4.56l-5.09 5.02L4 19l5-5 3.11 3.11.76-2.04zM18.5 10h-2L12 22h2l1.12-3h4.75L21 22h2l-4.5-12zm-2.62 7l1.62-4.33L19.12 17h-3.24z",
 "warning": "M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z",
 "info": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z",
 "rule": "M16.54 11 13 7.46l1.41-1.41 2.12 2.12 4.24-4.24 1.41 1.41L16.54 11zM11 7H2v2h9V7zm10 6.41L19.59 12 17 14.59 14.41 12 13 13.41 15.59 16 13 18.59 14.41 20 17 17.41 19.59 20 21 18.59 18.41 16 21 13.41zM11 15H2v2h9v-2z",
 "history": "M13 3a9 9 0 0 0-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42A8.954 8.954 0 0 0 13 21a9 9 0 0 0 0-18zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z",
 "menu": "M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z",
 "search": "M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z",
 "close": "M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z",
 "arrow_back": "M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z",
 "arrow_forward": "M12 4l-1.41 1.41L16.17 11H4v2h12.17l-5.58 5.59L12 20l8-8z",
 "expand_more": "M16.59 8.59 12 13.17 7.41 8.59 6 10l6 6 6-6z",
 "check_circle": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z",
 "circle": "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z",
 "check": "M9 16.17 4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
 "home": "M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z",
 "dark_mode": "M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.389 5.389 0 0 1-4.4 2.26 5.403 5.403 0 0 1-3.14-9.8c-.44-.06-.9-.1-1.36-.1z",
 "light_mode": "M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37a.996.996 0 0 0-1.41 0 .996.996 0 0 0 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0a.996.996 0 0 0 0-1.41l-1.06-1.06zm1.06-10.96a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36a.996.996 0 0 0 0-1.41.996.996 0 0 0-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z",
 "format_size": "M9 4v3h5v12h3V7h5V4H9zm-6 8h3v7h3v-7h3V9H3v3z",
 "toc": "M3 9h14V7H3v2zm0 4h14v-2H3v2zm0 4h14v-2H3v2zm16 0h2v-2h-2v2zm0-10v2h2V7h-2zm0 6h2v-2h-2v2z",
 "school": "M5 13.18v4L12 21l7-3.82v-4L12 17l-7-3.82zM12 3 1 9l11 6 9-4.91V17h2V9L12 3z",
 "link": "M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z",
 "quiz": "M11 18h2v-2h-2v2zm1-16C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-2.21 0-4 1.79-4 4h2c0-1.1.9-2 2-2s2 .9 2 2c0 2-3 1.75-3 5h2c0-2.25 3-2.5 3-5 0-2.21-1.79-4-4-4z",
 "volume": "M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 7.97v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z",
 "play": "M8 5v14l11-7z",
 "book": "M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z",
}


def icons_css():
    from urllib.parse import quote
    out = []
    for k, d in ICONS.items():
        svg = f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='{d}'/></svg>"
        u = f'url("data:image/svg+xml,{quote(svg, safe="/:=\' ")}")'
        out.append(f'.ic-{k}{{--i:{u}}}')
        if k == "link":
            out.append(f':root{{--link-i:{u}}}')
    return "\n".join(out)


errors = []
lessons = []          # dicts
lesson_index = {}     # id -> lesson
anchors = {}          # id -> set(anchor)


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


class Ctx:
    def __init__(self, lid):
        self.lid = lid
        self.links = []
        self.secs = []
        self.n_sec = 0


def strip_marks(s):
    s = re.sub(r'\{[mfnp]\|([^}]*)\}', r'\1', s)
    s = s.replace('**', '').replace('~~', '').replace('`', '')
    return s


GENDER_CLS = {"m": "g-m", "f": "g-f", "n": "g-n", "p": "g-p"}


def inline(s, ctx, in_de=False):
    """Inline markup -> HTML. Supports [[link]], `german`, **bold**, ~~wrong~~, {m|der Tisch}."""
    holders = []

    def hold(h):
        holders.append(h)
        return f"\x00{len(holders)-1}\x00"

    # links first
    def link(m):
        target, _, text = m.group(1).partition('|')
        lid, _, anc = target.partition('#')
        ctx.links.append((lid.strip(), anc.strip()))
        href = f"#/l/{lid.strip()}" + (f"/{anc.strip()}" if anc else "")
        inner = inline(text, ctx) if text else f"\x01TITLE:{lid.strip()}\x01"
        return hold(f'<a class="xref" href="{href}" data-l="{lid.strip()}">{inner}</a>')
    s = re.sub(r'\[\[([^\]]+)\]\]', link, s)

    # german code spans
    def de(m):
        inner = m.group(1)
        nw = ' nw' if len(strip_marks(inner)) <= 30 else ''
        return hold(f'<span class="de{nw}" dir="ltr" lang="de">{inline(inner, ctx, True)}</span>')
    if not in_de:
        s = re.sub(r'`([^`]+)`', de, s)

    def gender(m):
        if in_de:
            return hold(f'<span class="{GENDER_CLS[m.group(1)]}">{inline(m.group(2), ctx, True)}</span>')
        return hold(f'<span class="de nw {GENDER_CLS[m.group(1)]}" dir="ltr" lang="de">{inline(m.group(2), ctx, True)}</span>')
    s = re.sub(r'\{([mfnp])\|([^}]*)\}', gender, s)

    # escape remaining text
    parts = re.split(r'(\x00\d+\x00)', s)
    s = ''.join(p if re.fullmatch(r'\x00\d+\x00', p) else (esc(p) if in_de else esc(p).replace('→', '←')) for p in parts)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'~~(.+?)~~', r'<s class="wrong">\1</s>', s)
    # restore
    for _ in range(4):
        s = re.sub(r'\x00(\d+)\x00', lambda m: holders[int(m.group(1))], s)
    return s


def cell(s, ctx):
    # returns (html, is_german)
    s = s.strip()
    plain = strip_marks(s)
    if plain and not ARABIC.search(plain) and LATIN.search(plain) and '`' not in s:
        return f'<span class="de" dir="ltr" lang="de">{inline(s, ctx, True)}</span>', True
    return inline(s, ctx), False


SPEAK_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 7.97v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>'


def split_row(r):
    r = r.strip()
    if r.startswith('|'):
        r = r[1:]
    if r.endswith('|'):
        r = r[:-1]
    cells, buf, depth_b, depth_l, k = [], '', 0, 0, 0
    while k < len(r):
        c = r[k]
        if r.startswith('[[', k):
            depth_l += 1; buf += '[['; k += 2; continue
        if r.startswith(']]', k) and depth_l:
            depth_l -= 1; buf += ']]'; k += 2; continue
        if c == '{':
            depth_b += 1
        elif c == '}' and depth_b:
            depth_b -= 1
        if c == '|' and not depth_b and not depth_l:
            cells.append(buf); buf = ''
        else:
            buf += c
        k += 1
    cells.append(buf)
    return cells


def render_blocks(lines, ctx):
    out = []
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith(':::'):
            spec = s[3:].strip()
            kind, _, title = spec.partition(' ')
            if kind not in CALLOUTS:
                errors.append(f"{ctx.lid}: unknown callout {kind!r}")
            j = i + 1
            inner = []
            while j < n and lines[j].strip() != ':::':
                inner.append(lines[j])
                j += 1
            if j >= n:
                errors.append(f"{ctx.lid}: unclosed callout {kind}")
            label, icon = CALLOUTS.get(kind, ("", "info"))
            head = inline(title, ctx) if title else label
            out.append(f'<aside class="co co-{kind}"><div class="co-h"><i class="ic ic-{icon}"></i><span>{head}</span></div>'
                       f'<div class="co-b">{render_blocks(inner, ctx)}</div></aside>')
            i = j + 1
            continue
        m = re.match(r'^(#{2,3})\s+(.*?)(?:\s*\{#([\w-]+)\})?$', s)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            if level == 2:
                ctx.n_sec += 1
                anc = m.group(3) or f"s{ctx.n_sec}"
                hid = f"{ctx.lid}--{anc}"
                ctx.secs.append({"a": anc, "t": strip_marks(title)})
                anchors.setdefault(ctx.lid, set()).add(anc)
                out.append(f'<h2 id="{hid}" data-a="{anc}">{inline(title, ctx)}</h2>')
            else:
                if m.group(3):
                    anchors.setdefault(ctx.lid, set()).add(m.group(3))
                    out.append(f'<h3 id="{ctx.lid}--{m.group(3)}" data-a="{m.group(3)}">{inline(title, ctx)}</h3>')
                else:
                    out.append(f'<h3>{inline(title, ctx)}</h3>')
            i += 1
            continue
        if s.startswith('|'):
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                r = lines[i].strip()
                if not re.fullmatch(r'\|[\s\-:|]+\|?', r):
                    cells = split_row(r)
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            def th(c):
                return f'<th>{cell(c, ctx)[0]}</th>'
            def td(c):
                html_, de_ = cell(c, ctx)
                if not c.strip():
                    return '<td></td>'
                if de_:
                    return '<td class="long">' + html_ + '</td>' if len(strip_marks(c.strip())) > 26 else f'<td>{html_}</td>'
                return f'<td class="fa">{html_}</td>'
            wide = ' class="wide"' if len(head) >= 4 else ''
            h = f'<div class="tw"><table{wide}><thead><tr>' + ''.join(th(c) for c in head) + '</tr></thead><tbody>'
            for r in body:
                h += '<tr>' + ''.join(td(c) for c in r) + '</tr>'
            h += '</tbody></table></div>'
            out.append(h)
            continue
        if s.startswith('> '):
            items = []
            while i < n and lines[i].strip().startswith('> '):
                t = lines[i].strip()[2:]
                de_part, sep, fa_part = t.partition(' = ')
                say = strip_marks(de_part).strip()
                say = re.sub(r'^\([^)]*\)\s*', '', say)
                row = (f'<div class="ex-r"><button class="spk" data-say="{attr(say)}" aria-label="تلفظ">{SPEAK_ICON}</button>'
                       f'<div class="ex-t"><div class="de" dir="ltr" lang="de">{inline(de_part, ctx, True)}</div>')
                if sep:
                    row += f'<div class="ex-fa">{inline(fa_part, ctx)}</div>'
                row += '</div></div>'
                items.append(row)
                i += 1
            out.append('<div class="ex">' + ''.join(items) + '</div>')
            continue
        if s.startswith('?? '):
            items = []
            while i < n and lines[i].strip().startswith('?? '):
                q, _, a = lines[i].strip()[3:].partition(' => ')
                items.append(f'<details class="qz"><summary><span class="qz-q">{inline(q, ctx)}</span><span class="qz-hint">نمایش پاسخ</span></summary><div class="qz-a">{inline(a, ctx)}</div></details>')
                i += 1
            out.append('<div class="qzs">' + ''.join(items) + '</div>')
            continue
        if s.startswith('- '):
            items = []
            while i < n and lines[i].strip().startswith('- '):
                items.append(f'<li>{inline(lines[i].strip()[2:], ctx)}</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue
        if re.match(r'^\d+\.\s', s):
            items = []
            while i < n and re.match(r'^\d+\.\s', lines[i].strip()):
                items.append(f'<li>{inline(re.sub(r"^\d+\.\s+", "", lines[i].strip()), ctx)}</li>')
                i += 1
            out.append('<ol>' + ''.join(items) + '</ol>')
            continue
        # paragraph
        para = []
        while i < n:
            t = lines[i].strip()
            if not t or t.startswith((':::', '#', '|', '> ', '?? ', '- ')) or re.match(r'^\d+\.\s', t):
                break
            para.append(t)
            i += 1
        out.append(f'<p>{inline(" ".join(para), ctx)}</p>')
    return '\n'.join(out)


def parse_all():
    files = sorted(glob.glob(os.path.join(ROOT, 'content', '*.txt')))
    for f in files:
        text = open(f, encoding='utf-8').read()
        chunks = re.split(r'^@@\s+', text, flags=re.M)
        for ch in chunks[1:]:
            lid, _, rest = ch.partition('\n')
            lid = lid.strip()
            head, sep, body = rest.partition('\n---\n')
            if not sep:
                errors.append(f"{lid}: missing --- separator")
            meta = {}
            for line in head.splitlines():
                if ':' in line:
                    k, _, v = line.partition(':')
                    meta[k.strip()] = v.strip()
            if lid in lesson_index:
                errors.append(f"duplicate id {lid}")
            ctx = Ctx(lid)
            body_html = render_blocks(body.splitlines(), ctx)
            lv = meta.get('level', '?')
            if lv not in LEVEL_KEYS:
                errors.append(f"{lid}: bad level {lv}")
            L = {
                "id": lid, "lv": lv, "t": meta.get('title', lid), "de": meta.get('de', ''),
                "sum": meta.get('summary', ''), "tags": meta.get('tags', ''),
                "k0": meta.get("tags", "").split(",")[0].strip(), "html": body_html, "sumh": inline(meta.get("summary", ""), ctx), "secs": ctx.secs, "_links": ctx.links,
            }
            lessons.append(L)
            lesson_index[lid] = L


def plain(h):
    h = re.sub(r'<svg.*?</svg>', ' ', h, flags=re.S)
    h = re.sub(r'<span class="qz-hint">.*?</span>', ' ', h)
    h = re.sub(r'<[^>]+>', ' ', h)
    h = html.unescape(h)
    h = re.sub(r'[ً-ْٰ]', '', h)
    return re.sub(r'\s+', ' ', h).strip()


def finalize():
    # order lessons by level order (stable within file order)
    lessons.sort(key=lambda L: LEVEL_KEYS.index(L['lv']) if L['lv'] in LEVEL_KEYS else 99)
    for k, L in enumerate(lessons):
        L['n'] = k + 1
    pos = {L['id']: k for k, L in enumerate(lessons)}
    for L in lessons:
        refs = []
        for lid, anc in L['_links']:
            if lid not in lesson_index:
                errors.append(f"{L['id']}: broken link -> {lid}")
                continue
            if anc and anc not in anchors.get(lid, set()):
                errors.append(f"{L['id']}: broken anchor -> {lid}#{anc}")
            if lid != L['id'] and lid not in refs:
                refs.append(lid)
        L['refs'] = refs
        # resolve link titles
        L['html'] = re.sub(r'\x01TITLE:([\w-]+)\x01',
                           lambda m: esc(lesson_index[m.group(1)]['t']) if m.group(1) in lesson_index else m.group(1),
                           L['html'])
    for L in lessons:
        L['back'] = [M['id'] for M in lessons if L['id'] in M['refs'] and pos[M['id']] > pos[L['id']]]
        L['prev'] = [r for r in L['refs'] if pos[r] < pos[L['id']]]
    # search index: per section text
    search = []
    for k, L in enumerate(lessons):
        parts = re.split(r'(?=<h2 )', L['html'])
        intro = parts[0] if not parts[0].startswith('<h2') else ''
        search.append([k, -1, L['t'] + ' ' + L['de'], plain(strip_marks(L['sum']) + ' ' + L['tags'].replace(',', '،') + ' ' + intro)])
        si = 0
        for p in parts:
            if p.startswith('<h2'):
                search.append([k, si, L['secs'][si]['t'], plain(p)])
                si += 1
    data = {
        "levels": [{"k": k, "name": nm, "d": d} for k, nm, d in LEVELS],
        "lessons": [{k: L[k] for k in ("id", "lv", "n", "t", "de", "k0", "sumh", "html", "secs", "prev", "back")} for L in lessons],
        "search": search,
    }
    return data


def main():
    parse_all()
    data = finalize()
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  ", e)
    tpl = open(os.path.join(ROOT, 'template.html'), encoding='utf-8').read()
    font = base64.b64encode(open(os.path.join(ROOT, 'vendor/Vazirmatn-NL-wght.woff2'), 'rb').read()).decode()
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    out = tpl.replace('__FONT_B64__', font).replace('__DATA_JSON__', js).replace('/*__ICONS_CSS__*/', icons_css())
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    path = os.path.join(ROOT, 'dist', 'german-grammar-fa.html')
    open(path, 'w', encoding='utf-8').write(out)
    by = {}
    for L in lessons:
        by[L['lv']] = by.get(L['lv'], 0) + 1
    print(f"lessons: {len(lessons)}  {by}  size: {len(out)/1024:.0f} KB")
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
