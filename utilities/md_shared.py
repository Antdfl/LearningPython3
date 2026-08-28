#!/usr/bin/env python3
"""
utilities/md_shared.py

Small Markdown helpers shared between build_md_toc.py (hand-rolled
HTML/PDF/DOCX converter) and build_md_word_pandoc.py (Pandoc wrapper for
DOCX), kept dependency-free so importing either script doesn't drag in the
other's third-party libraries (markdown, xhtml2pdf, python-docx).
"""
import re


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

    Args:
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

    def _normalize_heading(s):
        """Strips any decorative characters (emoji, bullets, symbols) that may sit
        between the '#' markers and the heading text - e.g. '## \U0001F4CB INDICE' -
        so the heading_patterns above only need to match the plain text. Keeping this
        separate from `stripped` (used for is_list_item/is_anchor_list_item) avoids
        touching anything else that relies on the original line content."""
        return re.sub(r'^(#{1,3})\s*[^\w#]*\s*', r'\1 ', s)

    def is_list_item(s):
        return bool(re.match(r'^\s*(?:[-*+]|\d+[.)])\s+', s))

    def is_anchor_list_item(s):
        return bool(re.match(r'^\s*(?:[-*+]|\d+[.)])\s+.*\[.+?\]\(#.*?\)', s))

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
        normalized_heading = _normalize_heading(stripped)
        if any(re.match(p, normalized_heading, re.IGNORECASE) for p in heading_patterns):
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
