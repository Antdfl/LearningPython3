#!/usr/bin/env python3
"""
utilities/md_pdf_pro.py

Professional PDF renderer for build_md_toc.py: cover page, clickable table
of contents with dotted leaders and page numbers, "pagina X di Y" footer,
PDF bookmarks, "Indice" back-links, repeating table headers.

Why not xhtml2pdf (used by the plain PDF path): it has no flexbox, no running
footer with the total page count, no PDF outline and no way to know on which
page a heading lands. The page already installed on every Windows PC solves
all of that: Chrome/Edge, driven through Playwright (no browser download,
the system browser is used).

TOC page numbers need two passes, because the layout engine cannot look
ahead: pass 1 renders with placeholder numbers, the PDF outline is then read
back with pypdf to learn the real page of every heading, pass 2 renders again
with the real numbers. Placeholders and real numbers take the same space, so
the layout does not move between the two passes.

Dependencies: playwright, pypdf (pip install playwright pypdf). Pygments is
optional (syntax-highlighted code blocks).
"""
import datetime
import html
import io
import re
import unicodedata
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter
    PRO_PDF_AVAILABLE = True
except ImportError:
    PRO_PDF_AVAILABLE = False

try:
    import pygments  # noqa: F401
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


TOC_TITLE = "Indice"
BACK_LABEL = "↑ Indice"
TOC_INTRO = (
    "Ogni voce è cliccabile e porta alla sezione. Accanto a ogni titolo "
    "del documento, il rimando «Indice» riporta a questa pagina. Il pannello "
    "dei segnalibri del lettore PDF contiene anche i titoli di terzo e "
    "quarto livello."
)
TOC_MAX_LEVEL = 2          # levels listed in the printed TOC (bookmarks list all)
BACK_MAX_LEVEL = 3         # levels that get the "Indice" back-link
CHROME_CHANNELS = ("chrome", "msedge")

_MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
         "agosto", "settembre", "ottobre", "novembre", "dicembre"]

_HEADING_RE = re.compile(r'<h([1-6])\b[^>]*>(.*?)</h\1>', re.S)

CSS = """
@page { size: A4; }
:root {
    --blue: #1a5b9c; --navy: #14325a; --ink: #1f2430; --muted: #5f6b7c;
    --line: #d5dbe6; --head: #e3ebf6; --zebra: #f8fafc;
}
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
    font-family: 'Inter','Segoe UI',Arial,sans-serif;
    font-size: 10pt; line-height: 1.6; color: var(--ink); margin: 0;
}
p { margin: 0 0 8px 0; }
ul, ol { margin: 4px 0 10px 0; padding-left: 22px; }
li { margin-bottom: 3px; }
a { color: var(--blue); text-decoration: none; }
strong { font-weight: 700; }
hr { border: none; border-top: 1px solid var(--line); margin: 16px 0; }
img { max-width: 100%; height: auto; }

/* ── Cover ── */
.cover {
    height: 252mm; display: flex; flex-direction: column; justify-content: center;
    border-left: 6px solid var(--blue); padding-left: 16mm; break-after: page;
}
.cover .eyebrow {
    font-size: 8.5pt; font-weight: 700; letter-spacing: 2px;
    text-transform: uppercase; color: var(--blue); margin-bottom: 14px;
}
.cover .title { font-size: 34pt; line-height: 1.12; font-weight: 700; letter-spacing: -.8px; margin: 0 0 16px 0; }
.cover .subtitle { font-size: 14pt; line-height: 1.4; color: var(--muted); margin: 0 0 56px 0; max-width: 140mm; }
.cover table.meta { width: 150mm; border-collapse: collapse; font-size: 10pt; }
.cover table.meta td { border: none; border-top: 1px solid var(--line); padding: 9px 4px; vertical-align: top; background: none; }
.cover table.meta tr:last-child td { border-bottom: 1px solid var(--line); }
.cover table.meta td.k {
    width: 30mm; font-size: 7.5pt; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: var(--muted); padding-top: 11px;
}

/* ── Table of contents ── */
#toc { break-after: page; }
.toc-head { font-size: 23pt; font-weight: 700; letter-spacing: -.3px; border-bottom: 2.5px solid var(--blue); padding-bottom: 8px; margin: 0 0 14px 0; }
.toc-intro { font-size: 9pt; color: var(--muted); max-width: 150mm; margin-bottom: 20px; }
.toc-row { display: flex; align-items: baseline; gap: 6px; color: var(--ink); break-inside: avoid; }
.toc-row .t { flex: 0 1 auto; }
.toc-row .dots { flex: 1 1 24px; min-width: 24px; border-bottom: 1.5px dotted #9aa5b5; transform: translateY(-3px); }
.toc-row .n { flex: 0 0 auto; font-variant-numeric: tabular-nums; }
.toc-row.l1 { font-weight: 700; color: var(--blue); margin-top: 11px; font-size: 10.5pt; }
.toc-row.l2 { font-size: 9.5pt; margin-left: 14px; padding: 1px 0; }
.toc-row.l3 { font-size: 9pt; margin-left: 30px; color: var(--muted); }

/* ── Headings (each heading sits in a .hrow so the back-link stays outside
   the <h*> element and does not pollute the PDF bookmark text) ── */
.hrow { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; break-after: avoid; }
.hrow .back { font-size: 7.5pt; color: #8a94a6; white-space: nowrap; }
.h1-row { break-before: page; border-bottom: 2.5px solid var(--blue); padding-bottom: 8px; margin: 0 0 16px 0; }
h1 { font-size: 23pt; line-height: 1.2; font-weight: 700; letter-spacing: -.3px; margin: 0; }
.h2-row { border-top: 1px solid var(--line); padding-top: 14px; margin: 28px 0 10px 0; }
h2 { font-size: 15pt; line-height: 1.3; font-weight: 700; color: var(--navy); margin: 0; }
.h3-row { margin: 20px 0 6px 0; }
h3 { font-size: 11.5pt; font-weight: 700; color: var(--blue); margin: 0; }
h4, h5, h6 { break-after: avoid; margin: 16px 0 4px 0; font-size: 10.2pt; font-weight: 700; }
h5, h6 { color: var(--muted); }

/* ── Tables ── */
table { border-collapse: collapse; width: 100%; margin: 10px 0 16px 0; font-size: 9pt; line-height: 1.45; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
th { background: var(--head); color: var(--navy); text-align: left; font-weight: 700; padding: 7px 9px; border: 1px solid var(--line); }
td { padding: 7px 9px; border: 1px solid var(--line); vertical-align: top; overflow-wrap: break-word; }
tbody tr:nth-child(even) td { background: var(--zebra); }

/* ── Code ── */
code {
    font-family: 'Cascadia Mono',Consolas,'Courier New',monospace; font-size: .88em;
    background: #eef1f6; padding: 1px 5px; border-radius: 3px; overflow-wrap: anywhere;
}
pre, .codehilite {
    background: #f3f5f8 !important; border: 1px solid #e1e6ee; border-radius: 6px;
    padding: 10px 12px; margin: 10px 0 14px 0; font-size: 8.6pt; line-height: 1.5;
}
.codehilite pre { border: none; padding: 0; margin: 0; background: none !important; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { background: none; padding: 0; font-size: inherit; }

/* ── Quotes ── */
blockquote {
    background: #eaf1fa; border-left: 4px solid var(--blue); border-radius: 0 4px 4px 0;
    margin: 12px 0; padding: 10px 18px; break-inside: avoid;
}
blockquote p:last-child { margin-bottom: 0; }
"""


def _slug(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text) or 'section'


def prepare_headings(body_html):
    """Wraps every heading in a '.hrow' div with a unique id and (for levels
    1-3) an "Indice" back-link, and returns the heading list.

    Args:
        body_html (str): HTML from the markdown converter.

    Returns:
        tuple[str, list[dict]]: the rewritten HTML, and one dict per heading
        (level, inner html, anchor id), in document order, all levels.
    """
    used = {}
    entries = []

    def repl(match):
        level = int(match.group(1))
        inner = match.group(2)
        plain = html.unescape(re.sub(r'<[^>]+>', '', inner))
        base = _slug(plain)
        seen = used.get(base, 0)
        used[base] = seen + 1
        anchor = base if seen == 0 else f"{base}-{seen}"
        entries.append({'level': level, 'html': inner, 'id': anchor, 'plain': ' '.join(plain.split())})
        back = f'<a class="back" href="#toc">{BACK_LABEL}</a>' if level <= BACK_MAX_LEVEL else ''
        return (f'<div class="hrow h{level}-row"><h{level} id="{anchor}">{inner}</h{level}>'
                f'{back}</div>')

    return _HEADING_RE.sub(repl, body_html), entries


def _italian_date(day):
    return f"{day.day} {_MESI[day.month - 1]} {day.year}"


def build_document(body_html, entries, title, subtitle, meta, eyebrow,
                   source_name, pages=None):
    """Assembles the full HTML document (cover, TOC, body).

    Args:
        body_html (str): body already processed by prepare_headings().
        entries (list[dict]): heading list from prepare_headings().
        title (str | None): document title; the cover is skipped without it.
        subtitle (str | None): shown under the title.
        meta (dict[str, str]): extra front-matter fields, one row each in the
            cover's metadata table (key upper-cased as the label).
        eyebrow (str | None): small blue label above the title.
        source_name (str | None): source file name; adds the "PDF" row.
        pages (list[int] | None): absolute page of every entry (same order
            and length as entries). None renders placeholder numbers.

    Returns:
        str: the HTML document.
    """
    cover = ''
    if title:
        rows = [(k.replace('_', ' ').replace('-', ' '), v) for k, v in meta.items()]
        if source_name:
            rows.append(('PDF', f"Generato il {_italian_date(datetime.date.today())} "
                                f"dal file {source_name}"))
        meta_html = ''.join(
            f'<tr><td class="k">{html.escape(k)}</td><td>{html.escape(v)}</td></tr>'
            for k, v in rows
        )
        cover = (
            '<section class="cover">'
            + (f'<div class="eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else '')
            + f'<div class="title">{html.escape(title)}</div>'
            + (f'<div class="subtitle">{html.escape(subtitle)}</div>' if subtitle else '')
            + (f'<table class="meta">{meta_html}</table>' if rows else '')
            + '</section>'
        )

    toc = ''
    if any(e['level'] <= TOC_MAX_LEVEL for e in entries):
        rows = []
        for idx, e in enumerate(entries):
            if e['level'] > TOC_MAX_LEVEL:
                continue
            number = pages[idx] if pages else '00'
            rows.append(
                f'<a class="toc-row l{e["level"]}" href="#{e["id"]}">'
                f'<span class="t">{e["html"]}</span><span class="dots"></span>'
                f'<span class="n">{number}</span></a>'
            )
        toc = (f'<section id="toc"><div class="toc-head">{TOC_TITLE}</div>'
               f'<p class="toc-intro">{TOC_INTRO}</p>{"".join(rows)}</section>')

    return (
        '<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8">'
        f'<title>{html.escape(title or "Documento")}</title>'
        f'<style>{CSS}</style></head><body>{cover}{toc}{body_html}</body></html>'
    )


def _footer_template(left_text):
    return (
        '<div style="width:100%;margin:0 20mm;font-family:Segoe UI,Arial,sans-serif;'
        'font-size:8px;color:#6b7280;display:flex;justify-content:space-between;">'
        f'<span>{html.escape(left_text)}</span>'
        '<span>pagina <span class="pageNumber"></span> di '
        '<span class="totalPages"></span></span></div>'
    )


def _heading_pages(pdf_bytes):
    """Reads the PDF outline and returns the 1-based page of every heading,
    in document order (all levels), or None if it cannot be read."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []

    def walk(items):
        for item in items:
            if isinstance(item, list):
                walk(item)
            else:
                pages.append(reader.get_destination_page_number(item) + 1)

    walk(reader.outline)
    return pages


def _rebuild_outline(pdf_bytes, entries, pages):
    """Replaces Chromium's bookmarks with ones built from the real heading
    texts. Chromium sometimes duplicates the text of a heading that follows a
    forced page break ("DueDue"); no CSS cause was isolatable (removing any
    one of three unrelated rules made it vanish), so the bookmarks are
    rebuilt deterministically instead, keeping the page numbers it found.
    """
    writer = PdfWriter(clone_from=PdfReader(io.BytesIO(pdf_bytes)))
    writer._root_object.pop('/Outlines', None)
    stack = []  # (level, outline item) of the open ancestors
    for entry, page_number in zip(entries, pages):
        while stack and stack[-1][0] >= entry['level']:
            stack.pop()
        parent = stack[-1][1] if stack else None
        item = writer.add_outline_item(entry['plain'], page_number - 1, parent=parent)
        stack.append((entry['level'], item))
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def _launch(playwright):
    last_error = None
    for channel in CHROME_CHANNELS:
        try:
            return playwright.chromium.launch(channel=channel)
        except Exception as exc:  # channel not installed
            last_error = exc
    raise RuntimeError(f"Né Chrome né Edge risultano avviabili ({last_error})")


def render_pdf(body_html, output_path, title=None, subtitle=None, meta=None,
               eyebrow=None, source_name=None, footer_left=None):
    """Renders the Markdown-derived HTML to a professional PDF.

    Args:
        body_html (str): HTML from the markdown converter (no TOC, no title).
        output_path (Path | str): where to write the PDF.
        title, subtitle, eyebrow (str | None): cover texts.
        meta (dict[str, str] | None): extra cover metadata rows.
        source_name (str | None): source file name for the "PDF" cover row.
        footer_left (str | None): left footer text (default: the title).

    Returns:
        bool: True on success, False if the file could not be written.

    Raises:
        RuntimeError: if neither Chrome nor Edge can be launched.
    """
    body, entries = prepare_headings(body_html)

    def doc(pages=None):
        return build_document(body, entries, title, subtitle, meta or {},
                              eyebrow, source_name, pages)

    pdf_kwargs = dict(
        format="A4", print_background=True, display_header_footer=True,
        header_template='<span></span>',
        footer_template=_footer_template(footer_left or title or ''),
        margin={'top': '18mm', 'bottom': '20mm', 'left': '20mm', 'right': '20mm'},
        outline=True, tagged=True,  # Chromium builds bookmarks only for tagged PDFs
    )

    with sync_playwright() as p:
        browser = _launch(p)
        try:
            page = browser.new_page()
            page.set_content(doc(), wait_until='load')
            first = page.pdf(**pdf_kwargs)
            pages = _heading_pages(first)
            if len(pages) == len(entries):
                page.set_content(doc(pages), wait_until='load')
                final = _rebuild_outline(page.pdf(**pdf_kwargs), entries, pages)
            else:
                print(f"Attenzione: segnalibri ({len(pages)}) diversi dai titoli "
                      f"({len(entries)}), numeri di pagina del sommario omessi.")
                page.set_content(doc([''] * len(entries)), wait_until='load')
                final = page.pdf(**pdf_kwargs)
        finally:
            browser.close()

    try:
        Path(output_path).write_bytes(final)
    except PermissionError as exc:
        print(f"Impossibile scrivere su {Path(output_path).name}: {exc}")
        return False
    return True
