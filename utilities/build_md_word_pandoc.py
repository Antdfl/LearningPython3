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
"""
import shutil
import subprocess
import sys
from pathlib import Path

from md_shared import strip_md_toc

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REFERENCE_DOCX = SCRIPT_DIR / 'reference.docx'


def main():
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
