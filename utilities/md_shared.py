#!/usr/bin/env python3
"""
utilities/md_shared.py

Small Markdown helpers shared between build_md_toc.py (hand-rolled
HTML/PDF/DOCX converter) and build_md_word_pandoc.py (Pandoc wrapper for
DOCX), kept dependency-free so importing either script doesn't drag in the
other's third-party libraries (markdown, xhtml2pdf, python-docx).
"""
import re
import unicodedata


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


_FENCE_LINE_RE = re.compile(r'^(```|~~~)')

# Unicode ranges holding pictographic characters (emoji). Deliberately NOT a
# single sweeping "everything above U+2100" rule: real documents use
# Mathematical Operators (=, /=, <=) and Arrows (DB->front-end) as ordinary
# text, and those blocks sit right between the pictographic ones.
_EMOJI_CHARS = (
    '\U0001F000-\U0001FAFF'  # emoticons, pictographs, transport, flags, supplemental symbols
    '\u2600-\u27BF'          # Miscellaneous Symbols + Dingbats (warning sign, check mark, cross mark)
    '\u2B00-\u2BFF'          # Miscellaneous Symbols and Arrows (star, filled square)
    '\u231A-\u23FA'          # watch/hourglass/alarm-clock subset of Miscellaneous Technical
)

# The invisible characters that glue an emoji sequence together: U+FE0F
# (variation selector, the "render this as an emoji" flag), U+200D (zero-width
# joiner, used by composed emoji) and U+20E3 (combining keycap). Written as
# escapes on purpose - as literals they would be unreadable in the source.
_EMOJI_GLUE = '\uFE0F\u200D\u20E3'

# One emoji "run": consecutive pictographs with their glue characters, plus any
# spaces that FOLLOW them, so removing the emoji does not leave a double space
# behind. Whitespace BEFORE the run is deliberately left alone: eating it would
# destroy the indentation of a code line that happens to start with an emoji.
_EMOJI_RUN_RE = re.compile(f'(?:[{_EMOJI_CHARS}][{_EMOJI_GLUE}]*)+[ \t]*')

# Mathematical Alphanumeric Symbols (U+1D400-U+1D7FF): the "fake bold/italic"
# letters produced by LinkedIn text generators, since LinkedIn itself strips
# Markdown. A run keeps single spaces between styled words, so a whole styled
# phrase becomes ONE emphasis span instead of one per word.
_MATH_ALNUM_RUN_RE = re.compile(
    r'[\U0001D400-\U0001D7FF]+(?: +[\U0001D400-\U0001D7FF]+)*'
)


def _unstyle_math_alnum(line, emphasis):
    """Rewrites "fake bold/italic" Mathematical Alphanumeric Symbols as plain
    ASCII, optionally wrapped in the equivalent Markdown emphasis markers.

    The conversion itself is just NFKC normalization: every character in the
    block carries a compatibility decomposition back to its plain letter or
    digit (U+1D5E7 MATHEMATICAL SANS-SERIF BOLD CAPITAL T -> 'T'). The style
    is recovered from the character's own Unicode name, which spells out
    'BOLD' and/or 'ITALIC', so no hand-maintained table of the block's 14
    sub-ranges is needed.

    Args:
        line (str): A single line of Markdown text.
        emphasis (bool): True to wrap the recovered text in Markdown emphasis
            markers (**bold**, *italic*, ***bold italic***). Must be False
            inside a fenced code block, where Markdown is not parsed and the
            asterisks would show up literally in the output.

    Returns:
        str: The line with every styled run replaced by plain text.
    """
    def replace_run(match):
        plain = unicodedata.normalize('NFKC', match.group(0))
        if not emphasis:
            return plain
        # A styled run is homogeneous in practice, so the first character's
        # name describes the whole run.
        name = unicodedata.name(match.group(0)[0], '')
        marker = ('**' if 'BOLD' in name else '') + ('*' if 'ITALIC' in name else '')
        return f'{marker}{plain}{marker}' if marker else plain

    return _MATH_ALNUM_RUN_RE.sub(replace_run, line)


def replace_unsupported_glyphs(md_text):
    """Removes emoji and converts "fake bold" Unicode letters to real Markdown,
    so neither of them renders as an empty box in the generated PDF.

    WHY THIS EXISTS: xhtml2pdf draws text through ReportLab, which can only
    render monochrome outline glyphs taken from the ONE font matched by the
    CSS 'font-family'. Two consequences, both confirmed on a real document:

    1. Emoji are impossible, not just unstyled. Windows' colour emoji font
       (Segoe UI Emoji) stores its glyphs as colour bitmaps, a format
       ReportLab cannot draw at all - so no font-family change fixes this.
    2. ReportLab does not fall back to another font per missing character the
       way a browser does. If the matched font lacks a glyph, the result is a
       box, regardless of the fallback families listed after it in the CSS.

    Since the characters cannot be drawn, they are removed or rewritten here
    instead, before the Markdown ever reaches the converter:

    - Emoji are dropped, together with any spaces immediately after them, so
      "[rocket] THE RULE:" becomes "THE RULE:" and not " THE RULE:".
    - Mathematical Alphanumeric Symbols - the Unicode "fake bold" used to
      emphasise text on platforms that strip Markdown, such as LinkedIn - are
      converted back to plain letters. OUTSIDE a fenced code block they are
      wrapped in real Markdown emphasis, so the PDF shows genuine bold text
      instead of boxes; INSIDE a fence the markers are omitted, because
      Markdown is not parsed there and '**' would be printed literally.

    Characters that merely look decorative but are ordinary text are left
    untouched: mathematical operators (=, /=, <=), arrows, dashes and typographic
    quotes all render normally in the PDF fonts.

    Args:
        md_text (str): The raw Markdown content string.

    Returns:
        str: The same Markdown with unrenderable characters removed or
            rewritten. Text containing none of them is returned unchanged.
    """
    out_lines = []
    in_fence = False

    for line in md_text.split('\n'):
        if _FENCE_LINE_RE.match(line.lstrip()):
            in_fence = not in_fence
            out_lines.append(line)
            continue

        cleaned = _EMOJI_RUN_RE.sub('', line)
        if cleaned != line:
            # An emoji sitting at the end of a line leaves trailing spaces
            # behind. Only lines that actually had one are stripped, so a
            # deliberate two-space Markdown line break elsewhere survives.
            cleaned = cleaned.rstrip()
        out_lines.append(_unstyle_math_alnum(cleaned, emphasis=not in_fence))

    return '\n'.join(out_lines)
