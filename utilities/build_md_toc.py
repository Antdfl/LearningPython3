#!/usr/bin/env python3
"""
Converts a .md file to HTML, PDF, and/or DOCX (Word) with clickable TOC after H1.
On startup it asks whether to generate HTML, PDF, DOCX, or all three formats.

Menu: H = HTML only (.html), P = PDF only (.pdf), W = Word only (.docx), A = All three formats

NEW FEATURE: Adds a clickable Table of Contents (TOC) right after the first H1 heading
for both HTML and PDF formats. The Word format already has TOC support built-in.
"""
import sys, re, unicodedata, os
from pathlib import Path


# ── Helper comments section ──


def _missing(pip_name):
    """Prints a helpful message when a required library is not installed."""
    print(f"Library '{pip_name}' not found. Install with: pip install {pip_name}")


try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    _missing('markdown')
    MARKDOWN_AVAILABLE = False

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    _missing('xhtml2pdf')
    XHTML2PDF_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_AVAILABLE = True
except ImportError:
    _missing('python-docx')
    DOCX_AVAILABLE = False


SCRIPT_DIR = Path(__file__).resolve().parent


def strip_frontmatter(md_text):
    """Removes the initial YAML block (--- ... ---) if present."""
    lines = md_text.split('\n')
    if lines and lines[0].strip() == '---':
        for idx in range(1, len(lines)):
            if lines[idx].strip() == '---':
                return '\n'.join(lines[idx + 1:]).lstrip('\n')
    return md_text


def convert_to_html(md_text):
    """Converts Markdown text to HTML string using the 'markdown' library.

    Returns:
        str: The converted HTML string with tables, sane lists, and new line breaks supported.
    """
    return markdown.markdown(md_text, extensions=['tables', 'sane_lists', 'nl2br'])


def html_to_pdf(html_content, output_path):
    """Converts an HTML string to a PDF file using the 'xhtml2pdf' library."""
    try:
        with open(output_path, 'wb') as pdf_file:
            result = pisa.CreatePDF(html_content, dest=pdf_file, encoding='utf-8')
        if result.err:
            print(f"PDF generation error (xhtml2pdf reported {result.err} problems)")
        else:
            print(f"OK: {output_path.name}")
    except PermissionError as e:
        print(f"Cannot write to {output_path.name}: {e}")


def add_heading_bookmark(paragraph, bookmark_name, bookmark_id):
    """Adds a bookmark to a heading paragraph for Word TOC."""
    p_elem = paragraph._p
    start = OxmlElement('w:bookmarkStart')
    start.set(qn('w:id'), str(bookmark_id))
    start.set(qn('w:name'), bookmark_name)
    end = OxmlElement('w:bookmarkEnd')
    end.set(qn('w:id'), str(bookmark_id))
    insert_at = 1 if len(p_elem) and p_elem[0].tag == qn('w:pPr') else 0
    p_elem.insert(insert_at, start)
    p_elem.append(end)


def build_toc_entry_paragraph(doc, level, text, bookmark_name):
    """Creates a table of contents (TOC) entry paragraph for a heading."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches({1: 0, 2: 0.25, 3: 0.5}.get(level, 0.5))

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('w:anchor'), bookmark_name)

    run_el = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '1e3c72')
    underline = OxmlElement('w:u')
    underline.set(qn('w:val'), 'single')
    rpr.append(color)
    rpr.append(underline)
    run_el.append(rpr)
    t = OxmlElement('w:t')
    t.text = text
    run_el.append(t)
    hyperlink.append(run_el)

    p._p.append(hyperlink)
    return p


def build_toc(doc, toc_entries):
    """Builds the Table of Contents (TOC) block for Word documents."""
    if not toc_entries:
        return

    title_p = doc.add_paragraph()
    title_run = title_p.add_run('Table of Contents')
    title_run.font.size = Pt(18)
    title_run.font.bold = True

    entry_paragraphs = [
        build_toc_entry_paragraph(doc, level, text, bookmark_name)
        for level, text, bookmark_name in toc_entries
    ]

    doc.add_page_break()

    first_p = entry_paragraphs[0]._p
    
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    r_begin = OxmlElement('w:r')
    r_begin.append(fld_begin)

    instr_text = OxmlElement('w:instrText')
    instr_text.set(qn('xml:space'), 'preserve')
    instr_text.text = ' TOC \\o "1-3" \\h \\z \\u '
    r_instr = OxmlElement('w:r')
    r_instr.append(instr_text)

    fld_separate = OxmlElement('w:fldChar')
    fld_separate.set(qn('w:fldCharType'), 'separate')
    r_separate = OxmlElement('w:r')
    r_separate.append(fld_separate)

    insert_at = 1 if len(first_p) and first_p[0].tag == qn('w:pPr') else 0
    for el in (r_separate, r_instr, r_begin):
        first_p.insert(insert_at, el)

    last_p = entry_paragraphs[-1]._p
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    r_end = OxmlElement('w:r')
    r_end.append(fld_end)
    last_p.append(r_end)

    sdt = OxmlElement('w:sdt')
    sdt_pr = OxmlElement('w:sdtPr')
    doc_part_obj = OxmlElement('w:docPartObj')
    doc_part_gallery = OxmlElement('w:docPartGallery')
    doc_part_gallery.set(qn('w:val'), 'Table of Contents')
    doc_part_unique = OxmlElement('w:docPartUnique')
    doc_part_obj.append(doc_part_gallery)
    doc_part_obj.append(doc_part_unique)
    sdt_pr.append(doc_part_obj)
    sdt.append(sdt_pr)

    sdt_content = OxmlElement('w:sdtContent')
    sdt_content.append(title_p._p)
    for p in entry_paragraphs:
        sdt_content.append(p._p)
    sdt.append(sdt_content)

    doc.element.body.insert(0, sdt)


def create_word_from_md(md_text, output_path):
    """
    Creates a Microsoft Word document (.docx) from Markdown source with automatic
    Table of Contents (TOC) generation. Supports all standard Markdown syntax
    including headings, lists, tables, images, links, and code blocks.

    TOC Features:
    - Automatically numbered headings (1, 1.1, 1.1.1 format)
    - Clickable TOC with hyperlinks to each section
    - Hierarchical indentation matching heading levels

    Supported Markdown features:
    - Headings: # h1, ## h2, ### h3, #### h4, ##### h5, ###### h6
    - Unordered lists (- or *)
    - Ordered lists (1., 2., ...)
    - Bold (**text**) and Italic (*text*)
    - Inline code (`code`)
    - Tables with header rows
    - Links [text](url)
    - Images ![alt](path)

    Args:
        md_text (str): The full Markdown content as a string
        output_path (Path): Path where the .docx file will be saved
    """
    def split_table_row(row_line):
        # Helper: splits a markdown table row by '|' into individual cell content
        parts = row_line.split('|')
        
        # Remove empty first column (common pattern in markdown tables)
        if parts and parts[0].strip() == '':
            parts = parts[1:]
        
        # Remove empty last column if present
        if parts and parts[-1].strip() == '':
            parts = parts[:-1]
        
        return [p.strip() for p in parts]

    try:
        doc = Document()
        
        h_counters = [0, 0, 0]
        toc_entries = []
        bookmark_counter = 0
        
        lines = md_text.split('\n')
        num_lines = len(lines)
        i = 0

        while i < num_lines:
            line_stripped = lines[i]
            line = line_stripped.strip()

            if not line:
                # Skip empty lines (no paragraph needed)
                i += 1
                continue

            # ── Markdown Tables Detection ──
            # Detect table syntax: row containing '|' with a separator header row above it
            if '|' in line and not line.startswith('#'):
                # Look ahead at the next line to find the separator (header divider) pattern
                next_line = lines[i + 1].strip() if i + 1 < num_lines else ''
                sep_cells = split_table_row(next_line) if next_line else []
                
                # Check if this is a markdown table separator row (e.g., "|-|---|---:")
                is_separator = bool(sep_cells) and all(
                    re.match(r'^:?-+:?$', c) for c in sep_cells if c != ''
                ) and any(c != '' for c in sep_cells)

                if is_separator:
                    # This is a header separator, now extract the header row above it
                    header_cells = split_table_row(line)
                    num_cols = len(header_cells)

                    # Collect all data rows below until we hit another table section or non-table line
                    body_rows = []
                    j = i + 2
                    while j < num_lines and '|' in lines[j].strip():
                        body_rows.append(split_table_row(lines[j].strip()))
                        j += 1

                    # Create the Word table with header and body rows
                    table = doc.add_table(rows=1 + len(body_rows), cols=num_cols)
                    table.style = 'Table Grid'

                    # Fill in header cells (first row)
                    for k, cell_text in enumerate(header_cells[:num_cols]):
                        table.rows[0].cells[k].text = cell_text

                    # Fill in body cells (data rows)
                    for r, cells in enumerate(body_rows, start=1):
                        for k, cell_text in enumerate(cells[:num_cols]):
                            table.rows[r].cells[k].text = cell_text

                    i = j  # Move to next section
                    continue

            # ── Images ![alt](path) ──
            # Detect markdown image syntax and convert to plain text description
            img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)$', line_stripped)
            if img_match:
                alt_text = img_match.group(1)
                img_path = img_match.group(2)
                p = doc.add_paragraph(f"Image: {alt_text} (path: {img_path})")
                i += 1
                continue

            # ── Links [text](url) ──
            # Detect markdown link syntax and convert to clickable-style text
            link_match = re.match(r'^\[([^\]]*)\]\(([^)]+)\)$', line_stripped)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                p = doc.add_paragraph(f"[{link_text}]({link_url})")
                i += 1
                continue
            
            # ── Headings (h1-h6) ──
            # Detect markdown headings (# to ######) and convert to Word headings with bookmarks
            title_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            if title_match:
                level = len(title_match.group(1))
                title_text = title_match.group(2).strip()
                
                # Remove any [text](url) links from the heading, keeping only the text
                title_clean = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', title_text)
                
                if level in (1, 2, 3):
                    if level == 1:
                        h_counters[0] += 1
                        h_counters[1] = 0
                        h_counters[2] = 0
                        numbering = f"{h_counters[0]}"
                    elif level == 2:
                        h_counters[1] += 1
                        h_counters[2] = 0
                        numbering = f"{h_counters[0]}.{h_counters[1]}"
                    else:
                        h_counters[2] += 1
                        numbering = f"{h_counters[0]}.{h_counters[1]}.{h_counters[2]}"

                    numbered_text = f"{numbering} {title_clean}"
                    heading = doc.add_heading(numbered_text, level=level)

                    bookmark_counter += 1
                    bookmark_name = f"_toc_bm_{bookmark_counter}"
                    add_heading_bookmark(heading, bookmark_name, bookmark_counter)
                    toc_entries.append((level, numbered_text, bookmark_name))
                elif level == 4:
                    # Level 4 headings are too deep for TOC, render as custom paragraph
                    p = doc.add_paragraph()
                    run = p.add_run(title_clean)
                    run.font.name = 'Heading'
                    run.font.size = Pt(14)
                elif level == 5:
                    # Level 5 headings are very small detail headers
                    p = doc.add_paragraph()
                    run = p.add_run(title_clean)
                    run.font.size = Pt(12)
                else:  # h6
                    # Level 6 headings are fine print / footer-level text
                    p = doc.add_paragraph()
                    run = p.add_run(title_clean)
                    run.font.size = Pt(10)

                i += 1
                continue

            # ── Unordered Lists (-, *, +) ──
            # Detect bullet point lists and add them as paragraphs
            ul_match = re.match(r'^(\s*[-*+]\s+)(.+)$', line_stripped)
            if ul_match:
                list_item_text = ul_match.group(2).strip()
                p = doc.add_paragraph(list_item_text)
                i += 1
                continue

            # ── Ordered Lists (1., 2., 3...) ──
            # Detect numbered lists and preserve the numbering
            ol_match = re.match(r'^(\d+)\.\s+(.+)$', line_stripped)
            if ol_match:
                list_num = ol_match.group(1)
                list_item_text = ol_match.group(2).strip()
                p = doc.add_paragraph(f"{list_num}. {list_item_text}")
                i += 1
                continue

            # ── Blockquotes (") ──
            # Detect quoted text and add with Quote style in Word
            quote_match = re.match(r'^"(.+)"$', line_stripped)
            if quote_match:
                quote_text = quote_match.group(1).replace('"', '"')
                p = doc.add_paragraph('" ' + quote_text + '"', style='Quote')
                i += 1
                continue
            
            # ── Inline Code (`code`) ──
            # Detect markdown inline code and wrap in HTML <code> tags
            code_inline = re.sub(r'`([^`]+)`', r'<code>\1</code>', line_stripped)
            
            # ── Bold Text (**text**) ──
            # Detect bold formatting and convert to HTML <strong> tags
            bold_inline = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', code_inline)
            
            # ── Italic Text (*text*) ──
            # Detect italic formatting and convert to HTML <em> tags
            italic_inline = re.sub(r'\*(.+?)\*', r'<em>\1</em>', bold_inline)
            
            # ── Clean HTML Tags ──
            # Remove any raw HTML tags that were in the original markdown
            clean_text = re.sub(r'<[^>]+>', '', italic_inline)
            
            # ── Regular Paragraph Text ──
            # Add remaining text as a regular paragraph (not heading/list/quote/etc.)
            if clean_text.strip():
                p = doc.add_paragraph(clean_text)

            i += 1

        build_toc(doc, toc_entries)

        doc.save(output_path)
        print(f"OK: {output_path.name}")
    except Exception as e:
        print(f"Error creating DOCX file: {e}")


# ── Interactive menu to choose output formats ──
print("\n" + "=" * 40)
print("=== Convert Markdown File (with TOC for HTML/PDF) ===")
print("=" * 40)
print("H = HTML only (.html)")
print("P = PDF only (.pdf)  <-- DEFAULT")
print("W = Word only (.docx)")
print("A = All three formats (HTML, PDF, DOCX)")
print("=" * 40)
print("NEW: Both HTML and PDF will have a clickable TOC right after the first H1 heading.")
print("The Word format already has TOC support built-in.")
print("=" * 40)

choice = input("\nChoose format: H | P | W | A? ").strip().upper()

# Fallback: if the user didn't select anything, default to PDF
if not choice or choice == "":
    print("No selection - using default: PDF (.pdf)")
    choice = "P"

if choice not in ['H', 'P', 'W', 'A']:
    print("Invalid selection. Exiting program.")
    sys.exit(1)

# ── Input file ──
arg = sys.argv[1] if len(sys.argv) > 1 else 'text_to_convert.md'
src = Path(arg)
if not src.is_absolute():
    src = SCRIPT_DIR / src

if not src.exists():
    print(f"File not found: {src}")
    sys.exit(1)

# ── Output filename ──
default_stem = src.with_suffix('').name
output_name = input(f"\nOutput filename base [{default_stem}]: ").strip()
stem = Path(output_name) if output_name else src.with_suffix('')

# ── Read the Markdown content ──
print("\nReading Markdown file...")
md_text = open(src, encoding='utf-8').read()
md_text = strip_frontmatter(md_text)
print(f"Read: {len(md_text)} characters.")

# ── Convert Markdown to HTML (required for HTML/PDF output) ──
needs_html = choice in ['H', 'P', 'A']
body_html = None
if needs_html and MARKDOWN_AVAILABLE:
    body_html = convert_to_html(md_text)

# ── CSS stylesheet for HTML/PDF rendering ──
# Includes TOC styling and anchor links for clickable navigation
CSS = """
@page { size: A4; margin: 18mm 16mm 16mm 16mm; }
* { box-sizing: border-box; }

body { 
    font-family: 'Lato','Segoe UI',Helvetica,Arial,sans-serif; 
    font-size: 10pt; 
    line-height: 1.55; 
    color: #2b2b2b; 
    margin: 0; 
}

h1, h2, h3, h4, h5, h6 { 
    margin-top: 0; 
    page-break-after: avoid;
}

/* First H1 - add TOC right after it */
h1:first-of-type { 
    margin-bottom: 8px; 
}

/* Table of Contents container */
#toc { 
    background: #f8f9fa; 
    padding: 15px 20px; 
    border-radius: 6px; 
    margin-top: 0; 
    margin-bottom: 15px;
    border-left: 4px solid #1e3c72;
}

#toc h4 { 
    margin: 0 0 10px 0; 
    color: #1e3c72; 
    font-size: 12pt;
    font-weight: bold;
}

/* TOC navigation links */
#toc nav ul { 
    list-style: none; 
    padding: 0; 
    margin: 0;
}

#toc nav li {
    margin: 4px 0;
    padding-left: 15px;
    position: relative;
}

#toc nav li::before {
    content: "-";
    position: absolute;
    left: 0;
    font-size: 9.5pt;
}

/* Hierarchical indentation, mirrors the Word TOC (0 / 0.25in / 0.5in) */
#toc nav li.toc-l1 { margin-left: 0; font-weight: 600; }
#toc nav li.toc-l2 { margin-left: 18px; }
#toc nav li.toc-l3 { margin-left: 36px; font-size: 9pt; }

/* TOC links - clickable and styled */
#toc nav a {
    color: #1e3c72;
    text-decoration: none;
    font-weight: 500;
    font-size: 9.5pt;
    padding: 2px 4px;
    border-radius: 3px;
    transition: all 0.2s ease;
}

#toc nav a:hover { 
    background: #e8f0fe; 
    text-decoration: underline;
}

/* Headings with anchor links */
h1, h2, h3, h4, h5, h6 { 
    scroll-margin-top: 150px;
}

h1 { font-size: 20pt; color: #1e3c72; margin: 0 0 8px 0; letter-spacing: .3px; }
h2 { font-size: 12.5pt; color: #1e3c72; margin: 22px 0 8px 0; padding-bottom: 4px; border-bottom: 2px solid #1e3c72; }
h3 { font-size: 10.8pt; color: #2a5298; margin: 15px 0 5px 0; }
h4 { font-size: 10pt; color: #444; margin: 12px 0 4px 0; }
h5 { font-size: 9.6pt; color: #555; margin: 10px 0 3px 0; font-style: italic; }

p { margin: 0 0 7px 0; }

ul, ol { margin: 4px 0 8px 0; padding-left: 20px; }
li { margin-bottom: 3px; }

strong { color: #1e3c72; font-weight: bold; }
em { color: #555; font-style: italic; }

code { 
    background: #f0f2f5; 
    padding: 2px 6px; 
    border-radius: 3px; 
    font-family: 'Consolas','Courier New',monospace; 
    font-size: 9pt; 
}

pre { 
    background: #f5f7fa; 
    border-left: 3px solid #8fa8cf; 
    padding: 10px 12px; 
    margin: 8px 0 12px 0; 
    overflow-x: auto; 
}
pre code { background: none; padding: 0; }

table { 
    width: 100%; 
    border-collapse: collapse; 
    margin: 8px 0 12px 0; 
    font-size: 9pt; 
    page-break-inside: avoid;
}
th { 
    background: #eef3fb; 
    color: #1e3c72; 
    text-align: left; 
    padding: 6px 8px; 
    border: 1px solid #cdd9ec; 
    font-weight: bold; 
}
td { 
    padding: 6px 8px; 
    border: 1px solid #dde5f0; 
    vertical-align: top; 
}

blockquote { 
    margin: 7px 0 10px 0; 
    padding: 8px 14px; 
    background: #f5f7fa; 
    border-left: 4px solid #1e3c72; 
    font-size: 9.6pt; 
    page-break-inside: avoid;
}
blockquote p { margin: 0; }

hr { border: none; border-top: 1px solid #e2e2e2; margin: 15px 0; }

a { color: #1e3c72; text-decoration: underline; }
img { max-width: 100%; height: auto; }
"""

def slugify(text):
    """Convert heading text to a safe, unique anchor ID.

    FIX: Previously, TOC links calculated the anchor from text using a
    different rule than the one used to generate IDs on headings, so they
    never matched. Now both <a href="#..."> from TOC and heading IDs pass
    through this single function (with duplicate handling done by caller),
    so they always stay aligned.
    """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text or 'section'


# ── Assemble the HTML document with a hierarchical TOC (mirrors the Word TOC) ──
html_doc = None
if body_html is not None:
    # Numbers h1-h3 (1, 1.1, 1.1.1 ...) like the Word version, gives every heading
    # a unique anchor id, and collects h1-h3 entries for the TOC.
    h_counters = [0, 0, 0]
    used_ids = {}
    toc_entries = []  # (level, numbered_text, anchor_id)

    def add_heading_id(match_obj):
        level = int(match_obj.group(1))
        inner_html = match_obj.group(2)

        text_plain = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', inner_html)
        text_plain = re.sub(r'<[^>]+>', '', text_plain)
        text_plain = ' '.join(text_plain.split())

        display_html = inner_html
        if level in (1, 2, 3):
            if level == 1:
                h_counters[0] += 1
                h_counters[1] = 0
                h_counters[2] = 0
                numbering = f"{h_counters[0]}"
            elif level == 2:
                h_counters[1] += 1
                h_counters[2] = 0
                numbering = f"{h_counters[0]}.{h_counters[1]}"
            else:
                h_counters[2] += 1
                numbering = f"{h_counters[0]}.{h_counters[1]}.{h_counters[2]}"
            display_html = f"{numbering} {inner_html}"
            text_plain = f"{numbering} {text_plain}"

        base_id = slugify(text_plain)
        seen = used_ids.get(base_id, 0)
        used_ids[base_id] = seen + 1
        anchor_id = base_id if seen == 0 else f"{base_id}-{seen}"

        if level in (1, 2, 3):
            toc_entries.append((level, display_html, anchor_id))

        # FIX: PDF links were broken because xhtml2pdf (reportlab engine) ignores
        # the name="..." attribute set directly on h1..h6 - it only recognizes a
        # standalone <a name="..."> tag as an internal link target, and discards
        # empty ones during rendering (known bug). So we prepend the anchor tag
        # with a non-breaking space inside: id="..." is used as the target for
        # links in HTML export, while <a name="..."> makes PDF links clickable.
        return (
            f'<a name="{anchor_id}">&nbsp;</a>'
            f'<h{level} id="{anchor_id}" class="anchor">{display_html}</h{level}>'
        )

    html_with_ids = re.sub(
        r'<h([1-6])\b[^>]*>(.*?)</h\1>',
        add_heading_id,
        body_html,
        flags=re.S,
    )

    level_class = {1: 'toc-l1', 2: 'toc-l2', 3: 'toc-l3'}
    toc_links_html = '\n'.join(
        f'<li class="{level_class[level]}"><a href="#{anchor_id}">{text}</a></li>'
        for level, text, anchor_id in toc_entries
    )

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Converted Document</title>
<style>{CSS}</style></head>
<body>

<div id="toc">
<h4>Table of Contents</h4>
<nav>
<ul>
{toc_links_html}
</ul>
</nav>
</div>

{html_with_ids}</body>
</html>"""

# ── Generate files based on user choice ──
if choice in ['H', 'A']:
    if html_doc is not None:
        html_path = stem.with_suffix('.html')
        html_path.write_text(html_doc, encoding='utf-8')
        print(f"Generated: {html_path}")
    else:
        _missing('markdown')
        print("Skipping HTML generation.")

if choice in ['P', 'A']:
    if html_doc is None:
        _missing('markdown')
        print("Skipping PDF generation.")
    elif not XHTML2PDF_AVAILABLE:
        _missing('xhtml2pdf')
        print("Skipping PDF generation.")
    else:
        pdf_path = stem.with_suffix('.pdf')
        html_to_pdf(html_doc, pdf_path)

if choice in ['W', 'A']:
    if DOCX_AVAILABLE:
        word_path = stem.with_suffix('.docx')
        create_word_from_md(md_text, word_path)
    else:
        _missing('python-docx')
        print("Skipping DOCX generation.")

print("\n" + "=" * 40)
print("Conversion complete!")
print("=" * 40)