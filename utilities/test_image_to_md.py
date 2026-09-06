#!/usr/bin/env python3
"""
utilities/test_image_to_md.py

Minimal automated test suite for image_to_md.py, using only the standard
library (unittest) so it runs without extra dependencies.

extract_text_from_image() calls out to a real Tesseract binary, so it is
mocked out here rather than exercised against a real image and OCR engine.

Run with:
    .venv\\Scripts\\python.exe -m unittest utilities.test_image_to_md -v
or, from inside utilities/:
    ..\\.venv\\Scripts\\python.exe -m unittest test_image_to_md -v
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import image_to_md as m
from PIL import Image


class TestNaturalSortKey(unittest.TestCase):
    def test_orders_numeric_prefix(self):
        names = ["10_page.jpg", "2_page.jpg", "1_page.jpg"]
        self.assertEqual(
            sorted(names, key=m.natural_sort_key),
            ["1_page.jpg", "2_page.jpg", "10_page.jpg"],
        )

    def test_orders_numeric_suffix(self):
        names = ["file_10.png", "file_2.png", "file_1.png"]
        self.assertEqual(
            sorted(names, key=m.natural_sort_key),
            ["file_1.png", "file_2.png", "file_10.png"],
        )

    def test_falls_back_to_alphabetical_without_digits(self):
        names = ["banana.jpg", "apple.jpg"]
        self.assertEqual(
            sorted(names, key=m.natural_sort_key),
            ["apple.jpg", "banana.jpg"],
        )


class TestCollectImagePaths(unittest.TestCase):
    def test_collects_and_orders_files_from_directory(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            for name in ["2_page.png", "1_page.jpg", "notes.txt"]:
                (tmp_path / name).write_bytes(b"")

            result = m.collect_image_paths([tmp_dir])

            self.assertEqual([p.name for p in result], ["1_page.jpg", "2_page.png"])

    def test_orders_explicit_file_list_by_filename_not_argument_order(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file_b = tmp_path / "2_page.jpg"
            file_a = tmp_path / "1_page.jpg"
            file_b.write_bytes(b"")
            file_a.write_bytes(b"")

            result = m.collect_image_paths([str(file_b), str(file_a)])

            self.assertEqual([p.name for p in result], ["1_page.jpg", "2_page.jpg"])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            m.collect_image_paths(["no_such_file.jpg"])

    def test_no_inputs_raises_with_italian_message(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            m.collect_image_paths([])
        self.assertEqual(str(ctx.exception), m.NO_IMAGES_MESSAGE)

    def test_unsupported_extension_raises(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            bad_file = Path(tmp_dir) / "page.bmp"
            bad_file.write_bytes(b"")
            with self.assertRaises(ValueError):
                m.collect_image_paths([str(bad_file)])

    def test_directory_with_no_supported_images_raises(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            (Path(tmp_dir) / "notes.txt").write_bytes(b"")
            with self.assertRaises(FileNotFoundError):
                m.collect_image_paths([tmp_dir])


class TestScaleUpForOcr(unittest.TestCase):
    def test_upscales_small_image_to_target_width(self):
        small = Image.new('RGB', (1923, 1228))
        result = m._scale_up_for_ocr(small)
        self.assertEqual(result.width, m._OCR_TARGET_WIDTH)
        self.assertEqual(result.height, round(1228 * (m._OCR_TARGET_WIDTH / 1923)))

    def test_leaves_already_large_image_unchanged(self):
        large = Image.new('RGB', (m._OCR_TARGET_WIDTH, 1000))
        result = m._scale_up_for_ocr(large)
        self.assertEqual(result.size, large.size)

    def test_caps_upscale_factor_for_tiny_image(self):
        tiny = Image.new('RGB', (100, 50))
        result = m._scale_up_for_ocr(tiny)
        self.assertEqual(result.size, (400, 200))


class TestLooksLikeOcrNoise(unittest.TestCase):
    def test_flags_single_letter_paragraph(self):
        self.assertTrue(m.looks_like_ocr_noise("A"))

    def test_flags_short_run_of_garbled_tokens(self):
        self.assertTrue(m.looks_like_ocr_noise("A o k/ u 070,"))

    def test_does_not_flag_short_real_heading(self):
        self.assertFalse(m.looks_like_ocr_noise("Brain fuel"))
        self.assertFalse(m.looks_like_ocr_noise("Glass half full"))

    def test_does_not_flag_short_real_sentence_fragment(self):
        self.assertFalse(m.looks_like_ocr_noise("Is drinking 2 litres of water"))

    def test_does_not_flag_long_paragraph(self):
        long_text = "A o k/ u 070, " * 5
        self.assertFalse(m.looks_like_ocr_noise(long_text))


class TestStripTrailingEndMarker(unittest.TestCase):
    def test_strips_stray_letter_after_final_punctuation(self):
        text = "hope of recovering a little of that cognitive sparkle. I"
        self.assertEqual(
            m.strip_trailing_end_marker(text),
            "hope of recovering a little of that cognitive sparkle.",
        )

    def test_leaves_normal_ending_untouched(self):
        text = "This is a normal sentence."
        self.assertEqual(m.strip_trailing_end_marker(text), text)

    def test_leaves_trailing_initial_with_following_period_untouched(self):
        text = "Yours sincerely, J."
        self.assertEqual(m.strip_trailing_end_marker(text), text)


class TestTextToParagraphs(unittest.TestCase):
    def test_groups_lines_into_paragraphs_on_blank_lines(self):
        raw = "First line\nstill first\n\nSecond paragraph\n"
        self.assertEqual(
            m.text_to_paragraphs(raw),
            ["First line still first", "Second paragraph"],
        )

    def test_empty_text_returns_no_paragraphs(self):
        self.assertEqual(m.text_to_paragraphs("   \n  \n"), [])


class TestImagesToMarkdown(unittest.TestCase):
    def test_joins_pages_with_horizontal_rule_in_order(self):
        fake_paths = [Path("1_page.jpg"), Path("2_page.jpg")]

        with patch.object(m, "extract_text_from_image", side_effect=["Page one", "Page two"]):
            result = m.images_to_markdown(fake_paths)

        self.assertEqual(result, "Page one\n\n---\n\nPage two")

    def test_skips_pages_with_no_extracted_text(self):
        fake_paths = [Path("1_page.jpg"), Path("2_page.jpg")]

        with patch.object(m, "extract_text_from_image", side_effect=["", "Only page"]):
            result = m.images_to_markdown(fake_paths)

        self.assertEqual(result, "Only page")


class TestImageToMd(unittest.TestCase):
    def test_writes_combined_markdown_and_derives_output_path(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            (tmp_path / "1_page.jpg").write_bytes(b"")
            (tmp_path / "2_page.jpg").write_bytes(b"")

            with patch.object(m, "extract_text_from_image", side_effect=["First", "Second"]):
                output_path = m.image_to_md([str(tmp_path / "1_page.jpg"), str(tmp_path / "2_page.jpg")])

            self.assertEqual(output_path, str(tmp_path / "1_page.md"))
            self.assertEqual(Path(output_path).read_text(encoding="utf-8"), "First\n\n---\n\nSecond")

    def test_prompts_and_overwrites_existing_output_on_yes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            image_file = tmp_path / "1_page.jpg"
            image_file.write_bytes(b"")
            output_file = tmp_path / "1_page.md"
            output_file.write_text("old content", encoding="utf-8")

            with patch.object(m, "extract_text_from_image", return_value="New content"), \
                 patch("builtins.input", return_value="s") as mock_input:
                output_path = m.image_to_md([str(image_file)])

            mock_input.assert_called_once()
            self.assertEqual(output_path, str(output_file))
            self.assertEqual(output_file.read_text(encoding="utf-8"), "New content")

    def test_prompts_and_keeps_existing_output_on_default_no(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            image_file = tmp_path / "1_page.jpg"
            image_file.write_bytes(b"")
            output_file = tmp_path / "1_page.md"
            output_file.write_text("old content", encoding="utf-8")

            with patch.object(m, "extract_text_from_image", return_value="New content"), \
                 patch("builtins.input", return_value=""):
                result = m.image_to_md([str(image_file)])

            self.assertIsNone(result)
            self.assertEqual(output_file.read_text(encoding="utf-8"), "old content")


class TestConfirmOverwrite(unittest.TestCase):
    def test_accepts_s(self):
        with patch("builtins.input", return_value="S"):
            self.assertTrue(m.confirm_overwrite(Path("out.md")))

    def test_declines_on_empty_input(self):
        with patch("builtins.input", return_value=""):
            self.assertFalse(m.confirm_overwrite(Path("out.md")))

    def test_declines_on_anything_else(self):
        with patch("builtins.input", return_value="maybe"):
            self.assertFalse(m.confirm_overwrite(Path("out.md")))


if __name__ == "__main__":
    unittest.main()
