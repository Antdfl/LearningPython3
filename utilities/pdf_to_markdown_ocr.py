#!/usr/bin/env python3
# ==============================================================================
# PDF to Markdown Converter - Tesseract OCR Support (Mixed text+images)
# ==============================================================================

"""
PDF to Markdown Converter with local Tesseract OCR

What this script does:
----------------------
1. Automatically detects whether a PDF has selectable text or is image-based (scanned)
2. For text-based PDFs: Uses PyMuPDF for fast extraction with native table detection
3. For image-based PDFs: Uses Tesseract OCR (local) on page images
4. For mixed PDFs (text + images): Uses Tesseract to extract text from image portions

Why use this version?
----------------------
- Automatic detection: chooses the best method for each PDF
- Faster for digital PDFs (no OCR needed)
- For scanned PDFs: Uses local Tesseract OCR (no API key, no cost)
- Produces proper Markdown output with tables
- Supports native table detection from PyMuPDF

Required libraries (install via pip):
-----------------------------------
    pip install pymupdf pytesseract pillow
    
Note: The Tesseract executable (tesseract.exe + tessdata/) must be located in the
"tesseract" folder next to this script (utilities/tesseract/).
"""

import sys
import re
import argparse
import io
import os
from pathlib import Path

# Import PyMuPDF for PDF manipulation and text extraction
try:
    import fitz
except ImportError:
    print("Error: PyMuPDF is not installed.", file=sys.stderr)
    print("Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

# Import pytesseract and Pillow for local OCR on image-based PDFs
try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("Error: pytesseract or pillow is not installed.", file=sys.stderr)
    print("Install with: pip install pytesseract pillow", file=sys.stderr)
    sys.exit(1)


# ==============================================================================
# FUNCTION: configure_tesseract - Point pytesseract to the local Tesseract build
# ==============================================================================

def configure_tesseract():
    """
    Configures pytesseract to use the portable Tesseract build shipped alongside
    this script, in the "tesseract" subfolder (tesseract.exe + tessdata/).

    Raises:
        FileNotFoundError: If tesseract.exe is not found where expected
    """
    tesseract_dir = Path(__file__).parent / 'tesseract'
    tesseract_exe = tesseract_dir / 'tesseract.exe'
    tessdata_dir = tesseract_dir / 'tessdata'

    if not tesseract_exe.exists():
        raise FileNotFoundError(
            f"tesseract.exe not found in {tesseract_dir}. "
            "Copy the Tesseract build there (tesseract.exe, DLLs and tessdata/)."
        )

    pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
    os.environ['TESSDATA_PREFIX'] = str(tessdata_dir)


# ==============================================================================
# FUNCTION: detect_pdf_type - Detect whether PDF has selectable text or is image-based
# ==============================================================================

def detect_pdf_type(pdf_path):
    """
    Detects whether a PDF contains selectable text or is entirely image-based.
    
    Args:
        pdf_path (str or Path): Path to the PDF file
        
    Returns:
        str: 'text_based' if the PDF has selectable text, 'image_based' if it's scanned
    """
    try:
        doc = fitz.open(pdf_path)
        
        for i in range(len(doc)):
            page = doc[i]
            blocks = page.get_text("blocks", flags=0)
            
            if blocks:
                for block in blocks:
                    x0, y0, x1, y1, text, _block_no, block_type = block
                    if block_type == 0 and text.strip():
                        doc.close()
                        return 'text_based'
        
        doc.close()
        return 'image_based'
        
    except Exception as e:
        print(f"Warning: Could not detect PDF type: {e}", file=sys.stderr)
        return 'image_based'


# ==============================================================================
# FUNCTION: convert_pdf_page_to_image - Convert a specific page to RGB image for OCR
# ==============================================================================

def convert_pdf_page_to_image(pdf_path, page_num):
    """
    Converts a specific PDF page to an RGB PNG image.
    
    Args:
        pdf_path (str or Path): Path to the PDF file
        page_num (int): Page number (0-indexed)
        
    Returns:
        bytes: Raw PNG image data
    """
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    # Render page to RGB pixel array
    pix = page.get_pixmap(colorspace="rgb")
    png_data = pix.tobytes("png")
    
    doc.close()
    return png_data


# ==============================================================================
# FUNCTION: extract_text_with_tesseract - Extract text using local Tesseract OCR
# ==============================================================================

def extract_text_with_tesseract(image_data, lang='eng+ita'):
    """
    Uses local Tesseract OCR to extract text from an image.

    Args:
        image_data (bytes): Raw PNG image data
        lang (str): Tesseract language(s) to use, e.g. 'eng+ita'

    Returns:
        str: Extracted text string, or empty string if no text found
    """
    configure_tesseract()

    image = Image.open(io.BytesIO(image_data))
    text = pytesseract.image_to_string(image, lang=lang)

    return text


# ==============================================================================
# FUNCTION: extract_text_from_pdf - Extracts content from ALL pages of a PDF
# ==============================================================================

def extract_text_from_pdf(pdf_path, use_ocr=True):
    """
    Extracts text and tables from each page of the PDF.

    This function automatically handles:
    - Pure text PDFs (fast extraction with native table detection)
    - Image-based PDFs (OCR via local Tesseract)
    - Mixed PDFs (text + images) - uses OCR for image portions

    Args:
        pdf_path (str or Path): Path to the PDF file to process
        use_ocr (bool): Whether to use Tesseract OCR for image-based/mixed pages
        
    Returns:
        list[str]: List of strings where each element represents the formatted 
                   content of a page.
        
    Raises:
        Exception: If errors occur during extraction.
    """
    doc = fitz.open(pdf_path)

    num_pages = len(doc)
    print(f"✓ PDF has {num_pages} pages")

    pages = []

    for i in range(num_pages):
        page = doc[i]
        
        # Check if this page has selectable text (text-based content)
        blocks = page.get_text("blocks", flags=0)
        has_selectable_text = False
        
        for block in blocks:
            x0, y0, x1, y1, text, _block_no, block_type = block
            if block_type == 0 and text.strip():
                has_selectable_text = True
                break
        
        # Determine extraction method based on page content
        if has_selectable_text:
            # Page has selectable text - use fast native extraction with table detection
            elements = _extract_page_with_tables(page, doc)
        elif use_ocr:
            # Page is image-based or mixed (text embedded in images) - use Tesseract OCR
            elements = _extract_page_with_ocr(page, pdf_path)
        else:
            # No text and no OCR - try native extraction anyway as fallback
            elements = _extract_page_with_tables(page, doc)
        
        # Join all elements of the page with two newlines between them
        page_text = '\n\n'.join(elements) if elements else ""

        if page_text.strip():
            pages.append(page_text)

    doc.close()

    print(f"✓ Extracted {len(pages)} pages of content")

    return pages


# ==============================================================================
# FUNCTION: _extract_page_with_tables - Extract text and tables from a page (text-based)
# ==============================================================================

def _extract_page_with_tables(page, doc):
    """
    Extracts a page's content as an ordered list of elements (top-to-bottom),
    where each element is either plain text block or a Markdown table.
    
    Args:
        page (fitz.Page): PyMuPDF page object
        doc (fitz.Document): Document reference for utility access
        
    Returns:
        list[str]: List of text strings (tables and text blocks)
    """
    # Find all tables on the page using PyMuPDF's built-in table finder
    found_tables = page.find_tables()
    table_bboxes = [fitz.Rect(t.bbox) for t in found_tables.tables]

    elements = []

    # STEP 1: Extract tables from the page using native PyMuPDF detection
    for t in found_tables.tables:
        markdown_table = table_to_markdown(t.extract())
        if markdown_table:
            elements.append((t.bbox[1], markdown_table))

    # STEP 2: Extract plain text blocks (skipping images and overlapping tables)
    blocks = page.get_text("blocks", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in blocks:
        x0, y0, x1, y1, text, _block_no, block_type = block
        
        if block_type != 0:
            continue

        block_rect = fitz.Rect(x0, y0, x1, y1)
        
        if any(block_rect.intersects(tb) for tb in table_bboxes):
            continue

        if text.strip():
            elements.append((y0, text.strip()))

    elements.sort(key=lambda e: e[0])
    
    return [text for _y0, text in elements]


# ==============================================================================
# FUNCTION: _extract_page_with_ocr - Extract text from image-based/mixed pages using Tesseract OCR
# ==============================================================================

def _extract_page_with_ocr(page, pdf_path):
    """
    Extracts text from an image-based or mixed PDF page using local Tesseract OCR.

    This handles:
    - Fully scanned/image PDF pages
    - Mixed pages containing images with embedded text (e.g., screenshots, diagrams)

    Args:
        page (fitz.Page): PyMuPDF page object
        pdf_path (str or Path): Path to the PDF file

    Returns:
        list[str]: List of text strings extracted via OCR
    """
    # Convert CURRENT page to image for OCR
    image_data = convert_pdf_page_to_image(pdf_path, page.number)

    # Extract text using local Tesseract OCR
    extracted_text = extract_text_with_tesseract(image_data)
    
    if not extracted_text.strip():
        return []
    
    # Split into lines for better paragraph handling
    lines = extracted_text.split('\n')
    
    # Process lines to build paragraphs
    paragraphs = []
    current_para = ""
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            if current_para:
                paragraphs.append(current_para)
                current_para = ""
        else:
            current_para += " " + stripped
    
    if current_para:
        paragraphs.append(current_para)
    
    return paragraphs


# ==============================================================================
# FUNCTION: table_to_markdown - Convert extracted table rows to a Markdown table
# ==============================================================================

def table_to_markdown(rows):
    """
    Converts a list of table rows (each a list of cell values) into 
    a properly formatted Markdown table.
    
    Args:
        rows (list[list]): List of lists where each inner list represents 
                           a row of the table with its cell values.

    Returns:
        str: A Markdown-formatted table string, or empty string if rows is empty.
    """
    if not rows:
        return ""

    def clean_cell(cell):
        if cell is None:
            return ""
        
        import re as regex
        return regex.sub(r'\s+', ' ', str(cell)).replace('|', '\\|').strip()

    cleaned_rows = [[clean_cell(c) for c in row] for row in rows]
    
    num_cols = max(len(r) for r in cleaned_rows)

    for row in cleaned_rows:
        row.extend([''] * (num_cols - len(row)))

    header, *body = cleaned_rows

    lines = ['| ' + ' | '.join(header) + ' |']
    lines.append('|' + '|'.join(['---'] * num_cols) + '|')
    for row in body:
        lines.append('| ' + ' | '.join(row) + ' |')

    return '\n'.join(lines)


# ==============================================================================
# FUNCTION: clean_text - Cleans and formats the extracted text
# ==============================================================================

def clean_text(text):
    """
    Cleans and formats the extracted text to remove unwanted content.
    
    Args:
        text (str): Raw text extracted from the PDF
    
    Returns:
        str: Cleaned and formatted text
    """
    if not text or len(text.strip()) == 0:
        return ""

    lines = text.split('\n')
    result_lines = []
    current_block = []
    current_table = []

    def flush_table():
        if current_table:
            result_lines.append('\n'.join(current_table))
            current_table.clear()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('|'):
            if current_block:
                result_lines.append('\n'.join(current_block))
            current_block = []
            current_table.append(stripped)
            continue

        flush_table()
        
        if not stripped:
            if current_block:
                result_lines.append('\n'.join(current_block))
                current_block = []
            continue

        dot_count = stripped.count('.')
        punct_count = sum(1 for c in stripped if c in '.-—–')
        
        if len(stripped) > 0 and (dot_count / len(stripped)) > 0.3 or punct_count > 15:
            if current_block:
                result_lines.append('\n'.join(current_block))
                current_block = []
            continue

        current_block.append(stripped)

    flush_table()
    if current_block:
        result_lines.append('\n'.join(current_block))

    return '\n\n'.join(result_lines).strip()


# ==============================================================================
# FUNCTION: format_markdown - Applies Markdown formatting to the extracted text
# ==============================================================================

def format_markdown(text):
    """
    Applies basic Markdown formatting (headings, lists) to the extracted text.
    
    Args:
        text (str): Text to format
    
    Returns:
        str: Formatted Markdown text
    """
    lines = text.split('\n')
    result_lines = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            result_lines.append("")
            continue

        if stripped.startswith('|'):
            result_lines.append(stripped)
            continue

        header_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            result_lines.append(f"{'#' * level} {title}")
            result_lines.append("")
            continue

        list_marker = re.match(r'^(\s*)([-*+]\s+.+|\d+\.\s+.+)$', stripped)
        if list_marker:
            indent = len(list_marker.group(1))
            content = list_marker.group(2)
            result_lines.append(f"{' ' * indent}{content}")
            continue

        result_lines.append(stripped)

    return '\n'.join(result_lines).strip()


# ==============================================================================
# FUNCTION: merge_paragraphs - Groups lines into logical paragraphs
# ==============================================================================

def merge_paragraphs(text):
    """
    Groups wrapped text lines into logical paragraphs. Tables are kept intact.
    
    Args:
        text (str): Text to group into paragraphs
    
    Returns:
        str: Text with proper paragraph grouping and preserved tables
    """
    paragraphs = []
    current_para = ""
    current_table_lines = []

    def flush_para():
        nonlocal current_para
        if current_para:
            paragraphs.append(current_para)
            current_para = ""

    def flush_table():
        nonlocal current_table_lines
        if current_table_lines:
            paragraphs.append('\n'.join(current_table_lines))
            current_table_lines = []

    for line in text.split('\n'):
        stripped = line.strip()

        if stripped.startswith('|'):
            flush_para()
            current_table_lines.append(stripped)
            continue

        flush_table()
        
        if not stripped:
            flush_para()
        else:
            current_para += (" " if current_para else "") + stripped

    flush_para()
    flush_table()

    return '\n\n'.join(paragraphs).strip()


# ==============================================================================
# FUNCTION: pdf_to_markdown - Main function to convert PDF to Markdown
# ==============================================================================

def pdf_to_markdown(pdf_path, output_path=None, input_dir=None, output_dir=None, use_ocr=True):
    """
    Main function to convert a PDF file to Markdown.
    
    This function orchestrates the entire conversion process:
    1. Detects if PDF is text-based or image-based/mixed
    2. Extracts text (using PyMuPDF for text-based, Tesseract OCR for image-based)
    3. Cleans the extracted text
    4. Applies Markdown formatting
    5. Saves the result to a .md file
    
    Args:
        pdf_path (str or Path): Path to the PDF file to convert
        output_path (str or None): Optional custom output file path. 
                                   If None, uses pdf_path with .md extension.
        input_dir (str or None): Directory containing the PDF file
        output_dir (str or None): Directory for output Markdown file
        use_ocr (bool): Whether to use Tesseract OCR for image-based/mixed pages
                        Default: True (handles mixed PDFs automatically)
        
    Returns:
        str: Path to the generated Markdown file
    
    Raises:
        FileNotFoundError: If the input PDF file doesn't exist
    """
    path = Path(pdf_path)

    if input_dir is not None:
        input_dir_path = Path(input_dir).resolve()
        pdf_path = str(input_dir_path / path.name)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not str(path).lower().endswith('.pdf'):
        print("Warning: file does not have .pdf extension", file=sys.stderr)

    if output_path is None:
        output_path = path.with_suffix('.md')

    if output_dir is not None:
        output_dir_path = Path(output_dir).resolve()
        output_path = str(output_dir_path / output_path.name)

    output_path = Path(output_path)

    try:
        pages = extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
        
        full_text = '\n\n---\n\n'.join(pages)

        print(f"✓ Extracted text: {len(full_text)} characters")

        clean_text_result = clean_text(full_text)

        markdown_text = format_markdown(clean_text_result)
        
        markdown_text = merge_paragraphs(markdown_text)

        output_path.write_text(markdown_text, encoding='utf-8')

        print(f"\n✓ Conversion completed successfully!")
        print(f"  Input:    {path}")
        print(f"  Output:   {output_path}")
        print(f"  Characters: {len(markdown_text)}")

        word_count = sum(1 for word in markdown_text.split() if word.strip())
        print(f"  Words:    {word_count}")

        return str(output_path)

    except Exception as e:
        print(f"\n✗ Error during conversion: {e}", file=sys.stderr)
        raise


# ==============================================================================
# FUNCTION: main - Command-line interface entry point for PDF to Markdown converter
# ==============================================================================

def main():
    """
    Command-line interface for the PDF to Markdown converter.
    
    Usage examples:
        python pdf_to_markdown_ocr.py document.pdf
        python pdf_to_markdown_ocr.py document.pdf -o output.md
        python pdf_to_markdown_ocr.py document.pdf --output-dir .\\output
        python pdf_to_markdown_ocr.py document.pdf --no-ocr  # Disable OCR for speed
    
    Notes:
        - This automatically detects text-based PDFs (fast extraction) or image-based/mixed PDFs
        - Tables are detected from the PDF's actual layout and converted to proper Markdown table syntax
        - For image-based/mixed PDFs, local Tesseract OCR is enabled by default
          (requires the Tesseract build in utilities/tesseract/)
        - Use --no-ocr if you have a pure text PDF and want faster processing
    """
    parser = argparse.ArgumentParser(
        description='Convert PDF files to Markdown with automatic detection and native table support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_markdown_ocr.py document.pdf                    # Auto-detect and convert (default)
  python pdf_to_markdown_ocr.py document.pdf -o output.md       # Specify output filename
  python pdf_to_markdown_ocr.py document.pdf --output-dir .\\output  # Specify output directory
  python pdf_to_markdown_ocr.py document.pdf --no-ocr            # Disable OCR for pure text PDFs (faster)

Notes:
  - By default, local Tesseract OCR is enabled for handling mixed PDFs (text + images automatically)
  - No API key or internet connection required - everything runs locally
  - For pure text PDFs, consider using --no-ocr for faster processing
  - Requires the Tesseract build (tesseract.exe + tessdata/) in utilities/tesseract/
"""
    )

    parser.add_argument('pdf_file', help='Path to the PDF file to convert')
    parser.add_argument('-o', '--output', help='Path for the Markdown output file')
    parser.add_argument('--input-dir', dest='input_dir', default=None,
                         help='Directory containing the PDF file')
    parser.add_argument('--output-dir', dest='output_dir', default=None,
                         help='Directory for output Markdown file')
    # Default is True (enable Tesseract OCR for mixed PDFs)
    # Use --no-ocr to disable OCR and use native extraction only
    parser.add_argument('--no-ocr', dest='use_ocr', action='store_false',
                         help='Disable Tesseract OCR on image-based/mixed PDFs (faster for pure text)')

    args = parser.parse_args()

    pdf_path = args.pdf_file
    if args.input_dir is not None:
        pdf_path = str(Path(args.input_dir) / pdf_path)

    output_path = args.output
    if output_path is None:
        output_path = pdf_path.rsplit('.', 1)[0] + '.md'

    if args.output_dir is not None:
        output_path = str(Path(args.output_dir) / Path(output_path).name)

    try:
        pdf_to_markdown(
            pdf_path=pdf_path,
            output_path=output_path,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            use_ocr=args.use_ocr,  # Defaults to True if not specified
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# ==============================================================================
# Entry point - Run main() when this script is executed directly
# ==============================================================================

if __name__ == '__main__':
    main()