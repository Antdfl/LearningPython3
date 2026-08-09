#!/usr/bin/env python3
"""
utilities/test_transcribe_video.py

Minimal automated test suite for transcribe_video.py, using only the
standard library (unittest) so it runs without extra dependencies.

extract_audio_from_video() and transcribe_audio() call out to a real
ffmpeg binary and the Google Web Speech API respectively, so they are
only exercised here through their no-dependency failure branch
(ffmpeg missing), via mocking - not with a real video/audio file or a
live network call.

Run with:
    .venv\\Scripts\\python.exe -m unittest utilities.test_transcribe_video -v
or, from inside utilities/:
    ..\\.venv\\Scripts\\python.exe -m unittest test_transcribe_video -v
"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import transcribe_video as m


class TestSaveTranscription(unittest.TestCase):
    def test_writes_text_to_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "out.txt")
            m.save_transcription("Ciao mondo", output_path)
            with open(output_path, encoding="utf-8") as f:
                self.assertEqual(f.read(), "Ciao mondo")

    def test_missing_directory_raises_and_reports(self):
        missing_path = os.path.join(tempfile.gettempdir(), "no_such_dir_xyz", "out.txt")
        with self.assertRaises(FileNotFoundError):
            m.save_transcription("text", missing_path)


class TestExtractAudioFromVideo(unittest.TestCase):
    def test_returns_none_when_ffmpeg_not_found_anywhere(self):
        # Neither the venv's ffmpeg.exe nor a system ffmpeg on PATH exists,
        # so the function should give up cleanly and return None (not raise).
        with patch("transcribe_video.os.path.exists", return_value=False), \
             patch("transcribe_video.subprocess.run", side_effect=FileNotFoundError):
            result = m.extract_audio_from_video("some_video.mp4")
        self.assertIsNone(result)


class TestMain(unittest.TestCase):
    def test_no_arguments_prints_usage_and_returns(self):
        buf = io.StringIO()
        with patch.object(sys, "argv", ["transcribe_video.py"]), redirect_stdout(buf):
            m.main()  # must not raise, must not attempt any transcription
        self.assertIn("Usage:", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
