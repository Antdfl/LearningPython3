#!/usr/bin/env python3
"""
utilities/build_md_word_pandoc.py

# Purpose: Thin wrapper around the Pandoc CLI (https://pandoc.org) that
# converts a Markdown (.md) file - together with any local images it
# references - into a Word (.docx) document styled by a reference.docx
# template.
#
# Unlike build_md_toc.py's hand-rolled DOCX generator (which does not embed
# images at all), this script delegates all Markdown parsing, list/table
# handling, image embedding and TOC generation to Pandoc itself. Requires
# Pandoc installed and on PATH - it is an external binary, not a pip
# package.

# Audience Note for Junior Programmers:
# This script deliberately does NOT reimplement Markdown/DOCX handling the
# way build_md_toc.py does. Pandoc already solves image embedding, list/table
# formatting and TOC generation correctly, so calling out to it as a
# subprocess avoids reinventing that logic - the tradeoff is an external
# binary dependency instead of a pure pip package, so Pandoc must be
# installed separately and be on PATH before this script can run.

# Functionality Overview:
# main() does the following, in order:
# 1. Locates the pandoc executable via PATH (shutil.which); exits if missing.
# 2. Resolves the source .md path and the reference.docx template path from
#    command-line arguments, falling back to defaults relative to this
#    script's folder.
# 3. Prompts for an output filename and, if that file already exists, asks
#    for overwrite confirmation before continuing.
# 4. Reads the source file as UTF-8, falling back to cp1252 if decoding
#    fails.
# 5. Strips any existing hand-written TOC from the Markdown before Pandoc
#    generates its own (--toc), to avoid a duplicated TOC.
# 6. Writes the stripped Markdown to a temporary file in the SAME folder as
#    the source, so relative image paths keep resolving without extra
#    bookkeeping.
# 7. Runs pandoc as a subprocess (--toc, --number-sections, --reference-doc)
#    with its working directory pinned to the source folder, so Pandoc's own
#    relative image-path resolution matches the source file's location.
# 8. Deletes the temporary file in a finally block regardless of outcome.
# 9. Reports Pandoc errors (and any non-fatal warnings on stderr) before
#    printing the generated output path.

# Dependencies:
# - Pandoc: external CLI binary (https://pandoc.org), must be installed and
#   on PATH - NOT installed via pip.
# - md_shared.strip_md_toc: local helper module used to remove an existing
#   hand-written TOC before conversion.
# - reference.docx: a Word template file expected in this script's own
#   folder (or an explicit path passed as the second command-line argument),
#   used by Pandoc to style the generated document.
"""
import shutil
import subprocess
import sys
from pathlib import Path

from md_shared import strip_md_toc

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REFERENCE_DOCX = SCRIPT_DIR / 'reference.docx'


def main():
    """
    This function acts as a wrapper around the Pandoc CLI utility to convert Markdown (.md) files into professional Word (.docx) documents. It handles complex tasks like generating Table of Contents, embedding images, and styling the output using a specified reference DOCX template. The script orchestrates the entire conversion process by managing file paths, calling Pandoc with specific flags, and handling potential errors during the external execution.

    Parameters:
        None (The function accepts no explicit parameters).

    Returns:
        None (The function returns nothing; success/failure is communicated via exit codes or print statements).
    """
    pandoc_exe = shutil.which('pandoc')
    if not pandoc_exe:
        print("Pandoc non trovato nel PATH. Installalo da https://pandoc.org/installing.html")
        sys.exit(1)

    arg = sys.argv[1] if len(sys.argv) > 1 else 'text_to_convert.md'
    src = Path(arg)
    if not src.is_absolute():
        src = SCRIPT_DIR / src
    if not src.exists():
        print(f"File non trovato: {src}")
        sys.exit(1)

    ref_arg = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_REFERENCE_DOCX)
    reference_docx = Path(ref_arg)
    if not reference_docx.is_absolute():
        reference_docx = SCRIPT_DIR / reference_docx
    if not reference_docx.exists():
        print(f"reference.docx non trovato: {reference_docx}")
        sys.exit(1)

    default_stem = src.with_suffix('').name
    output_name = input(f"\nNome base del file di output [{default_stem}]: ").strip()
    stem = Path(output_name) if output_name else src.with_suffix('')
    if not stem.is_absolute():
        stem = SCRIPT_DIR / stem
    output_path = stem.with_suffix('.docx')

    if output_path.exists():
        confirmation = input(
            f"\n{output_path.name} esiste gia'. Sovrascrivere? (S/N) [Default N]: "
        ).strip().upper()
        if confirmation != 'S':
            print("\nOk allora non devo fare nulla. Uscita dal programma.")
            sys.exit(0)

    print("\nLettura del file Markdown in corso...")
    try:
        md_text = src.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:
        print("Attenzione: il file non e' UTF-8, provo con la codifica Windows-1252 (cp1252)...")
        md_text = src.read_text(encoding='cp1252')

    # Pandoc builds its own TOC below (--toc); a hand-written one in the
    # source would just be duplicated, same reasoning as in build_md_toc.py.
    md_text = strip_md_toc(md_text)

    # Written into the SAME folder as the source .md so relative image
    # paths (![alt](images/foo.png)) keep resolving exactly as they did in
    # the original file, with no extra --resource-path bookkeeping.
    tmp_md = src.parent / f".{src.stem}.pandoc_tmp.md"
    tmp_md.write_text(md_text, encoding='utf-8')

    try:
        print("Conversione con Pandoc in corso...")
        result = subprocess.run(
            [
                pandoc_exe,
                str(tmp_md),
                '--from', 'markdown',
                '--to', 'docx',
                '--toc', '--toc-depth=3',
                '--number-sections',
                '--reference-doc', str(reference_docx),
                '-o', str(output_path),
            ],
            # Pandoc resolves relative image paths (![alt](images/pic.png))
            # against its OWN working directory, not against the input
            # file's location - so cwd must be pinned to the .md's folder,
            # otherwise images resolve fine only if the script happens to be
            # launched from that same folder.
            cwd=str(src.parent),
            capture_output=True, text=True,
        )
    finally:
        tmp_md.unlink(missing_ok=True)

    if result.returncode != 0:
        print("Errore nella conversione con Pandoc:")
        print(result.stderr)
        sys.exit(1)

    if result.stderr:
        # Pandoc prints non-fatal warnings (e.g. unresolved reference links)
        # to stderr even on a successful (returncode 0) conversion.
        print(result.stderr)

    print(f"\nGenerato: {output_path}")


if __name__ == "__main__":
    main()
