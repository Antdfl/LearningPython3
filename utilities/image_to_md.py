#!/usr/bin/env python3
# ==============================================================================
# Image to Markdown Converter - Tesseract OCR (JPEG, PNG, GIF)
# ==============================================================================

"""
Image to Markdown Converter with local Tesseract OCR

What this script does:
----------------------
1. Accepts one or more image files (.jpg, .jpeg, .png, .gif), or a directory
   containing them
2. Runs each image through local Tesseract OCR to extract its text
3. When multiple images are given, orders them by any number found in their
   filename (a prefix like "1_nome_file.jpg" or a suffix like "file_2.png"),
   so a multi-page scan is reassembled in the right order
4. Joins the extracted text into a single Markdown (.md) file, one page's
   text per image, separated by a horizontal rule
5. Asks for confirmation before overwriting an existing output file
   (defaults to No)

Required libraries (install via pip):
-----------------------------------
    pip install pytesseract pillow

Note: The Tesseract executable (tesseract.exe + tessdata/) must be located in
the "tesseract" folder next to this script (utilities/tesseract/).
"""

import sys
import re
import argparse
from pathlib import Path

# Import pytesseract and Pillow for local OCR
try:
    import pytesseract
    from PIL import Image
except ImportError:
    print("Error: pytesseract or pillow is not installed.", file=sys.stderr)
    print("Install with: pip install pytesseract pillow", file=sys.stderr)
    sys.exit(1)


SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

NO_IMAGES_MESSAGE = (
    "Ho bisogno di almeno un'immagine da convertire in testo "
    "(est. *.png, *.jpeg, *.gif)"
)


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
    import os
    os.environ['TESSDATA_PREFIX'] = str(tessdata_dir)


# ==============================================================================
# FUNCTION: natural_sort_key - Sort key that orders filenames by embedded numbers
# ==============================================================================

def natural_sort_key(path):
    """
    Builds a sort key that orders filenames the way a human would, by treating
    any run of digits as a number instead of comparing it character-by-character.

    This covers both a numeric prefix ("1_nome_file.jpg", "2_nome_file.jpg", ...)
    and a numeric suffix ("file_2.png", "file_10.png", ...): whichever number is
    embedded in the name is compared numerically, so "file_2" sorts before
    "file_10". Filenames without any digits simply fall back to alphabetical order.

    Args:
        path (str or Path): Image file path

    Returns:
        list: A key suitable for use with sorted()/list.sort()
    """
    stem = Path(path).stem
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', stem)]


# ==============================================================================
# FUNCTION: collect_image_paths - Resolve CLI inputs into a sorted list of images
# ==============================================================================

def collect_image_paths(inputs):
    """
    Resolves the given inputs (image file paths and/or directories) into a
    flat, naturally-ordered list of image files.

    Args:
        inputs (list[str or Path]): Image file paths and/or directory paths

    Returns:
        list[Path]: Image files ordered by natural_sort_key()

    Raises:
        FileNotFoundError: If no inputs are given, a given file/directory does
                           not exist, or no supported images are found
        ValueError: If a given file's extension is not one of
                    .jpg, .jpeg, .png, .gif
    """
    if not inputs:
        raise FileNotFoundError(NO_IMAGES_MESSAGE)

    paths = []

    for item in inputs:
        p = Path(item)

        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")

        if p.is_dir():
            for child in sorted(p.iterdir()):
                if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                    paths.append(child)
        else:
            if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise ValueError(
                    f"Unsupported image format: {p.name} "
                    "(expected .jpg, .jpeg, .png, or .gif)"
                )
            paths.append(p)

    if not paths:
        raise FileNotFoundError(
            "No supported image files (.jpg, .jpeg, .png, .gif) found"
        )

    paths.sort(key=natural_sort_key)

    return paths


# ==============================================================================
# FUNCTION: _scale_up_for_ocr - Upscale low-resolution images before OCR
# ==============================================================================

# Below this width, small print (e.g. multi-column magazine/newspaper scans)
# tends to have individual glyphs only a few pixels wide, which makes
# Tesseract lose the gap between words and glue them together
# ("researchersbehind"). Upscaling first consistently fixes this.
_OCR_TARGET_WIDTH = 6000
_OCR_MAX_UPSCALE_FACTOR = 4.0


def _scale_up_for_ocr(image):
    """
    Upscales an image so Tesseract has enough resolution to keep adjacent
    words apart, if it isn't already large enough.

    Images already at or above the target width are returned unchanged (OCR
    on an already-high-resolution scan doesn't need it, and upscaling it
    further would just slow things down). Very small images are capped at
    _OCR_MAX_UPSCALE_FACTOR so a tiny icon-sized input isn't blown up to the
    point of producing meaningless noise.

    Args:
        image (PIL.Image.Image): Source image (already RGB)

    Returns:
        PIL.Image.Image: The original image, or an upscaled copy
    """
    if image.width >= _OCR_TARGET_WIDTH:
        return image

    factor = min(_OCR_TARGET_WIDTH / image.width, _OCR_MAX_UPSCALE_FACTOR)
    if factor <= 1.0:
        return image

    new_size = (round(image.width * factor), round(image.height * factor))
    return image.resize(new_size, Image.LANCZOS)


# ==============================================================================
# FUNCTION: extract_text_from_image - Extract text from one image via Tesseract
# ==============================================================================

def extract_text_from_image(image_path, lang='eng+ita'):
    """
    Uses local Tesseract OCR to extract text from a single image file.

    Args:
        image_path (str or Path): Path to the image file
        lang (str): Tesseract language(s) to use, e.g. 'eng+ita'

    Returns:
        str: Extracted text, or empty string if no text found
    """
    configure_tesseract()

    with Image.open(image_path) as image:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image = _scale_up_for_ocr(image)
        text = pytesseract.image_to_string(image, lang=lang)

    return text


# ==============================================================================
# FUNCTION: text_to_paragraphs - Group raw OCR text into paragraphs
# ==============================================================================

def text_to_paragraphs(raw_text):
    """
    Groups raw OCR output into paragraphs, treating blank lines as paragraph
    breaks and joining wrapped lines within a paragraph with a single space.

    Args:
        raw_text (str): Raw text returned by Tesseract

    Returns:
        list[str]: Paragraphs, in order
    """
    if not raw_text.strip():
        return []

    paragraphs = []
    current_para = ""

    for line in raw_text.split('\n'):
        stripped = line.strip()

        if not stripped:
            if current_para:
                paragraphs.append(current_para)
                current_para = ""
        else:
            current_para += (" " if current_para else "") + stripped

    if current_para:
        paragraphs.append(current_para)

    return paragraphs


# ==============================================================================
# FUNCTION: looks_like_ocr_noise - Detect a paragraph that is just OCR garbage
# ==============================================================================

def looks_like_ocr_noise(paragraph):
    """
    Flags a short paragraph as OCR noise rather than real text.

    Magazine/newspaper layouts often print a tiny photo credit rotated 90
    degrees along the edge of a photo (e.g. "...GETTY IMAGES"). When that
    sits beside a text column, Tesseract's automatic layout analysis
    sometimes slices a fragment of it into the column's own reading order,
    producing a short run of near-meaningless tokens such as "A" or
    "A o k/ u 070,". Such a run is easy to tell apart from real prose (even a
    short heading like "Brain fuel"): almost every "word" in it is one or two
    characters long, which normal text - including short headings - does not
    look like.

    Args:
        paragraph (str): A single paragraph of OCR'd text

    Returns:
        bool: True if the paragraph looks like injected OCR noise
    """
    tokens = paragraph.split()

    if not tokens or len(paragraph) > 30:
        return False

    short_tokens = sum(1 for t in tokens if len(t.strip('.,:;!?')) <= 2)

    return (short_tokens / len(tokens)) >= 0.8


# ==============================================================================
# FUNCTION: strip_trailing_end_marker - Remove a stray OCR'd end-of-article glyph
# ==============================================================================

def strip_trailing_end_marker(text):
    """
    Strips a stray single-letter token sometimes left at the very end of the
    document's OCR text. Many printed sources (magazines, newspapers) mark
    the end of an article with a small solid square/bullet glyph; Tesseract
    can misread that glyph as an isolated capital letter (typically 'I')
    sitting right after the closing sentence punctuation, e.g.
    "...cognitive sparkle. I".

    Only matches at the very end of the text, and only immediately after
    sentence-ending punctuation, so a legitimate trailing initial or
    abbreviation elsewhere in the text is never touched.

    Args:
        text (str): Combined Markdown text

    Returns:
        str: The text with any trailing stray letter removed
    """
    return re.sub(r'(?<=[.!?])\s+[A-Za-z]\s*$', '', text)


# ==============================================================================
# FUNCTION: images_to_markdown - OCR a list of images into one Markdown string
# ==============================================================================

def images_to_markdown(image_paths, lang='eng+ita'):
    """
    Runs OCR on each image in order and assembles the results into a single
    Markdown string, one section per image, separated by a horizontal rule.

    Args:
        image_paths (list[Path]): Image files, already in the desired order
        lang (str): Tesseract language(s) to use, e.g. 'eng+ita'

    Returns:
        str: Combined Markdown text
    """
    sections = []

    for image_path in image_paths:
        print(f"  Processing {image_path.name}...")
        raw_text = extract_text_from_image(image_path, lang=lang)
        paragraphs = text_to_paragraphs(raw_text)
        paragraphs = [p for p in paragraphs if not looks_like_ocr_noise(p)]
        if paragraphs:
            sections.append('\n\n'.join(paragraphs))

    markdown_text = '\n\n---\n\n'.join(sections)

    return strip_trailing_end_marker(markdown_text)


# ==============================================================================
# FUNCTION: confirm_overwrite - Ask before overwriting an existing output file
# ==============================================================================

def confirm_overwrite(path):
    """
    Asks the user whether an existing output file should be overwritten.
    Defaults to No: pressing Enter with no input, or anything other than an
    explicit "s"/"si"/"sì" (case-insensitive), declines the overwrite.

    Args:
        path (Path): The existing file that would be overwritten

    Returns:
        bool: True if the user confirmed the overwrite
    """
    answer = input(
        f"Esiste un altro file '{path.name}' con lo stesso nome. "
        "Vuoi sovrascriverlo? (S/N) [N]: "
    )
    return answer.strip().lower() in ('s', 'si', 'sì')


# ==============================================================================
# FUNCTION: image_to_md - Main function to convert image(s) to Markdown
# ==============================================================================

def image_to_md(inputs, output_path=None, output_dir=None, lang='eng+ita'):
    """
    Main function to convert one or more images to a single Markdown file.

    Args:
        inputs (list[str or Path]): Image file paths and/or directory paths
        output_path (str or None): Optional custom output file path.
                                    If None, derived from the input.
        output_dir (str or None): Directory for output Markdown file
        lang (str): Tesseract language(s) to use, e.g. 'eng+ita'

    Returns:
        str or None: Path to the generated Markdown file, or None if the
                     user declined to overwrite an existing output file

    Raises:
        FileNotFoundError: If an input file/directory doesn't exist, or no
                            supported images are found
        ValueError: If an input file has an unsupported extension
    """
    image_paths = collect_image_paths(inputs)

    print(f"✓ Found {len(image_paths)} image(s) to process")
    for i, p in enumerate(image_paths, start=1):
        print(f"  {i}. {p.name}")

    if output_path is None:
        first_input = Path(inputs[0])
        if first_input.is_dir():
            output_path = first_input / f"{first_input.name}.md"
        else:
            output_path = image_paths[0].with_suffix('.md')

    output_path = Path(output_path)

    if output_dir is not None:
        output_dir_path = Path(output_dir).resolve()
        output_path = output_dir_path / output_path.name

    if output_path.exists() and not confirm_overwrite(output_path):
        print(f"\nOperazione annullata: '{output_path}' non è stato sovrascritto.")
        return None

    try:
        markdown_text = images_to_markdown(image_paths, lang=lang)

        if not markdown_text.strip():
            print("Warning: no text was extracted from the provided image(s)", file=sys.stderr)

        output_path.write_text(markdown_text, encoding='utf-8')

        print(f"\n✓ Conversion completed successfully!")
        print(f"  Images:     {len(image_paths)}")
        print(f"  Output:     {output_path}")
        print(f"  Characters: {len(markdown_text)}")

        return str(output_path)

    except Exception as e:
        print(f"\n✗ Error during conversion: {e}", file=sys.stderr)
        raise


# ==============================================================================
# FUNCTION: main - Command-line interface entry point for Image to Markdown converter
# ==============================================================================

def main():
    """
    Command-line interface for the Image to Markdown converter.

    Usage examples:
        python image_to_md.py page.jpg
        python image_to_md.py 1_page.jpg 2_page.jpg 3_page.jpg
        python image_to_md.py .\\scans\\ -o document.md
        python image_to_md.py page.png --lang eng

    Notes:
        - Multiple images are treated as pages of one document and combined,
          in order, into a single Markdown file
        - Ordering is derived from any number embedded in each filename
          (prefix or suffix), not from the order given on the command line
        - A directory may be passed instead of individual files; every
          supported image inside it (.jpg, .jpeg, .png, .gif) is used
        - Requires the Tesseract build in utilities/tesseract/
    """
    parser = argparse.ArgumentParser(
        description='Convert one or more images (JPEG, PNG, GIF) to Markdown via local Tesseract OCR',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_to_md.py page.jpg                          # Single image
  python image_to_md.py 1_page.jpg 2_page.jpg 3_page.jpg   # Multi-page, ordered by filename number
  python image_to_md.py .\\scans\\ -o document.md            # All images in a directory
  python image_to_md.py page.png --lang eng                # Force English-only OCR

Notes:
  - No API key or internet connection required - everything runs locally
  - Requires the Tesseract build (tesseract.exe + tessdata/) in utilities/tesseract/
"""
    )

    parser.add_argument('images', nargs='*',
                         help='Image file(s) (.jpg, .jpeg, .png, .gif) and/or a directory containing them')
    parser.add_argument('-o', '--output', help='Path for the Markdown output file')
    parser.add_argument('--output-dir', dest='output_dir', default=None,
                         help='Directory for output Markdown file')
    parser.add_argument('--lang', default='eng+ita',
                         help="Tesseract language(s) to use, e.g. 'eng', 'ita', 'eng+ita' (default: eng+ita)")

    args = parser.parse_args()

    try:
        image_to_md(
            inputs=args.images,
            output_path=args.output,
            output_dir=args.output_dir,
            lang=args.lang,
        )
    except (FileNotFoundError, ValueError) as e:
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
