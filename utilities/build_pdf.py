#!/usr/bin/env python3
"""
Converts a markdown file into a paginated HTML page and PDF (with a
clickable index and bookmarks).

On startup it asks: whether to delete old .html/.pdf files already
present in the input's folder, and whether to use a different name
than the default for the generated .html/.pdf files. If the chosen
output files already exist, it asks for confirmation before
overwriting them.

Libraries used:
    - markdown: converts Markdown text to HTML (with table/list/<br> support)
    - xhtml2pdf.pisa: converts HTML string to A4 PDF with page break management

Usage:  python3 build_pdf.py text_to_convert.md
"""
import sys, re, unicodedata
from pathlib import Path
import markdown  # Converts Markdown -> HTML (tables, lists, newline-><br>)
from xhtml2pdf import pisa  # Converts HTML string -> PDF file

# Absolute path to the folder this script lives in (utilities/).
# We use this so the script always looks for its input file next to
# itself, no matter what directory it was launched from.
SCRIPT_DIR = Path(__file__).resolve().parent

# Read the input file name from the command line, e.g.:
#   python build_pdf.py my_document.md
# If the user doesn't pass one, fall back to a default file name.
arg = sys.argv[1] if len(sys.argv) > 1 else 'text_to_convert.md'
src = Path(arg)
if not src.is_absolute():
    # If the user gave a relative name/path, resolve it against
    # SCRIPT_DIR instead of the current working directory.
    src = SCRIPT_DIR / src

# Ask whether to clear out old output files before starting. Default is
# "no" (just pressing Enter) since deleting files is not something we
# want to do by accident.
cleanup_answer = input("Vuoi cancellare i vecchi file .html e .pdf nella cartella? (Y/N) [N]: ").strip().lower()
if cleanup_answer == 'y':
    old_files = list(src.parent.glob('*.html')) + list(src.parent.glob('*.pdf'))
    deleted, skipped = 0, []
    for old_file in old_files:
        try:
            old_file.unlink()
            deleted += 1
        except PermissionError:
            # Likely open in another program (a viewer, a browser, ...);
            # skip it instead of crashing the whole script.
            skipped.append(old_file.name)
    print(f"Cancellati {deleted} file." if deleted else "Nessun file .html/.pdf cancellato.")
    if skipped:
        print(f"Non cancellabili (probabilmente aperti altrove): {', '.join(skipped)}")

# "stem" is the input path without its extension, e.g. ".../report".
# We reuse it as the default base name for the output files: report.html,
# report.pdf. The user can type a different base name (no extension) or
# just press Enter to keep this default.
default_stem = src.with_suffix('').name
name_answer = input(f"Nome dei file di output [default: {default_stem}]: ").strip()
stem = str(src.parent / name_answer) if name_answer else str(src.with_suffix(''))
html_path = Path(f'{stem}.html')
pdf_path = Path(f'{stem}.pdf')

# If either output file already exists, ask before overwriting it so we
# don't silently destroy a previous version of the document.
existing = [p.name for p in (html_path, pdf_path) if p.exists()]
if existing:
    answer = input(f"I file {', '.join(existing)} esistono gia'. Sovrascrivere? (Y/N): ").strip().lower()
    if answer != 'y':
        sys.exit("Ok lasciamo i file cosi' come sono.")

# Load the raw Markdown text and convert it to an HTML string.
# The extensions add support for tables, plain "-"/"*" lists, and
# turning single newlines into <br> tags.
md_text = open(src, encoding='utf-8').read()
body = markdown.markdown(md_text, extensions=['tables', 'sane_lists', 'nl2br'])

# ── Helper: normalize a heading/index-entry string for comparison ──
# We need this because the same section title can appear slightly
# differently in the index list and in the actual <h2> heading
# (different capitalization, accented letters, extra notes, etc.).
# This function strips HTML tags, removes accents, drops a
# "(nuova in vX.Y)" suffix, lowercases everything and keeps only
# letters/digits, so two "equivalent" titles become identical strings
# we can safely compare/use as dictionary keys.
def norm(s):
    s = re.sub(r'<[^>]+>', '', s)                       # remove HTML tags
    s = unicodedata.normalize('NFKD', s)                 # split accented chars into base + accent
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))  # drop the accent marks
    s = re.sub(r'\(nuova in v[\d.]+\)', '', s, flags=re.I)        # drop "(nuova in vX.Y)" notes
    s = re.sub(r'[^a-z0-9]+', '', s.lower())             # keep only lowercase letters/digits
    return s

# ── Step 1: give every <h2> section heading a unique HTML id ──
# We'll need these ids later so the index (table of contents) can link
# directly to each section with an anchor like <a href="#sec0">.
headings = {}  # maps normalized heading text -> generated id (e.g. "sec0")

def add_id(m):
    inner = m.group(1)               # the heading text captured by the regex
    hid = f"sec{len(headings)}"      # next id: sec0, sec1, sec2, ...
    headings[norm(inner)] = hid
    return f'<h2 id="{hid}">{inner}</h2>'

# re.sub scans the HTML body for every <h2>...</h2> and replaces it
# using add_id(), which both records the heading and rewrites it with an id.
body = re.sub(r'<h2>(.*?)</h2>', add_id, body, flags=re.DOTALL)

# ── Step 2: turn the "INDICE" (table of contents) list items into clickable links ──
# The Markdown source is expected to contain a "## INDICE" section
# followed by a bullet list whose items repeat the section titles.
# Here we find that section and rewrite each <li> into a link pointing
# to the matching <h2 id="..."> we created above.
idx_id = headings.get(norm('INDICE'))
if idx_id:
    # Locate the INDICE heading, then the <ul>...</ul> list right after it.
    start = body.find(f'<h2 id="{idx_id}">')
    ul_s = body.find('<ul>', start)
    ul_e = body.find('</ul>', ul_s) + 5
    block = body[ul_s:ul_e]

    def linkify(m):
        inner = m.group(1)                 # text of the <li> entry
        hid = headings.get(norm(inner))    # matching section id, if any
        # If we found a matching heading, wrap the text in a link to it;
        # otherwise leave the original <li> untouched.
        return f'<li><a class="toc" href="#{hid}">{inner}</a></li>' if hid else m.group(0)

    block = re.sub(r'<li>(.*?)</li>', linkify, block, flags=re.DOTALL)
    # Replace the plain <ul> list with a <nav> block containing the linked version.
    body = body[:ul_s] + f'<nav class="toc-list">{block}</nav>' + body[ul_e:]

# ── Step 3: avoid a chapter heading landing right after a split table ──
# xhtml2pdf does not reliably honor "page-break-inside: avoid" for
# <table>: if a table doesn't fully fit in whatever space is left on the
# page, it can print just the header row, leave a large blank gap, and
# continue the body rows on the next page instead of moving the whole
# table down. A long table can also simply be taller than one page and
# spill onto the next regardless. Either way, if the *next* chapter
# heading lands right after such a table, it ends up stacked awkwardly
# close to the table's tail. So: whenever a <h2> is immediately preceded
# by a table with more rows than this threshold, we tag that <h2> to
# force it onto its own fresh page.
# This is a heuristic (we can't ask xhtml2pdf where it actually broke
# the page), tuned from testing so tables under the threshold reliably
# fit on a single page and don't need the extra break.
LONG_TABLE_ROW_THRESHOLD = 12

def force_break_before_long_tables(m):
    table_html, h2_tag = m.group(1), m.group(2)
    row_count = table_html.count('<tr>')
    if row_count > LONG_TABLE_ROW_THRESHOLD:
        h2_tag = h2_tag.replace('<h2 ', '<h2 class="force-break" ', 1)
    return table_html + h2_tag

body = re.sub(r'(<table.*?</table>)\s*(<h2 id="sec\d+">)', force_break_before_long_tables,
              body, flags=re.DOTALL)

# ── Step 3b: start the whole chapter on a fresh page when its table is
# near the top ──
# We used to just force a page break directly before every <table>, but
# that only moved the ugly gap: the chapter heading and its short intro
# text would end a page with a big trailing blank area before the table
# jumped to the next page. Better fix: if a chapter's table shows up
# shortly after its heading (i.e. before much other content), push the
# *heading* itself onto a fresh page instead, so the heading, its short
# intro and the table all land together with room to spare and no gap
# on either side.
#
# We process each chapter as its own isolated text slice (split on the
# <h2 id="secN"> boundaries) rather than a single regex over the whole
# body: a regex spanning "from one heading to the next table" has no
# clean way to fail fast when a chapter has no table of its own, and can
# end up pairing a later chapter's table with the wrong (table-less)
# heading.
NEAR_START_CHARS = 400  # how much intro HTML is still "close to the top"

heading_starts = [m.start() for m in re.finditer(r'<h2 id="sec\d+">', body)]
if heading_starts:
    chapters = []
    for i, start in enumerate(heading_starts):
        end = heading_starts[i + 1] if i + 1 < len(heading_starts) else len(body)
        chapters.append(body[start:end])

    for i, chapter in enumerate(chapters):
        h2_close = chapter.find('</h2>') + len('</h2>')
        heading, rest = chapter[:h2_close], chapter[h2_close:]
        table_pos = rest.find('<table')
        if 0 <= table_pos <= NEAR_START_CHARS and 'class="force-break"' not in heading:
            heading = heading.replace('<h2 ', '<h2 class="force-break" ', 1)
        chapters[i] = heading + rest

    body = body[:heading_starts[0]] + ''.join(chapters)

# ── Stylesheet used inside the generated HTML/PDF ──
# This is plain CSS embedded as a Python string. It controls page size,
# margins, fonts, colors and spacing for every HTML element that can
# appear in the converted document (headings, tables, quotes, code, etc).
CSS = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm; }
* { box-sizing: border-box; }
body { font-family: 'Lato','Segoe UI',Helvetica,Arial,sans-serif; font-size: 10pt;
       line-height: 1.55; color: #2b2b2b; margin: 0; }
h1 { font-size: 20pt; color: #1e3c72; margin: 0 0 4px 0; letter-spacing: .3px; }
h2 { font-size: 12.5pt; color: #1e3c72; margin: 22px 0 8px 0; padding-bottom: 4px;
     border-bottom: 2px solid #1e3c72; page-break-after: avoid; }
/* Forces a fresh page only for the specific chapters flagged by the
   table-related heuristics above (a long table right before this
   chapter, or this chapter's own table sitting close to its heading). */
h2.force-break { page-break-before: always; }
h3 { font-size: 10.8pt; color: #2a5298; margin: 15px 0 5px 0; page-break-after: avoid; }
h4 { font-size: 10pt; color: #444; margin: 12px 0 4px 0; page-break-after: avoid; }
h5 { font-size: 9.6pt; color: #555; margin: 10px 0 3px 0; font-style: italic; page-break-after: avoid; }
p { margin: 0 0 7px 0; }
ul, ol { margin: 4px 0 8px 0; padding-left: 20px; }
li { margin-bottom: 3px; }
strong { color: #1e3c72; }
/* xhtml2pdf does not reliably honor this for <table>: a table that
   doesn't fully fit in whatever space is left on the page can still get
   its header row stranded with a blank gap below it. We compensate for
   that in the Python code above by pushing the whole chapter (heading +
   table) onto a fresh page whenever the table sits close to the top. */
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px 0; font-size: 9pt;
        page-break-inside: avoid; }
th { background: #eef3fb; color: #1e3c72; text-align: left; padding: 5px 7px;
     border: 1px solid #cdd9ec; font-weight: 700; }
td { padding: 5px 7px; border: 1px solid #dde5f0; vertical-align: top; }
blockquote { margin: 6px 0 10px 0; padding: 7px 12px; background: #f5f7fa;
             border-left: 3px solid #1e3c72; font-size: 9.4pt; page-break-inside: avoid; }
blockquote p { margin: 0; }
code { background: #f0f2f5; padding: 1px 4px; border-radius: 3px;
       font-family: 'Consolas','Courier New',monospace; font-size: 9pt; }
pre { background: #f5f7fa; border-left: 3px solid #8fa8cf; padding: 8px 11px;
      margin: 6px 0 10px 0; page-break-inside: avoid; overflow-wrap: break-word; }
pre code { background: none; padding: 0; font-size: 8.8pt; line-height: 1.45; }
hr { border: none; border-top: 1px solid #e2e2e2; margin: 14px 0; }
em { color: #555; }

/* ── Styling for the clickable table of contents (see Step 2 above) ── */
.toc-list ul { list-style: none; padding-left: 0; margin: 6px 0 4px 0; }
.toc-list li { margin-bottom: 5px; }
a.toc { color: #1e3c72; text-decoration: none; font-weight: 600; font-size: 10pt;
        border-bottom: 1px dotted #b6c6e0; padding-bottom: 1px; }
a { color: #1e3c72; }
"""

# Assemble the final HTML document: doctype, head (title + CSS) and the
# converted Markdown body we built above.
doc = f"""<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8">
<title>Strategia Operativa di Ricerca Lavoro</title>
<style>{CSS}</style></head><body>
{body}
</body></html>"""

# Save the HTML version to disk (useful for previewing in a browser).
html_path.write_text(doc, encoding='utf-8')

# Convert the same HTML string to a PDF file using xhtml2pdf.
# pisa.CreatePDF reads the HTML and writes the rendered PDF bytes
# straight into the open file handle.
try:
    with open(pdf_path, 'wb') as pdf_file:
        result = pisa.CreatePDF(doc, dest=pdf_file, encoding='utf-8')
except PermissionError:
    # On Windows this almost always means the PDF is currently open in
    # another program (a viewer, a browser, ...) that is locking the file.
    sys.exit(f"Impossibile scrivere {pdf_path.name}: chiudi il file se e' aperto in un altro programma e riprova.")

# result.err is non-zero if xhtml2pdf hit rendering errors; stop here
# instead of silently producing a broken/incomplete PDF.
if result.err:
    sys.exit(f"Errore nella generazione del PDF ({result.err} problemi)")

print(f"OK: {html_path.name} e {pdf_path.name}  |  voci indice collegate: {sum(1 for h in headings)}")
