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
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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


class TestReplaceUnsupportedGlyphs(unittest.TestCase):
    # Sans-serif bold "Test" and italic "A", from the Mathematical
    # Alphanumeric Symbols block - the Unicode "fake bold/italic" that
    # LinkedIn text generators produce.
    FAKE_BOLD_TEST = "\U0001D5E7\U0001D5F2\U0001D600\U0001D601"
    FAKE_ITALIC_A = "\U0001D434"

    def test_emoji_at_line_start_leaves_no_leading_space(self):
        result = m.replace_unsupported_glyphs("✅ Capture the change.")
        self.assertEqual(result, "Capture the change.")

    def test_emoji_at_line_end_leaves_no_trailing_space(self):
        result = m.replace_unsupported_glyphs("The query changes shape. \U0001F504")
        self.assertEqual(result, "The query changes shape.")

    def test_emoji_with_variation_selector_is_removed(self):
        result = m.replace_unsupported_glyphs("⚠️ Warning: read this.")
        self.assertEqual(result, "Warning: read this.")

    def test_fake_bold_becomes_real_markdown_bold(self):
        result = m.replace_unsupported_glyphs(self.FAKE_BOLD_TEST + ": the rest")
        self.assertEqual(result, "**Test**: the rest")

    def test_fake_italic_becomes_real_markdown_italic(self):
        self.assertEqual(m.replace_unsupported_glyphs(self.FAKE_ITALIC_A), "*A*")

    def test_styled_phrase_becomes_one_emphasis_span(self):
        # Spaces between styled words stay inside the run, so the phrase gets
        # one pair of markers instead of one pair per word.
        text = self.FAKE_BOLD_TEST + " " + self.FAKE_BOLD_TEST
        self.assertEqual(m.replace_unsupported_glyphs(text), "**Test Test**")

    def test_no_emphasis_markers_inside_fenced_code_block(self):
        # Markdown is not parsed inside a fence, so '**' would be printed
        # literally; the letters must still be un-styled, though.
        text = "```\n\U0001F4CC " + self.FAKE_BOLD_TEST + "\n```"
        self.assertEqual(m.replace_unsupported_glyphs(text), "```\nTest\n```")

    def test_indentation_inside_fence_is_preserved(self):
        text = "```\n    \U0001F680 indented code\n```"
        self.assertEqual(m.replace_unsupported_glyphs(text), "```\n    indented code\n```")

    def test_operators_and_arrows_are_left_alone(self):
        text = "DB→front-end, a ≈ b, x ≠ y, n ≤ 10"
        self.assertEqual(m.replace_unsupported_glyphs(text), text)

    def test_plain_text_is_returned_unchanged(self):
        text = "# Titolo\n\nUn paragrafo **gia' in grassetto**, con due spazi  \nfinali."
        self.assertEqual(m.replace_unsupported_glyphs(text), text)


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
