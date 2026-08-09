# Prompt for Enhancing Documentation Without Altering Code Logic

This is a reusable prompt intended for use with a Large Language Model (LLM) when the goal is to enhance comments and docstrings within a Python file (`.py`) or an entire source directory, while strictly ensuring that the underlying functional code remains untouched, un-duplicated, and unaltered.

> **Note:** the binding rules for this project live in `dev_notes/lessons_learned.md` (see "Rule: Documenting Code Logic Changes"). This file is just a ready-to-paste prompt text; if the two ever disagree, `lessons_learned.md` is the source of truth.

## Core Prompt Template

```
Improve ONLY the documentation of the following Python code: inline comments, module/function/class docstrings, and type hints within docstrings (Args/Returns/Raises).

BINDING RULES — no exceptions:
1. DO NOT modify, move, reorder, add, or remove any executable lines of code (statements, imports, variable declarations/constants, function calls, if/else structure, etc.). The functional code must remain character-for-character identical, including indentation and line order.
2. DO NOT add new functions, try/except blocks, __main__ guards, error handling, or any other logic, even if it appears to be an improvement. If you believe the code has a bug or warrants refactoring, report this SEPARATELY in a comment at the end of your response; do not modify the code yourself.
3. DO NOT duplicate existing docstrings, imports, or code blocks. If a docstring or comment already exists, replace or improve that specific section, but do not add new ones next to it.
4. You are restricted only to: writing/rewriting docstrings, adding or improving inline comments (#...), and removing obsolete or redundant comments. Nothing else.
5. Return the COMPLETE and updated file (not just an excerpt), so I can perform a clean line-by-line diff against the original.
6. If the file/directory is very long, ask me to proceed one file at a time instead of summarizing or truncating.

Before responding, re-read your draft and verify that a `diff` between the original and your version shows ONLY changes to comments/docstrings and absolutely no change to executable code lines.

File/Directory to Document:
[paste the file name or list of files here]
```

## Best Practices & Usage Guidelines

*   **Always Verify with Diff:** After generation, always use `git diff` as it is the only reliable method to ensure that no functional line of code has changed, even when using a well-crafted prompt.
*   **Process Files Individually (Recommended):** If the directory contains multiple files, it is better to request **one file at a time** rather than the entire directory together. This minimizes the risk of the LLM confusing or duplicating content across different source files.
*   **Review Before Commit:** Do not commit until you have checked the diff and (if possible) compiled/executed the modified file.