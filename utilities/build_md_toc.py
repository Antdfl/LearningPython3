#!/usr/bin/env python3
"""
utilities/build_md_toc.py

# Purpose: This module provides utilities for converting Markdown (.md) files into multiple document 
# formats (HTML, PDF, DOCX). It is designed to handle complex features like automatic Table of Contents (TOC) generation.

# Audience Note for Junior Programmers:
# The conversion process involves several technical workarounds and external library dependencies 
# (markdown, xhtml2pdf, python-docx). Understanding the *why* behind these functions 
# (e.g., why table widths must be explicitly set in CSS/XML) is crucial for maintenance.

# Functionality Overview:
# - Markdown to HTML: Converts markdown syntax to structured, styled HTML.
# - TOC Generation (HTML/PDF): Dynamically finds H1-H3 headings, creates unique anchors, and builds a navigable TOC block placed after the first major heading.
# - DOCX Generation: Uses advanced python-docx XML manipulation to create a Word document that contains proper internal field codes for an automatic TOC when opened in MS Word.

# Conversion Menu:
# H = HTML only (.html)
# P = PDF only (.pdf): Requires xhtml2pdf and relies on the generated HTML structure.
# W = Word only (.docx): Uses advanced DOCX XML manipulation for full functionality.
# A = All three formats: Executes all supported conversions sequentially.

# Dependencies (MUST be installed via pip): 
# - markdown: Core Markdown parser.
# - xhtml2pdf: For PDF conversion from HTML.
# - python-docx: For Word document creation and XML manipulation.
"""
import sys, re, unicodedata, os
from pathlib import Path


# ── Helper comments section ──


def _missing(pip_name):
    """
    [Helper Function] Outputs an actionable warning message if a required third-party library 
    is not available in the current Python environment.

    Parameters:
        pip_name (str): The name of the missing library package.
    """
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
    """
    [Utility Function] Strips common YAML "Front Matter" blocks from the start of a Markdown file.

    Front matter is used in many static site generators (e.g., Jekyll, Hugo) to store 
    metadata like author, date, or version before the main content begins. It must be removed 
    before parsing the core markdown text.

    Parameters:
        md_text (str): The raw Markdown content string read from disk.

    Returns:
        str: The cleaned Markdown text with the front matter block completely removed.
    """
    lines = md_text.split('\n')
    # Check if the first line is the start delimiter '---'.
    if lines and lines[0].strip() == '---':
        for idx in range(1, len(lines)):
            # Found the closing delimiter '---'. Everything after this point is content.
            if lines[idx].strip() == '---':
                return '\n'.join(lines[idx + 1:]).lstrip('\n')
    # If no front matter structure was found, return the original text unchanged.
    return md_text


def strip_md_toc(md_text):
    """
    [Utility Function] Strips a hand-written Markdown Table of Contents (TOC) from the
    start of a document, so it does not duplicate the auto-generated TOC built later for
    HTML/PDF/DOCX output.

    Two TOC shapes are recognized, both searched for only near the top of the document
    (right after the title, so real content lists elsewhere are never touched):

    1. Heading-guarded: a heading like "## Contenuto" / "## Table of Contents" / "## Indice"
       followed by a list of anchor links (e.g. "[Link](#id)").
    2. Bare: a contiguous list of anchor links placed directly under the first H1 title,
       with no introducing heading at all (this is what tools like Pandoc/VS Code TOC
       extensions typically generate).

    A run of list items is only treated as a real TOC if the large majority of its items
    are anchor links, which avoids false positives on ordinary bullet lists.

    IMPORTANT: The first H1 heading (the document title) is never removed, only the TOC
    block that follows it.

    Parameters:
        md_text (str): The raw Markdown content string.

    Returns:
        str: The cleaned Markdown text with the TOC block removed, unchanged if none found.
    """
    lines = md_text.split('\n')

    if not lines:
        return md_text

    total = len(lines)
    # A hand-written TOC always sits near the very top of the document (right after the
    # title), so we only look there. This keeps ordinary content lists further down
    # (which may also happen to contain internal anchor links) untouched.
    search_limit = min(total, 400)

    # Heading text is anchored with \s*$ so a real title like "# Sommario del Progetto"
    # is never mistaken for a bare TOC heading like "# Sommario".
    heading_patterns = [
        r'^#\s*Contenuto\s*$',
        r'^#\s*Indice\s*$',
        r'^#\s*Table\s+of\s+Contents\s*$',
        r'^#\s*Sommario\s*$',
        r'^##\s*Contenuto\s*$',
        r'^##\s*Indice\s*$',
        r'^##\s*Table\s+of\s+Contents\s*$',
        r'^###\s*Contenuto\s*$',
    ]

    def is_list_item(s):
        return bool(re.match(r'^\s*[-*+]\s+', s))

    def is_anchor_list_item(s):
        return bool(re.match(r'^\s*[-*+]\s+.*\[.+?\]\(#.*?\)', s))

    # Locate the first H1 (document title); the TOC search starts right after it.
    title_idx = None
    for i in range(min(total, search_limit)):
        if re.match(r'^#\s+', lines[i].strip()):
            title_idx = i
            break

    scan_start = (title_idx + 1) if title_idx is not None else 0

    toc_start_idx = None
    toc_end_idx = None

    i = scan_start
    while i < search_limit:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        heading_line_idx = None
        if any(re.match(p, stripped) for p in heading_patterns):
            heading_line_idx = i
            j = i + 1
            while j < search_limit and not lines[j].strip():
                j += 1
            run_start = j
        elif is_anchor_list_item(stripped):
            run_start = i
        else:
            # First non-blank content after the title is neither a TOC heading nor a
            # TOC-like list item, so there is no hand-written TOC to strip.
            break

        # Collect the contiguous run of list items starting at run_start (a real blank
        # line ends the run - TOC entries are not blank-line separated).
        collected = []
        j = run_start
        while j < search_limit and is_list_item(lines[j].strip()):
            collected.append(j)
            j += 1

        if collected:
            anchor_count = sum(1 for k in collected if is_anchor_list_item(lines[k].strip()))
            if anchor_count / len(collected) >= 0.8:
                toc_start_idx = heading_line_idx if heading_line_idx is not None else collected[0]
                toc_end_idx = collected[-1]
        break

    if toc_start_idx is None or toc_end_idx is None:
        return md_text

    result_lines = lines[:toc_start_idx] + lines[toc_end_idx + 1:]
    return '\n'.join(result_lines)


def convert_to_html(md_text):
    """Converts Markdown text to HTML string using the 'markdown' library.

    Returns:
        str: The converted HTML string with tables, sane lists, and new line breaks supported.
    """
    return markdown.markdown(md_text, extensions=['tables', 'sane_lists', 'nl2br'])


# Printable width of the PDF page (A4 minus the left/right margins set in the
# @page CSS rule below: 210mm page width - 16mm - 16mm margins), converted to
# points. Used to give wide tables absolute (not percentage) column widths.
_MM_TO_PT = 72 / 25.4
PAGE_CONTENT_WIDTH_PT = (210 - 16 - 16) * _MM_TO_PT


def _cell_text_len(cell_html):
    """
    [Utility] Strips all HTML tags from a given cell's content and returns 
    the remaining plaintext length. This is used for calculating content-based column widths.

    Parameters:
        cell_html (str): The raw HTML string of the table cell.

    Returns:
        int: Length of the visible text content after stripping all tags.
    """
    # Regex Explanation: <[^>]+> matches any sequence starting with < and ending with > 
    # (i.e., a complete HTML tag). We substitute these matches with nothing ('') to strip them out.
    return len(re.sub(r'<[^>]+>', '', cell_html).strip())


def _longest_word_len(cell_html):
    """
    [Utility] Calculates the length of the longest continuous, unbreakable word within a table cell.

    Critical Limitation Workaround: The xhtml2pdf/ReportLab PDF engine only wraps text at 
    whitespace boundaries. Therefore, we must ensure that the minimum calculated column width 
    is greater than or equal to the widest single word in that column, preventing crashes 
    when the content is highly varied (e.g., a long URL vs. "A").

    Parameters:
        cell_html (str): The raw HTML string of the table cell.

    Returns:
        int: Length of the longest single word found in the cell's text content. Returns 0 if empty.
    """
    # Step 1: Strip all HTML tags to get pure text for analysis.
    text = re.sub(r'<[^>]+>', '', cell_html).strip()
    # Step 2: Use regex splitting by one or more whitespace characters (\s+) to reliably extract word boundaries.
    words = re.split(r'\s+', text)
    # Step 3: Calculate and return the maximum length found among all words.
    return max((len(w) for w in words), default=0)


def shrink_wide_tables(html_content, max_cols_before_shrink=6):
    """Gives explicit per-column widths (and smaller font/padding) to tables
    with many columns.

    xhtml2pdf/reportlab compute column widths automatically from cell content.
    With many narrow columns this auto-calculation can produce a negative
    available width and crash (ValueError: ... negative availWidth ...).
    Setting an explicit width on each header cell avoids that code path.

    Widths are set in absolute points (derived from the page's printable
    width) rather than percentages: xhtml2pdf resolves table-cell '%' widths
    against the full page width, not the margin-adjusted printable area, so
    percentage widths cause the last column(s) to spill past the right margin.

    Column widths are proportional to each column's content (the longest
    cell text in that column), with a minimum floor, so text-heavy columns
    (e.g. free-text notes) get more room than short numeric ones.
    """
    def process_table(match):
        table_html = match.group(0)
        header_row_match = re.search(r'<tr>(.*?)</tr>', table_html, flags=re.S)
        if not header_row_match:
            return table_html
        num_cols = len(re.findall(r'<th\b', header_row_match.group(1)))
        if num_cols <= max_cols_before_shrink:
            return table_html

        extra_cols = num_cols - max_cols_before_shrink
        font_pt = max(6.0, 9.0 - extra_cols * 0.4)
        pad_px = max(2, 6 - extra_cols)
        # Rough Helvetica-Bold average glyph width, used to size each
        # column's hard minimum from its longest unbreakable word.
        char_width_pt = font_pt * 0.62
        pad_pt = pad_px * 0.75 * 2  # px->pt, both sides

        # Longest cell text / longest single word per column, over every row.
        max_len = [0] * num_cols
        max_word_len = [0] * num_cols
        for row_match in re.finditer(r'<tr>(.*?)</tr>', table_html, flags=re.S):
            cells = re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', row_match.group(1), flags=re.S)
            for col_idx, cell_html in enumerate(cells[:num_cols]):
                max_len[col_idx] = max(max_len[col_idx], _cell_text_len(cell_html))
                max_word_len[col_idx] = max(max_word_len[col_idx], _longest_word_len(cell_html))

        # Slight safety margin (0.97) to absorb border/rounding overhead.
        usable_width_pt = PAGE_CONTENT_WIDTH_PT * 0.97

        # Hard floor: a column can never go below what its longest
        # unbreakable word needs, or xhtml2pdf silently expands it anyway
        # (overflowing the table past the page's right margin).
        hard_min_pt = [
            max(20.0, word_len * char_width_pt + pad_pt)
            for word_len in max_word_len
        ]

        # Weight = content length with a floor, so empty/short columns don't
        # collapse to nothing, and capped so one huge cell can't dominate.
        weights = [max(6, min(length, 40)) for length in max_len]
        total_weight = sum(weights)

        total_hard_min = sum(hard_min_pt)
        if total_hard_min >= usable_width_pt:
            # Content is too wide even at the minimums: fall back to the
            # hard minimums as-is (table will be as tight as it can be).
            col_widths_pt = hard_min_pt
        else:
            extra_width_pt = usable_width_pt - total_hard_min
            col_widths_pt = [
                hard_min_pt[i] + extra_width_pt * weights[i] / total_weight
                for i in range(num_cols)
            ]

        table_html = re.sub(
            r'<table\b[^>]*>',
            f'<table style="width:{PAGE_CONTENT_WIDTH_PT:.1f}pt;font-size:{font_pt:.1f}pt;">',
            table_html,
            count=1,
        )

        # Apply the width to every cell in every row (th AND td), not just
        # the header: xhtml2pdf resets a column's width down to just its
        # padding whenever it meets an EMPTY <td> with no explicit width,
        # silently discarding the width set on the header. Giving every
        # cell its own explicit width avoids that code path entirely.
        def process_row(row_match):
            row_html = row_match.group(0)
            col_idx = {'i': 0}

            def repl_cell(cell_match):
                tag = cell_match.group(1)
                inner = cell_match.group(2)
                i = col_idx['i']
                col_idx['i'] += 1
                width = col_widths_pt[i] if i < len(col_widths_pt) else 20.0
                return (
                    f'<{tag} style="width:{width:.2f}pt;padding:{pad_px}px 4px;">'
                    f'{inner}</{tag}>'
                )

            return re.sub(r'<(th|td)\b[^>]*>(.*?)</\1>', repl_cell, row_html, flags=re.S)

        table_html = re.sub(r'<tr>.*?</tr>', process_row, table_html, flags=re.S)
        return table_html

    return re.sub(r'<table\b[^>]*>.*?</table>', process_table, html_content, flags=re.S)


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


def build_toc(doc, has_headings, insert_after=None):
    """Builds a native, updatable Table of Contents field for Word documents.

    This inserts the real `{ TOC \\o "1-3" \\h \\z \\u }` field (wrapped in the
    same docPartObj/"Table of Contents" content control Word itself uses),
    with only a placeholder line as its cached result - no hand-built
    hyperlinks or bookmarks. Word/LibreOffice both take ownership of a field
    like this and rebuild its content themselves from the document's
    Heading 1-3 paragraphs whenever the user updates it (F9 / right-click >
    Update Field). Trying to pre-fill the cached result with our own
    hyperlinks was tried and made things worse: both editors detected the
    field, discarded our cached entries as stale, and produced a dead TOC
    that couldn't even be regenerated with F9. Leaving it genuinely empty is
    what makes the F9 update path (confirmed working by the user) kick in.

    Args:
        insert_after: xml element (e.g. a heading paragraph's ._p) the TOC block
            should be placed right after - typically the document title, so the
            title reads before the TOC instead of being pushed after it. Falls
            back to inserting at the very start of the document when None.
    """
    if not has_headings:
        return

    title_p = doc.add_paragraph()
    title_run = title_p.add_run('Table of Contents')
    title_run.font.size = Pt(18)
    title_run.font.bold = True

    field_p = doc.add_paragraph()
    field_p.paragraph_format.left_indent = Inches(0)

    r_begin = OxmlElement('w:r')
    fld_begin = OxmlElement('w:fldChar')
    fld_begin.set(qn('w:fldCharType'), 'begin')
    r_begin.append(fld_begin)

    r_instr = OxmlElement('w:r')
    instr_text = OxmlElement('w:instrText')
    instr_text.set(qn('xml:space'), 'preserve')
    instr_text.text = ' TOC \\o "1-3" \\h \\z \\u '
    r_instr.append(instr_text)

    r_separate = OxmlElement('w:r')
    fld_separate = OxmlElement('w:fldChar')
    fld_separate.set(qn('w:fldCharType'), 'separate')
    r_separate.append(fld_separate)

    r_placeholder = OxmlElement('w:r')
    rpr = OxmlElement('w:rPr')
    italic = OxmlElement('w:i')
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '888888')
    rpr.append(italic)
    rpr.append(color)
    r_placeholder.append(rpr)
    t_placeholder = OxmlElement('w:t')
    t_placeholder.text = (
        "Clic destro qui sopra e scegli \"Aggiorna campo\" (o seleziona il "
        "testo e premi F9) per generare il sommario."
    )
    r_placeholder.append(t_placeholder)

    r_end = OxmlElement('w:r')
    fld_end = OxmlElement('w:fldChar')
    fld_end.set(qn('w:fldCharType'), 'end')
    r_end.append(fld_end)

    for el in (r_begin, r_instr, r_separate, r_placeholder, r_end):
        field_p._p.append(el)

    doc.add_page_break()

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
    sdt_content.append(field_p._p)
    sdt.append(sdt_content)

    body = doc.element.body
    if insert_after is not None and insert_after in list(body):
        body.insert(list(body).index(insert_after) + 1, sdt)
    else:
        body.insert(0, sdt)


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
        has_headings = False
        title_element = None  # xml element of the first H1 (document title)
        
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
                
                if level == 1 and title_element is None:
                    # The very first H1 is the document title, not a numbered
                    # chapter: render it with the big built-in "Title" style,
                    # leave it out of the chapter numbering / TOC entries, and
                    # give it space-after instead of blank paragraphs so it
                    # doesn't sit glued to the TOC box that follows.
                    heading = doc.add_heading(title_clean, level=0)
                    heading.paragraph_format.space_after = Pt(0)
                    title_element = heading._p
                elif level in (1, 2, 3):
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
                    doc.add_heading(numbered_text, level=level)
                    has_headings = True
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

        build_toc(doc, has_headings, insert_after=title_element)

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
# Rimuovi l'eventuale TOC scritta a mano nel markdown sorgente: HTML, PDF e DOCX
# generano tutti la propria TOC automatica piu' avanti, quindi quella originale
# sarebbe solo duplicata.
md_text = strip_md_toc(md_text)
print(f"Read: {len(md_text)} characters.")

# ── Convert Markdown to HTML (required for HTML/PDF output) ──
needs_html = choice in ['H', 'P', 'A']
body_html = None
if needs_html and MARKDOWN_AVAILABLE:
    body_html = convert_to_html(md_text)
    body_html = shrink_wide_tables(body_html)

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

/* Document title (the first H1, pulled out in front of the TOC) */
.doc-title {
    font-size: 26pt;
    font-weight: 700;
    color: #1e3c72;
    margin: 0 0 28px 0;
    letter-spacing: .3px;
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
    table-layout: fixed;
    border-collapse: collapse;
    margin: 8px 0 12px 0;
    font-size: 9pt;
}
th {
    background: #eef3fb;
    color: #1e3c72;
    text-align: left;
    padding: 6px 8px;
    border: 1px solid #cdd9ec;
    font-weight: bold;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
td {
    padding: 6px 8px;
    border: 1px solid #dde5f0;
    vertical-align: top;
    word-wrap: break-word;
    overflow-wrap: break-word;
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

    # Holds the rendered title <h1> block once found, so it can be placed
    # before the TOC instead of staying wherever it naturally falls in the body.
    title_html_box = []

    def add_heading_id(match_obj):
        level = int(match_obj.group(1))
        inner_html = match_obj.group(2)

        text_plain = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', inner_html)
        text_plain = re.sub(r'<[^>]+>', '', text_plain)
        text_plain = ' '.join(text_plain.split())

        # The very first H1 is the document title, not a numbered chapter:
        # give it a distinct anchor/class, keep it out of the chapter
        # numbering and out of the TOC entries, and render it separately
        # before the TOC (mirrors the Word "Title" style treatment).
        if level == 1 and not title_html_box:
            base_id = slugify(text_plain)
            seen = used_ids.get(base_id, 0)
            used_ids[base_id] = seen + 1
            anchor_id = base_id if seen == 0 else f"{base_id}-{seen}"
            title_html_box.append(
                f'<a name="{anchor_id}">&nbsp;</a>'
                f'<h1 id="{anchor_id}" class="doc-title">{inner_html}</h1>'
            )
            return ''

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

    title_html = title_html_box[0] if title_html_box else ''

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

{title_html}

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

# Word conversion uses processed text (TOC stripped for markdown source TOC)
if choice in ['W', 'A']:
    if DOCX_AVAILABLE:
        word_path = stem.with_suffix('.docx')
        create_word_from_md(md_text, word_path)
        print(f"Generated: {word_path}")
    else:
        _missing('python-docx')
        print("Skipping DOCX generation.")

print("\n" + "=" * 40)
print("Conversion complete!")
print("=" * 40)
