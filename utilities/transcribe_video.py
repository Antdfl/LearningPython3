#!/usr/bin/env python3
"""
========================================
Video Transcription Tool
========================================

This Python script converts audio/video files into text transcripts using
speech recognition technology. Long audio is split into chunks and
transcribed one at a time, printing progress as "chunk N/total (X%)".

Author: AI Assistant
Language: Italian by default, configurable via CLI argument
Dependencies: speechrecognition, pyaudio, ffmpeg

Usage Example:
    python transcribe_video.py video.mp4 [language]
    Output: Creates "video.txt" with the transcription

========================================
"""


# ============================================================
# IMPORT SECTION - Required Python Libraries
# ============================================================
import math                # For computing total chunk count for progress display
import os                 # For file system operations (file paths and directories)
import subprocess         # For running external commands (ffmpeg)
import sys                # For accessing system information (command line arguments)
from speech_recognition import Recognizer, AudioFile, UnknownValueError, RequestError  # Speech recognition API from Google
import time                # For measuring total elapsed processing time
import wave               # For reading and writing WAV audio files


def _print_safe(message):
    """Prints message, replacing characters the console encoding can't handle
    (e.g. checkmark/cross symbols on a Windows cp1252 console) instead of
    crashing with UnicodeEncodeError."""
    try:
        print(message)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "ascii"
        print(message.encode(encoding, errors="replace").decode(encoding))


# ============================================================
# FUNCTION: extract_audio_from_video()
# ============================================================
def extract_audio_from_video(video_path):
    """
    Extracts audio from a video file using ffmpeg and saves it as a temporary WAV file.
    
    Args:
        video_path (str): Full path to the video file to process
                          Example: "movie.mp4", "/path/to/video.avi"
    
    Returns:
        str: Path to the extracted audio WAV file, or None if extraction fails
    
    How it works:
    1. Uses ffmpeg to remove video and keep only audio (-vn = no video)
    2. Converts audio to simple WAV format with:
       - 16000 Hz sample rate (lower rate is better for speech recognition)
       - 1 mono channel (single audio channel)
       - PCM 16-bit format (standard, compatible with speech_recognition)
    3. Saves result as "temp_audio.wav" in current directory
    
    FFmpeg Parameters Explained:
    ----------------------------
    -vn        : Disable video output (extract audio only)
    -acodec    : Specify audio codec for conversion
    -ar 16000  : Sample rate set to 16kHz (optimal for speech recognition)
    -ac 1      : Single audio channel (mono, not stereo)
    
    Return Value:
    -------------
    The function returns the path to the extracted audio file if successful.
    Returns None if ffmpeg is not found or extraction fails.
    """
    # Name of temporary file for extracted audio
    temp_audio_path = "temp_audio.wav"
    
    # Path to ffmpeg in the Python virtual environment
    venv_folder = ".venv"
    ffmpeg_exe = os.path.join(venv_folder, "Scripts", "ffmpeg.exe")
    
    # Check if ffmpeg exists at the virtual environment path
    if not os.path.exists(ffmpeg_exe):
        print("Warning: ffmpeg not found at .venv\\Scripts\\ffmpeg.exe.")
        print("Please install it system-wide or add to PATH.")
        ffmpeg_exe = None
    
    # Fallback: if ffmpeg is not in .venv, try system PATH on Windows
    if ffmpeg_exe is None:
        try:
            # Try running "ffmpeg -version" to verify installation
            subprocess.run(["ffmpeg", "-version"], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Warning: ffmpeg not found in PATH.")
            print("Please install ffmpeg from: https://ffmpeg.org/download.html")
            return None
    
    # If ffmpeg is found, extract the audio
    if ffmpeg_exe is not None:
        try:
            # FFmpeg command for extracting audio:
            # -i     : Input file (the video)
            # -vn   : Disable video extraction (audio only)
            # -acodec pcm_s16le : Output audio codec (PCM signed 16-bit little-endian)
            # -ar    16000       : Audio sample rate set to 16kHz (good for speech recognition)
            # -ac    1           : Single audio channel (mono)
            subprocess.run(
                [ffmpeg_exe, "-i", video_path, 
                 "-vn", "-acodec", "pcm_s16le", 
                 "-ar", "16000", "-ac", "1", temp_audio_path], 
                check=True, capture_output=True
            )
            return temp_audio_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error during audio extraction with ffmpeg.exe: {e}")
            raise
        except Exception as e:
            print(f"Error extracting audio from video with ffmpeg.exe: {e}")
            raise
    
    # Fallback second attempt: try with system ffmpeg from PATH
    try:
        print("Trying system ffmpeg from PATH...")
        subprocess.run(
            ["ffmpeg", "-i", video_path, 
             "-vn", "-acodec", "pcm_s16le", 
             "-ar", "16000", "-ac", "1", temp_audio_path], 
            check=True, capture_output=True
        )
        return temp_audio_path
        
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio with system ffmpeg: {e}")
        raise
    except Exception as e:
        print(f"Error extracting audio from video: {e}")
        raise


# ============================================================
# FUNCTION: transcribe_audio()
# ============================================================
def transcribe_audio(audio_path, language="it-IT", chunk_seconds=55):
    """
    Transcribes audio file to text using Google speech recognition API.

    Args:
        audio_path (str): Full path to the WAV audio file to transcribe
        language (str): Speech locale code passed to recognize_google(),
                        e.g. 'it-IT', 'en-US', 'es-ES'. Defaults to 'it-IT'.
        chunk_seconds (int): Length of each audio segment sent to the API.
                              The free Google Web Speech API is unreliable
                              (or outright rejects the request) on long audio,
                              so long files are split into chunks and
                              transcribed one at a time, then joined.

    Returns:
        str: Transcribed text in the requested language

    How it works:
    1. Uses speech_recognition API with Google Speech model
    2. Computes the audio duration up front to know the total chunk count
    3. Reads the WAV audio file in chunk_seconds-long segments, printing
       progress as "chunk N/total (X%)" for each one
    4. Sends each segment to the online speech recognition service
    5. Joins all segment transcriptions into the final text

    SPEECH RECOGNITION API DETAILS:
    --------------------------------
    - Recognizer()      : Creates object for managing speech recognition
    - AudioFile()       : Handles safe opening and closing of audio files
    - record(source, duration=...) : Reads one segment of audio, advancing
                                      the read position for the next call
    - recognize_google() : Sends data to Google service for transcription

    SUPPORTED AUDIO FORMATS:
    ------------------------
    This function works best with WAV files extracted by extract_audio_from_video().
    Supported formats for AudioFile include: .wav, .flac, .mp3 (if available)

    LANGUAGE SETTINGS:
    -----------------
    Defaults to Italian ('it-IT'). Pass a different locale code via the
    `language` argument (also exposed as the optional CLI argument in
    main()) to transcribe other languages, e.g. 'en-US', 'es-ES'.

    Return Value:
    -------------
    Returns the transcribed text as a string, with each chunk's transcription
    separated by a space. Silent chunks are skipped.
    """
    recognizer = Recognizer()
    chunks = []

    # Get the audio duration up front so progress can be shown as X/Y (Z%)
    with wave.open(audio_path, "rb") as wav_file:
        duration = wav_file.getnframes() / wav_file.getframerate()
    total_chunks = math.ceil(duration / chunk_seconds)

    try:
        with AudioFile(audio_path) as source:
            chunk_number = 0
            while True:
                chunk_number += 1
                audio_data = recognizer.record(source, duration=chunk_seconds)

                # No more audio left to read
                if len(audio_data.frame_data) == 0:
                    break

                progress_pct = min(chunk_number, total_chunks) / total_chunks * 100
                print(f"  Transcribing chunk {chunk_number}/{total_chunks} "
                      f"({progress_pct:.0f}%)...")
                try:
                    text = recognizer.recognize_google(audio_data, language=language)
                    chunks.append(text)
                except UnknownValueError:
                    # Chunk was silent or unintelligible; skip it
                    print(f"  Chunk {chunk_number}: no speech detected, skipping.")
                except RequestError as e:
                    print(f"  Chunk {chunk_number}: API request failed - {e}")

        return " ".join(chunks)

    except Exception as e:
        # Print error and re-raise exception for external handling
        print(f"Error transcribing audio file '{audio_path}': {e}")
        raise


# ============================================================
# FUNCTION: save_transcription()
# ============================================================
def save_transcription(text, output_path):
    """
    Saves transcribed text to a text file.
    
    Args:
        text (str): The transcribed text to be saved
        output_path (str): Full path where to save the output file
    
    How it works:
    1. Opens file in write mode ('w')
    2. Writes text to file using UTF-8 encoding (supports special characters)
    3. Automatically closes file after writing
    
    ENCODING DETAILS:
    -----------------
    Uses UTF-8 encoding which supports:
    - Latin characters (A-Z, a-z)
    - Special characters (è, é, ñ, etc.)
    - Unicode symbols and emojis if needed
    
    Return Value:
    -------------
    Returns None on success. Prints confirmation message to console.
    
    ERRORS:
    -------
    Raises FileNotFoundError if output directory doesn't exist.
    Raises PermissionError if no write access to file.
    """
    try:
        # Open file in write mode with UTF-8 encoding
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        # Print confirmation message
        _print_safe(f"✓ Transcription saved to {output_path}")
        
    except FileNotFoundError:
        # Error handling: directory does not exist
        print(f"Error: Cannot write to '{os.path.dirname(output_path)}'.")
        print("   Please create the output directory first.")
        raise
    except PermissionError:
        # Error handling: access denied
        print(f"Error: No permission to write to '{output_path}'.")
        raise
    except Exception as e:
        # Generic error handling
        print(f"Error saving transcription to '{output_path}': {e}")
        raise


# ============================================================
# FUNCTION: main()
# ============================================================
def main():
    """
    Main function that orchestrates the video transcription process.
    
    How it works:
    1. Checks if a file was provided as argument
    2. Extracts audio from video using ffmpeg
    3. Transcribes audio to text using AI recognition
    4. Saves text to output file
    5. Cleans up temporary audio file
    6. Reports total elapsed time
    
    USAGE INSTRUCTION:
    -----------------
    Run from command line (DOS/Command Prompt):

        python utilities\\transcribe_video.py <video_file> [language]

    Example:

        cd E:\\code\\LeaningPython3\\utilities
        python transcribe_video.py my_video.mp4
        python transcribe_video.py my_video.mp4 en-US

    `language` is an optional speech locale code (default 'it-IT').
    This will create "my_video.txt" in the same directory.
    
    OUTPUT FILE NAME:
    ----------------
    Output file has same name as input but .txt extension:
        Input:  video.mp4    → Output: video.txt
        Input:  audio.wav    → Output: audio.txt
    """
    
    # Check number of command arguments
    # If no file is given, show usage instructions
    if len(os.sys.argv) not in (2, 3):
        print("=" * 50)
        print("VIDEO TRANSCRIPTION TOOL")
        print("=" * 50)
        print()
        print("Usage: python transcribe_video.py <input_file> [language]")
        print("       language: speech locale code, default 'it-IT'")
        print()
        print("Examples:")
        print('  python transcribe_video.py movie.mp4')
        print('  python transcribe_video.py interview.avi en-US')
        print('  python transcribe_video.py recording.wav es-ES')
        print()
        print("Output: Creates <input_file>.txt with transcription")
        print("=" * 50)
        return

    # Get path to the video/audio file provided
    input_path = os.sys.argv[1]
    language = os.sys.argv[2] if len(os.sys.argv) == 3 else "it-IT"

    # Start time reference, used to report total elapsed time at the end
    start_time = time.time()

    # Calculate output file path (same name but with .txt extension)
    # Example: "video.mp4" → "video.txt"
    output_path = os.path.splitext(input_path)[0] + ".txt"

    print("=" * 50)
    print("TRANSCRIPTION PROCESS")
    print("=" * 50)
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    print()

    try:
        # STEP 1: Extract audio from video
        print("STEP 1/3: Extracting audio from video...")
        temp_audio_path = extract_audio_from_video(input_path)
        if temp_audio_path:
            _print_safe(f"✓ Audio extracted to {temp_audio_path}")
        else:
            _print_safe("✗ Failed to extract audio. Cannot continue.")
            return

        # STEP 2: Transcribe audio to text
        print("\nSTEP 2/3: Transcribing audio to text...")
        transcription = transcribe_audio(temp_audio_path, language=language)
        _print_safe("✓ Transcription completed.")

        # STEP 3: Save transcribed text
        print("\nSTEP 3/3: Saving transcription...")
        save_transcription(transcription, output_path)

    except FileNotFoundError as e:
        # Error handling: file not found
        _print_safe(f"\n✗ Error: File not found - {e}")
        print("   Please check that the input file path is correct.")

    except Exception as e:
        # Generic error handling
        _print_safe(f"\n✗ Error during transcription: {e}")

    finally:
        # STEP CLEANUP: Remove temporary audio file if it exists
        temp_audio_path = "temp_audio.wav"
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                _print_safe("✓ Temporary audio file removed.")
            except Exception as e:
                print(f"Warning: Could not remove temp file: {e}")

    elapsed_seconds = time.time() - start_time
    minutes, seconds = divmod(int(elapsed_seconds), 60)

    print()
    print("=" * 50)
    print("PROCESS COMPLETE")
    print(f"Elapsed time: {minutes}m {seconds}s")
    print("=" * 50)


# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # This block runs only when the script is executed directly (not imported).
    # Windows consoles default to the cp1252 codepage, which cannot encode the
    # checkmark/cross characters used in status messages below; force UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    main()