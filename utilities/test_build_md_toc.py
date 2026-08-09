#!/usr/bin/env python3
"""
utilities/test_build_md_toc.py

Minimal automated test suite for build_md_toc.py, using only the
standard library (unittest) so it runs without extra dependencies.

Run with:
    .venv\\Scripts\\python.exe -m unittest utilities.test_build_md_toc -v
or, from inside utilities/:
    ..\\.venv\\Scripts\\python.exe -m unittest test_build_md_toc -v
"""
import unittest

import build_md_toc as m


class TestStripFrontmatter(unittest.TestCase):
    def test_removes_frontmatter_block(self):
        text = "---\ntitle: Hello\n---\nBody text\nMore body"
        self.assertEqual(m.strip_frontmatter(text), "Body text\nMore body")

    def test_no_frontmatter_returns_unchanged(self):
        text = "# Title\nJust body content, no front matter."
        self.assertEqual(m.strip_frontmatter(text), text)


class TestExtractFrontmatterFields(unittest.TestCase):
    def test_extracts_title_and_subtitle(self):
        text = '---\ntitle: "My Title"\nsubtitle: A subtitle\n---\nBody'
        fields = m.extract_frontmatter_fields(text)
        self.assertEqual(fields.get('title'), 'My Title')
        self.assertEqual(fields.get('subtitle'), 'A subtitle')

    def test_no_frontmatter_returns_empty_dict(self):
        self.assertEqual(m.extract_frontmatter_fields("# Title\nBody"), {})


class TestStripMdToc(unittest.TestCase):
    def test_removes_heading_guarded_toc(self):
        text = (
            "# Document Title\n"
            "## Contenuto\n"
            "- [Section One](#section-one)\n"
            "- [Section Two](#section-two)\n"
            "\n"
            "## Section One\n"
            "Real content here.\n"
        )
        result = m.strip_md_toc(text)
        self.assertNotIn("Contenuto", result)
        self.assertNotIn("[Section One](#section-one)", result)
        self.assertIn("Real content here.", result)

    def test_no_toc_returns_unchanged(self):
        text = "# Document Title\n\nJust a normal paragraph, no TOC.\n"
        self.assertEqual(m.strip_md_toc(text), text)


class TestSlugify(unittest.TestCase):
    def test_basic_text(self):
        self.assertEqual(m.slugify("Ciao Mondo"), "ciao-mondo")

    def test_strips_accents_and_punctuation(self):
        self.assertEqual(m.slugify("Perché è così?"), "perche-e-cosi")

    def test_empty_text_falls_back_to_section(self):
        self.assertEqual(m.slugify(""), "section")


class TestConvertToHtml(unittest.TestCase):
    def test_converts_heading_and_paragraph(self):
        html = m.convert_to_html("# Title\n\nSome paragraph.")
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<p>Some paragraph.</p>", html)


class TestMainGuard(unittest.TestCase):
    def test_main_is_defined_but_not_run_on_import(self):
        # Importing the module must not trigger the interactive menu
        # (this test file itself proves that: if it did, importing
        # build_md_toc above would already have raised EOFError).
        self.assertTrue(callable(m.main))


if __name__ == "__main__":
    unittest.main()
