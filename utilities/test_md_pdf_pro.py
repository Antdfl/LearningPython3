#!/usr/bin/env python3
"""
utilities/test_md_pdf_pro.py

Tests for the pure (browser-free) parts of md_pdf_pro.py, using only unittest.

Run from inside utilities/:
    ..\\.venv\\Scripts\\python.exe -m unittest test_md_pdf_pro -v
"""
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import md_pdf_pro as pro


class TestPrepareHeadings(unittest.TestCase):
    def test_wraps_headings_and_collects_entries(self):
        body, entries = pro.prepare_headings("<h1>Uno</h1><p>x</p><h2>Due</h2>")
        self.assertEqual([e['level'] for e in entries], [1, 2])
        self.assertIn('<h1 id="uno">Uno</h1>', body)
        self.assertIn('class="back" href="#toc"', body)

    def test_duplicate_titles_get_unique_ids(self):
        _, entries = pro.prepare_headings("<h2>Esito</h2><h2>Esito</h2>")
        self.assertEqual([e['id'] for e in entries], ["esito", "esito-1"])

    def test_deep_headings_have_no_back_link(self):
        body, _ = pro.prepare_headings("<h4>Piccolo</h4>")
        self.assertNotIn("back", body)


class TestBuildDocument(unittest.TestCase):
    def setUp(self):
        self.body, self.entries = pro.prepare_headings("<h1>Uno</h1><h2>Due</h2><h3>Tre</h3>")

    def test_cover_has_meta_rows_and_pdf_row(self):
        doc = pro.build_document(self.body, self.entries, "Titolo", "Sotto",
                                 {"autore": "Ada"}, "Etichetta", "file.md")
        self.assertIn('class="title">Titolo', doc)
        self.assertIn('<td class="k">autore</td><td>Ada</td>', doc)
        self.assertIn("dal file file.md", doc)

    def test_toc_lists_only_levels_up_to_max(self):
        doc = pro.build_document(self.body, self.entries, "T", None, {}, None,
                                 None, pages=[3, 3, 4])
        self.assertIn('class="toc-row l1"', doc)
        self.assertIn('class="toc-row l2"', doc)
        self.assertNotIn('class="toc-row l3"', doc)

    def test_no_title_means_no_cover(self):
        doc = pro.build_document(self.body, self.entries, None, None, {}, None, None)
        self.assertNotIn('class="cover"', doc)


def _browser_available():
    if not pro.PRO_PDF_AVAILABLE:
        return False
    try:
        with pro.sync_playwright() as p:
            pro._launch(p).close()
        return True
    except Exception:
        return False


@unittest.skipUnless(_browser_available(), "Playwright + Chrome/Edge non disponibili")
class TestRenderPdfIntegration(unittest.TestCase):
    """Real end-to-end render: needs Chrome or Edge, skipped otherwise."""

    BODY = (
        "<h1>Uno</h1><p>testo</p>"
        "<table><thead><tr><th>Data</th><th>Nota</th></tr></thead>"
        "<tbody><tr><td>24/09/2026</td><td>x</td></tr></tbody></table>"
        "<h2>Sotto</h2>" + "<p>riempitivo</p>" * 120 +
        "<h1>Due</h1><h3>Terzo</h3><h4>Quarto</h4>"
    )

    def _render(self, **kwargs):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "o.pdf"
        self.assertTrue(pro.render_pdf(self.BODY, out, **kwargs))
        return pro.PdfReader(io.BytesIO(out.read_bytes()))

    def test_cover_toc_and_bookmarks(self):
        reader = self._render(title="Titolo", subtitle="Sotto", meta={"autore": "Ada"},
                              source_name="f.md", footer_left="Titolo · versione 1")
        # all five headings (h1-h4) become bookmarks, nested
        flat = []
        def walk(items):
            for it in items:
                walk(it) if isinstance(it, list) else flat.append(it["/Title"])
        walk(reader.outline)
        self.assertEqual(flat, ["Uno", "Sotto", "Due", "Terzo", "Quarto"])
        self.assertIn("Titolo", reader.pages[0].extract_text())
        self.assertIn("pagina 1 di", reader.pages[0].extract_text())

    def test_toc_numbers_match_real_pages(self):
        reader = self._render(title="Titolo")
        toc = reader.pages[1].extract_text()
        # heading "Due" starts a new page: its TOC number must be the page
        # where the heading text is really found.
        real = next(i + 1 for i, pg in enumerate(reader.pages)
                    if i > 1 and pg.extract_text().splitlines()[0].startswith("Due"))
        line = next(l for l in toc.splitlines() if l.startswith("Due"))
        self.assertTrue(line.rstrip().endswith(str(real)), (line, real))

    def test_no_title_no_cover_and_table_dates_not_split(self):
        reader = self._render()
        self.assertNotIn("Generato il", reader.pages[0].extract_text())
        text = "".join(pg.extract_text() for pg in reader.pages)
        self.assertIn("24/09/2026", text)  # not wrapped as "24/09/20 26"


if __name__ == "__main__":
    unittest.main()
