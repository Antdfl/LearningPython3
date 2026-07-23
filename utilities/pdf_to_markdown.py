#!/usr/bin/env python3
# ==============================================================================
# PDF to Markdown Converter - Native Table Detection (No External Libraries)
# ==============================================================================

"""
PDF to Markdown Converter - Native Table Detection

What this script does:
----------------------
1. Takes a PDF file with selectable text (not scanned images)
2. Extracts text and tables directly from each PDF page using PyMuPDF
3. Detects real tables via PyMuPDF's built-in table finder (geometry-based,
   not guesswork on whitespace), and converts them to proper Markdown tables
4. Formats everything into readable Markdown with headings and paragraphs

Why use this version?
---------------------
- MUCH faster than OCR-based conversion
- Preserves original text exactly as written in the PDF
- No need to install Tesseract OCR
- Table detection is based on the PDF's actual layout (lines/alignment),
  not on regex heuristics over extracted text
- Works perfectly for digital/text-based PDFs including technical manuals

Required libraries (install once):
-----------------------------------
    .\\Scripts\\pip.exe install pymupdf

IMPORTANT: This works with PDFs that have selectable text. If your PDF is a 
scanned image, this won't work and you need the OCR version instead.
"""


import sys          # For printing error messages to stderr
import re           # For regex matching (detecting headings, lists)
import argparse     # For handling command-line arguments
from pathlib import Path  # For cross-platform file path operations



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
    
    Example:
        >>> table_to_markdown([['Name', 'Age'], ['Alice', '30'], ['Bob', '25']])
        "| Name | Age |\n|--- | --- |\n| Alice | 30 |\n| Bob | 25 |"
    """
    if not rows:
        return ""  # If no rows, return empty string

    def clean_cell(cell):
        """
        Cleans a single cell value to make it safe for Markdown.
        
        Args:
            cell: The raw cell value (can be None or any type)
        
        Returns:
            str: A cleaned and Markdown-safe string
        """
        if cell is None:
            return ""  # If cell is None, return empty string
        
        # In Markdown, cells cannot contain raw newlines or unescaped pipes '|'
        # Replace any whitespace with a single space
        # Escape pipe characters by replacing '|' with '\|' for proper Markdown formatting
        return re.sub(r'\s+', ' ', str(cell)).replace('|', '\\|').strip()

    # Clean all cells in all rows using the clean_cell function
    cleaned_rows = [[clean_cell(c) for c in row] for row in rows]
    
    # Find the maximum number of columns across all rows
    num_cols = max(len(r) for r in cleaned_rows)

    # Pad short rows with empty strings to ensure every row has the same number of columns
    # This ensures uniform table structure where each row has exactly num_cols elements
    for row in cleaned_rows:
        row.extend([''] * (num_cols - len(row)))

    # The first row is the table header, remaining rows are body rows
    header, *body = cleaned_rows

    lines = ['| ' + ' | '.join(header) + ' |']  # First line: header with pipe separators
    lines.append('|' + '|'.join(['---'] * num_cols) + '|')  # Second line: separator dashes "---"
    for row in body:  # Add remaining body rows
        lines.append('| ' + ' | '.join(row) + ' |')

    return '\n'.join(lines)  # Join all lines with newlines and return


# ==============================================================================
# FUNCTION: extract_page_elements - Extract text blocks and tables from a page 
#                                 in reading order (top to bottom)
# ==============================================================================

def extract_page_elements(page, fitz):
    """
    Extracts a page's content as an ordered list of elements (top-to-bottom),
    where each element is either plain text block or a Markdown table.
    
    Tables are located using PyMuPDF's native table finder, which looks at
    the PDF's actual lines/alignment rather than guessing from whitespace
    in extracted text. Text blocks that overlap a detected table are
    skipped, since their content is already represented by the table.
    
    Args:
        page (fitz.Page): PyMuPDF page object containing the PDF page content
        fitz: Reference to the PyMuPDF module for utilities like Rect
    
    Returns:
        list[str]: List of text strings where each element is either a 
                   Markdown table or a plain text block.
    
    Example:
        elements = extract_page_elements(page, fitz)
        print(elements[0])  # Print first content block (table or text)
    """
    # Find all tables on the page using PyMuPDF's built-in table finder
    found_tables = page.find_tables()
    # Create Rectangles that bound each detected table (for overlap checking)
    table_bboxes = [fitz.Rect(t.bbox) for t in found_tables.tables]

    elements = []  # List of elements: tuple (y_coordinate, text_or_markdown_table)

    # -------------------------------------------------------------------------
    # STEP 1: Extract tables from the page using native PyMuPDF detection
    # -------------------------------------------------------------------------
    for t in found_tables.tables:
        markdown_table = table_to_markdown(t.extract())  # Convert table to Markdown
        if markdown_table:  # If there's a valid Markdown representation
            elements.append((t.bbox[1], markdown_table))  # Add with table's y-coordinate

    # -------------------------------------------------------------------------
    # STEP 2: Extract plain text blocks (skipping images and overlapping tables)
    # -------------------------------------------------------------------------
    blocks = page.get_text("blocks", flags=fitz.TEXT_PRESERVE_WHITESPACE)
    for block in blocks:
        x0, y0, x1, y1, text, _block_no, block_type = block
        
        # Skip blocks that are not plain text (e.g., images where block_type != 0)
        if block_type != 0:
            continue

        # Create a rectangle bounding this text block
        block_rect = fitz.Rect(x0, y0, x1, y1)
        
        # If the text block overlaps with any detected table, skip it
        # (the content is already represented by the table, not as plain text)
        if any(block_rect.intersects(tb) for tb in table_bboxes):
            continue

        # If the block has non-empty text, add it to elements list
        if text.strip():
            elements.append((y0, text.strip()))  # Add with its y-coordinate

    # Sort all elements by their Y coordinates (top to bottom on the page)
    elements.sort(key=lambda e: e[0])
    
    # Return only the text strings (without the y-coordinates)
    return [text for _y0, text in elements]


# ==============================================================================
# FUNCTION: extract_text_from_pdf - Extracts content from ALL pages of a PDF
# ==============================================================================

def extract_text_from_pdf(pdf_path):
    """
    Extracts text and tables from each page of the PDF using PyMuPDF.
    
    Args:
        pdf_path (str or Path): Path to the PDF file to process
    
    Returns:
        list[str]: List of strings where each element represents the formatted 
                   content of a page (text + tables).
    
    Raises:
        Exception: If errors occur during extraction.
    
    Example:
        pages = extract_text_from_pdf("document.pdf")
        for page in pages:
            print(page)
    """
    try:
        import fitz  # Import here to avoid circular dependency issues
        # Open the PDF file with PyMuPDF (fitz)
        doc = fitz.open(pdf_path)

        num_pages = len(doc)  # Total number of pages in the document
        print(f"✓ PDF has {num_pages} pages")  # Print number of pages found

        pages = []  # List to hold extracted content for each page

        for i in range(num_pages):
            page = doc[i]  # Get the current page object
            elements = extract_page_elements(page, fitz)  # Extract elements from this page
            # Join all elements of the page with two newlines between them
            page_text = '\n\n'.join(elements)

            if page_text.strip():  # If there is non-empty content
                pages.append(page_text)  # Add to pages list

        doc.close()  # Close the PDF document when finished

        print(f"✓ Extracted {len(pages)} pages of content")  # Print number of extracted pages

        return pages  # Return the list of page contents

    except Exception as e:
        # If an error occurs, print detailed message to stderr
        print(f"\nError extracting text from PDF: {e}", file=sys.stderr)
        raise  # Re-raise the exception


# ==============================================================================
# FUNCTION: clean_text - Cleans and formats the extracted text by removing
#                       unwanted lines while preserving important structures
# ==============================================================================

def clean_text(text):
    """
    Cleans and formats the extracted text to remove unwanted content like 
    page numbers and index markers, while preserving tables and important structures.
    
    Lines belonging to Markdown tables (starting with '|') are always
    preserved untouched - table rows and their pipe characters must
    never be filtered or merged with surrounding text.
    
    Args:
        text (str): Raw text extracted from the PDF
    
    Returns:
        str: Cleaned and formatted text
    
    Example:
        clean_text = clean_text(raw_extracted_text)
        print(clean_text)  # Print cleaned version
    """
    if not text or len(text.strip()) == 0:
        return ""  # If text is empty or only spaces, return empty string

    lines = text.split('\n')  # Split text into individual lines
    result_lines = []         # List to accumulate sections of cleaned text
    
    current_block = []        # Current buffer for joining lines of a paragraph
    current_table = []        # Buffer for accumulating table rows

    def flush_table():
        """Save the accumulated table lines to result and reset the buffer."""
        if current_table:  # If there are accumulated table rows
            result_lines.append('\n'.join(current_table))  # Add to results
            current_table.clear()  # Reset table buffer

    for line in lines:
        stripped = line.strip()  # Remove leading/trailing whitespace

        # --------------------------------------------------------------------
        # LOGIC 1: If line starts with '|', it's a table row - handle separately
        # --------------------------------------------------------------------
        if stripped.startswith('|'):
            if current_block:  # If there was a text block, save it first
                result_lines.append('\n'.join(current_block))
            current_block = []  # Reset text buffer
            current_table.append(stripped)  # Add table row to buffer
            continue  # Continue to next iteration (don't process further)

        # --------------------------------------------------------------------
        # LOGIC 2: Not a table row - flush any accumulated table rows first
        # --------------------------------------------------------------------
        flush_table()  # Save any accumulated table rows before processing text
        
        # Skip empty lines but preserve block separation for formatting
        if not stripped:
            if current_block:  # If there's a text block
                result_lines.append('\n'.join(current_block))  # Save it
                current_block = []  # Reset buffer
            continue  # Continue to next line

        # Filter out index/leader lines (lines with mostly dots/punctuation marks)
        dot_count = stripped.count('.')  # Count period characters in the line
        punct_count = sum(1 for c in stripped if c in '.-—–')  # Count other punctuation symbols
        
        # If line has more than 30% dots/punctuation, or more than 15 punct marks:
        if len(stripped) > 0 and (dot_count / len(stripped)) > 0.3 or punct_count > 15:
            # This line is mostly dots/punctuation - skip it (index lines like page numbers)
            if current_block:  # If there's text content before this index line
                result_lines.append('\n'.join(current_block))  # Save the block
                current_block = []  # Reset buffer
            continue  # Continue to next line

        # Add cleaned line to current paragraph block
        current_block.append(stripped)

    # Add any remaining content after processing all lines
    flush_table()  # Flush any remaining table rows
    if current_block:  # If there's remaining text block
        result_lines.append('\n'.join(current_block))  # Save it

    return '\n\n'.join(result_lines).strip()  # Join sections with double newlines and strip


# ==============================================================================
# FUNCTION: format_markdown - Applies Markdown formatting to the extracted text
# ==============================================================================

def format_markdown(text):
    """
    Applies basic Markdown formatting (headings, lists) to the extracted text.
    Preserves table structures exactly as-is.
    
    Args:
        text (str): Text to format
    
    Returns:
        str: Formatted Markdown text
    
    Example:
        formatted = format_markdown(plain_text)
        print(formatted)  # Print with proper Markdown formatting
    """
    lines = text.split('\n')  # Split into individual lines
    result_lines = []         # Accumulate formatted lines

    for line in lines:
        stripped = line.strip()

        if not stripped:  # Empty line
            result_lines.append("")
            continue

        # Table rows pass through untouched (preserve table structure)
        if stripped.startswith('|'):
            result_lines.append(stripped)
            continue

        # Check for Markdown heading (#, ##, ###, etc.)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', stripped)
        if header_match:
            level = len(header_match.group(1))  # Number of hashes = heading level
            title = header_match.group(2).strip()
            result_lines.append(f"{'#' * level} {title}")
            result_lines.append("")  # Add empty line after heading
            continue

        # Check for list item (-, *, or numbered format)
        list_marker = re.match(r'^(\s*)([-*+]\s+.+|\d+\.\s+.+)$', stripped)
        if list_marker:
            indent = len(list_marker.group(1))  # Number of spaces for indentation
            content = list_marker.group(2)  # The list item content
            result_lines.append(f"{' ' * indent}{content}")
            continue

        # Regular paragraph line - keep as-is
        result_lines.append(stripped)

    return '\n'.join(result_lines).strip()


# ==============================================================================
# FUNCTION: merge_paragraphs - Groups lines into logical paragraphs while 
#                            preserving table structures exactly
# ==============================================================================

def merge_paragraphs(text):
    """
    Groups wrapped text lines into logical paragraphs. Tables (consecutive 
    lines starting with '|') are kept intact - joining their rows would 
    collapse the table structure, causing rendering issues.
    
    Args:
        text (str): Text to group into paragraphs
    
    Returns:
        str: Text with proper paragraph grouping and preserved tables
    
    Example:
        grouped = merge_paragraphs(wrapped_text)
        print(grouped)  # Print with proper paragraphs
    """
    paragraphs = []       # List to hold completed paragraphs
    current_para = ""     # Current paragraph being built
    current_table_lines = []  # Buffer for accumulated table rows

    def flush_para():
        """Save the current paragraph if not empty."""
        nonlocal current_para
        if current_para:
            paragraphs.append(current_para)
            current_para = ""

    def flush_table():
        """Save the current table if there are accumulated rows."""
        nonlocal current_table_lines
        if current_table_lines:
            paragraphs.append('\n'.join(current_table_lines))
            current_table_lines = []

    for line in text.split('\n'):
        stripped = line.strip()

        # If it's a table row, save paragraph and start new table
        if stripped.startswith('|'):
            flush_para()  # Save any current paragraph first
            current_table_lines.append(stripped)  # Add to table buffer
            continue  # Continue (don't process as regular text)

        # Otherwise, flush any accumulated table rows first
        flush_table()
        
        # If empty line, just save current paragraph
        if not stripped:
            flush_para()
        else:
            # Add to current paragraph with space if needed
            current_para += (" " if current_para else "") + stripped

    # Flush any remaining content after the loop ends
    flush_para()  # Save last paragraph
    flush_table()  # Save last table if exists

    return '\n\n'.join(paragraphs).strip()  # Join paragraphs with double newlines


# ==============================================================================
# FUNCTION: pdf_to_markdown - Main function to convert PDF to Markdown 
#                           using direct text extraction and formatting
# ==============================================================================

def pdf_to_markdown(pdf_path, output_path=None, input_dir=None, output_dir=None):
    """
    Main function to convert a PDF file to Markdown.
    
    This function orchestrates the entire conversion process:
    1. Extracts text and tables from all PDF pages
    2. Cleans the extracted text (removes page numbers/index lines)
    3. Applies Markdown formatting (headings, lists)
    4. Groups text into logical paragraphs
    5. Saves the result to a .md file
    
    Args:
        pdf_path (str or Path): Path to the PDF file to convert
        output_path (str or None): Optional custom output file path. 
                                   If None, uses pdf_path with .md extension.
        input_dir (str or None): Directory containing the PDF file (if different from cwd)
        output_dir (str or None): Directory for output Markdown file (if different from cwd)
    
    Returns:
        str: Path to the generated Markdown file
    
    Raises:
        FileNotFoundError: If the input PDF file doesn't exist
    
    Example:
        output_file = pdf_to_markdown("input.pdf")  # Output: "input.md" in same dir
        output_file = pdf_to_markdown("input.pdf", output_path="output.md")
        output_file = pdf_to_markdown("input.pdf", output_dir="docs")
    """
    path = Path(pdf_path)  # Convert to Path object for easier handling

    # Handle input directory if provided
    if input_dir is not None:
        input_dir_path = Path(input_dir).resolve()  # Get absolute path
        pdf_path = str(input_dir_path / path.name)  # Update path to include input_dir

    # Check if file exists
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # Warn if file doesn't have .pdf extension
    if not str(path).lower().endswith('.pdf'):
        print("Warning: file does not have .pdf extension", file=sys.stderr)

    # Set output path (use provided or default to input with .md extension)
    if output_path is None:
        output_path = path.with_suffix('.md')  # Default: same name with .md extension

    # Handle output directory if provided
    if output_dir is not None:
        output_dir_path = Path(output_dir).resolve()  # Get absolute path
        output_path = str(output_dir_path / output_path.name)  # Update path to include output_dir

    output_path = Path(output_path)  # Convert output path to Path object

    try:
        # STEP 1: Extract text and tables from PDF, page by page
        pages = extract_text_from_pdf(pdf_path)
        
        # STEP 2: Combine all pages with separators (--- between pages)
        full_text = '\n\n---\n\n'.join(pages)

        print(f"✓ Extracted text: {len(full_text)} characters")

        # STEP 3: Clean the text (filter out index lines, preserve tables)
        clean_text_result = clean_text(full_text)

        # STEP 4: Format as Markdown (add headings, lists, etc.)
        markdown_text = format_markdown(clean_text_result)
        
        # STEP 5: Merge wrapped paragraphs into logical groups
        markdown_text = merge_paragraphs(markdown_text)

        # STEP 6: Save output to file with UTF-8 encoding
        output_path.write_text(markdown_text, encoding='utf-8')

        print(f"\n✓ Conversion completed successfully!")
        print(f"  Input:    {path}")
        print(f"  Output:   {output_path}")
        print(f"  Characters: {len(markdown_text)}")

        # Calculate word count
        word_count = sum(1 for word in markdown_text.split() if word.strip())
        print(f"  Words:    {word_count}")

        return str(output_path)  # Return path to generated file

    except Exception as e:
        # Print error to stderr and re-raise
        print(f"\n✗ Error during conversion: {e}", file=sys.stderr)
        raise


# ==============================================================================
# FUNCTION: main - Command-line interface entry point for PDF to Markdown converter
# ==============================================================================

def main():
    """
    Command-line interface for the PDF to Markdown converter.
    
    Usage examples:
        python pdf_to_markdown.py document.pdf
        python pdf_to_markdown.py document.pdf -o output.md
        python pdf_to_markdown.py document.pdf --output-dir .\\output
    
    Notes:
        - This works with PDFs that have selectable text (not scanned images)
        - Tables are detected from the PDF's actual layout (lines/alignment)
          and converted to proper Markdown table syntax
        - If the PDF is a scanned image, install Tesseract OCR and use the OCR version instead
    
    Args:
        pdf_file: Path to the PDF file to convert
        -o, --output: Optional output file path for Markdown result
        --input-dir: Directory containing the PDF (if different from current directory)
        --output-dir: Directory for output Markdown file (if different from current dir)
    """
    parser = argparse.ArgumentParser(
        description='Convert PDF files to Markdown (direct text extraction with native table detection)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_markdown.py document.pdf
  python pdf_to_markdown.py document.pdf -o output.md
  python pdf_to_markdown.py document.pdf --output-dir .\\output

Notes:
  - This works with PDFs that have selectable text (not scanned images)
  - Tables are detected from the PDF's actual layout (lines/alignment)
    and converted to proper Markdown table syntax
  - If the PDF is a scanned image, install Tesseract OCR and use the OCR version instead
         """
    )

    parser.add_argument('pdf_file', help='Path to the PDF file to convert')
    parser.add_argument('-o', '--output', help='Path for the Markdown output file')
    parser.add_argument('--input-dir', dest='input_dir', default=None,
                         help='Directory containing the PDF file')
    parser.add_argument('--output-dir', dest='output_dir', default=None,
                         help='Directory for output Markdown file')

    args = parser.parse_args()

    # Resolve full path considering input directory if provided
    pdf_path = args.pdf_file
    if args.input_dir is not None:
        pdf_path = str(Path(args.input_dir) / pdf_path)

    # Set output path (use provided or auto-generate from input filename)
    output_path = args.output
    if output_path is None:
        output_path = pdf_path.rsplit('.', 1)[0] + '.md'  # Same name with .md extension

    # Handle output directory if provided
    if args.output_dir is not None:
        output_path = str(Path(args.output_dir) / Path(output_path).name)

    try:
        # Call the main conversion function
        pdf_to_markdown(
            pdf_path=pdf_path,
            output_path=output_path,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error code
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)  # Exit with error code


# ==============================================================================
# Entry point - Run main() when this script is executed directly
# ==============================================================================

if __name__ == '__main__':
    main()