# 📚 Lessons Learned: Code Anomalies Review (V2)

This file compiles specific findings from recent coding sessions to prevent recurring documentation or code structure errors and defines general best practices for interacting with LLMs in a development context.

---

## 1) Specific Errors Already Happened

*These entries document concrete incidents, their technical impact, and the corrective actions taken.*

### `day-64-top-movies/main.py` (Date: 2026-07-26)
*   **What went wrong:** LLM duplicated the initial boilerplate block (e.g., imports and docstrings), resulting in two complete sets of necessary code at different points in the file structure.
*   **Impact:** Functional bug was not detected, but the presence of redundant/messy code significantly violates cleanliness standards.
*   **How it was fixed:** Manual cleanup by removing one full copy of the duplicated block.
*   **Files affected:** `day-64-top-movies/main.py`

### `Amazon_Price_tracker/main.py` (Date: 2026-03-12)
*   **What went wrong:** The LLM added new functional blocks (`send_email()`, etc.) but failed to remove the original "legacy" code below it (lines 129-176).
*   **Impact:** The file contained two conflicting execution paths. Variables necessary for the *new* functionality were often defined too late, causing a **`NameError`** when the main script ran. Furthermore, the old legacy code ensured double execution logic (e.g., running input prompts twice).
*   **Action/Solution:** The entire redundant "legacy" code block must be removed completely. All variables and constants required for the new functionality (`EMAIL_SERVER`, `URL`, etc.) *must* be defined before they are called in the primary `if __name__ == "__main__":` guard.
*   **Files affected:** `Amazon_Price_tracker/main.py`

### `utilities/build_md_toc.py` — xhtml2pdf wide-table rendering (Date: 2026-07-26)
*   **What went wrong:** A Markdown table with 11 columns crashed PDF generation with `ValueError: ... flowable given negative availWidth ...` inside `xhtml2pdf`/`reportlab`. After removing the crash, the table still visually overflowed past the page's right margin (or columns overlapped/collided) across three separate fix attempts, even though the generated HTML *looked* correct on inspection.
*   **Root causes (xhtml2pdf/reportlab, undocumented quirks):**
    1.  Automatic column-width calculation for tables with many columns can produce a negative available width and crash outright — must set explicit widths instead of relying on auto-layout.
    2.  `width: X%` on a `<table>`/cell is resolved by xhtml2pdf against the **full page width**, not the margin-adjusted printable area — must compute and use **absolute point widths** derived from the real printable width (`page_width - left_margin - right_margin`, converted mm→pt).
    3.  A column can never be made narrower than its **longest single unbreakable word** (no spaces) — if the assigned width is smaller, xhtml2pdf silently **expands that column anyway**, growing the table wider than declared and pushing later columns off the page. Must size a hard per-column minimum from the longest word (using an estimated glyph width for the font), not just from total text length.
    4.  **Most surprising:** when xhtml2pdf processes a **completely empty `<td>`** (no text/children) that has no *explicit* width of its own, it silently resets that column's width down to just its padding (a few points) — even if the header `<th>` for that column already declared a much larger width. This overrides the intended layout for the entire column, not just that one cell. Fix: set the explicit `width` style on **every cell in every row** (both `<th>` and `<td>`), never leaving it implicit for `<td>`.
*   **Debugging technique that worked:** Visual screenshots (including from three different PDF viewers) were misleading/inconsistent — at one point a viewer showed a stale cached render of an already-fixed file. The reliable method was to open the generated PDF programmatically (Python + `PyMuPDF`/`fitz`), extract the actual drawn cell rectangles (`page.get_drawings()`) and their coordinates, and compare them numerically against the page's printable width. This bypassed viewer-side caching/rendering differences entirely and pinpointed the exact column and pixel offset responsible.
*   **Action/Solution:** In `shrink_wide_tables()`, widths are computed as absolute pt values from the real printable width, with a per-column hard minimum based on the longest unbreakable word, and the resulting `width` style is applied to every `<th>` and `<td>` in the table (not just headers) so no cell is ever left with an implicit/None width.
*   **Files affected:** `utilities/build_md_toc.py`

### `utilities/build_md_toc.py` — doc-only task added executable lines (Date: 2026-07-26)
*   **What went wrong:** An LLM (Cline) was asked to add comments/docstrings only to `build_md_toc.py`. Alongside good docstrings, it also: (1) rewrote the text of an existing `print()` call and split it into two `print()` calls, (2) added a brand-new `print()` statement that did not exist before, and (3) added type hints to every touched function signature (`def f(x: str) -> None:`).
*   **Impact:** No crash, but silent behavior drift (extra/changed console output) that would not have been caught without an explicit `git diff` review. This happened *despite* an existing preventive rule ("Documenting Code Logic Changes", below) already telling the LLM not to do this.
*   **How it was fixed:** Reverted the two `print()` changes back to the original text/structure and removed the added type hints, verified via `git diff` that only comment/docstring lines remained changed, then re-ran the script to confirm behavior was unchanged.
*   **Root cause:** The existing rule said "no executable lines... modified/added" but did not explicitly call out two things LLMs treat as "obviously fine improvements" during doc-only tasks: (a) rewording/adding `print()`/log messages, and (b) adding type annotations to function signatures (these are code, not docstring content, even though they look like documentation).
*   **Files affected:** `utilities/build_md_toc.py`

### `utilities/build_md_toc.py` — doc-only task broke syntax with a stray `"""` (Date: 2026-08-09)

*   **What went wrong:** LLM (Cline) was asked to add comments documenting recent changes to `build_md_toc.py`, using `git diff` to find what changed, without touching code. Instead of consulting `utilities/lessons_learned.md`, it read `learning.md` (root, public, unrelated file). It then inserted a `#`-comment block right after the module's closing docstring `"""`, but appended an extra stray `"""` right after that block. That stray delimiter opened a new, unterminated triple-quoted string which silently swallowed `import sys, re, unicodedata, os`, `from pathlib import Path`, and the following code as inert string content.
*   **Impact:** `python -m py_compile` failed with `IndentationError: unexpected indent` (the swallowed `import`/code lines resurfaced as unexpected indentation once the string closed at the next unrelated `"""`). This would have been a silent, hard-to-diagnose failure if the mandatory `py_compile` check (see `.clinerules`) had not been run before considering the task done.
*   **How it was fixed:** `git checkout -- utilities/build_md_toc.py` (only one hunk was pending, so a full revert was safe); re-verified with `py_compile` that the file compiled again.
*   **Root cause:** Two compounding issues — (1) ambiguity between `learning.md` and `utilities/lessons_learned.md` led the LLM to skip the actual process rules; (2) even a "comments only" edit can break syntax by mis-placing a `"""` delimiter, which the LLM did not catch itself.
*   **Fix applied to `.clinerules`:** Added an explicit disambiguation section for the two similarly-named files, inlined the derived rules directly into `.clinerules` (so they apply even if `utilities/lessons_learned.md` is never opened), and added an explicit rule that a comment/docstring-only edit must never add/remove/duplicate a `"""` delimiter, with mandatory `git diff` + `py_compile` verification even for doc-only tasks.
*   **Files affected:** `utilities/build_md_toc.py` (reverted, no lasting damage)

### Process Note: Cline's `git diff` hangs forever on "Running" (Date: 2026-08-09)

*   **What went wrong:** Whenever Cline ran `git diff -- <file>` in its own VSCode terminal, the command appeared to hang indefinitely (stuck on "Running", requiring the user to click "Proceed While Running" or manually type `q` in the terminal to unblock it). Earlier symptoms attributed to this same root cause: `git diff` runs that seemed to "return empty output" and were silently retried by the LLM.
*   **Root cause:** `git diff`/`git log` invoke a pager (`less`, via Git for Windows) whenever stdout is a real terminal (TTY) — which VSCode's integrated terminal is. A human can dismiss the pager by pressing `q`; an LLM driving the terminal via text commands cannot send that keystroke, so the command never "completes" from its point of view. This was initially misdiagnosed as a VSCode/Cline shell-integration output-capture bug (a real, separate issue that was also present and partially masked this one — see `.venv`/PowerShell-profile investigation in this same session).
*   **First fix attempted (did NOT work):** Set `GIT_PAGER: cat` in the `env` of `terminal.integrated.automationProfile.windows` in the VSCode **user** `settings.json`. This VSCode setting controls the terminal profile VSCode's own Tasks/Debug system uses for automation — but Cline does **not** appear to honor it for its own extension-created terminals, so the env var never reached Cline's git process and the hang persisted after a fresh Cline session.
*   **Actual fix:** `git config --global core.pager cat` (writes to the user's `~/.gitconfig`). This works regardless of which terminal/shell/profile invokes git, because git reads its own config at invocation time rather than relying on an inherited environment variable. Verified immediately (no VSCode/terminal restart needed) — a fresh `git diff` printed full output and exited on its own. Trade-off: the user's own interactive `git diff`/`git log` also stop paging now (full output printed directly instead of via `less`), which was an accepted trade-off.
*   **Related, kept but not the actual fix:** A dedicated `"PowerShell (No Profile)"` terminal profile was also set up and pointed to by `automationProfile.windows` (`-NoProfile`), to rule out the user's customized `$PROFILE` as a source of shell-integration flakiness. Harmless to keep, but per the above, it's unconfirmed whether Cline actually uses this profile at all.
*   **Files affected:** none (VSCode user settings + global git config only, no project files)

### Process Note: large `replace_in_file` SEARCH block failure caused a fallback rewrite that deleted ~670 lines (Date: 2026-08-09)

*   **What went wrong:** During the same doc-only commenting task on `utilities/build_md_toc.py` (~780 lines), a `replace_in_file` operation's `SEARCH` block was too large/complex to match the file exactly. After that failure, the LLM's recovery attempt resulted in a rewritten file with 673 lines deleted and only 106 inserted — i.e. it reconstructed/rewrote large parts of the file from its own (imperfect) memory instead of surgically applying a small change to the real, freshly-read file content.
*   **Impact:** Would have silently destroyed most of a 780-line working module had the user not visually spotted a truncated line (`p` with no continuation, mid-function) and stopped Cline before it "successfully" ran `py_compile`/tests against the mangled file.
*   **How it was fixed:** `git checkout -- utilities/build_md_toc.py` (single pending file, safe full revert); re-verified `py_compile` passed.
*   **Root cause:** Attempting one large edit (or an edit whose `SEARCH` block spans a large/complex region) on a long file is fragile — small formatting differences (whitespace, line endings) make exact-match search-replace fail, and the fallback behavior on failure is not safe to trust for large files.
*   **Fix applied to `.clinerules`:** Added rule requiring small, sequential, individually-verified edits on long/complex files, and forbidding "rewrite from memory" as a recovery strategy when a search/replace match fails — the correct recovery is to re-read the current file from disk and retry with a smaller, more precise block.
*   **Files affected:** `utilities/build_md_toc.py` (reverted, no lasting damage)

### `utilities/transcribe_video.py` — Qwen (32k context) produced bloated docstring + misindented comment (Date: 2026-08-10)
*   **What went wrong:** Local Qwen model, run with context window lowered to 32k, was asked to work on `transcribe_video.py`. Unprompted, it (1) expanded a concise, already-good docstring on `_print_safe()` into a verbose `Args:`/`Returns:`/`ERRORS:` boilerplate block that violates this project's "no comments unless they explain a non-obvious why" convention, and (2) reworded an inline comment above `except UnknownValueError:` and in doing so re-indented it to 16 spaces instead of the 20 spaces matching the surrounding block, leaving it visually misaligned with the code it annotates.
*   **Impact:** No functional/behavioral change and the file still compiled fine (`py_compile` passes — comment-only lines don't affect Python's INDENT/DEDENT tracking), but the diff was noisy and the misindentation would read as sloppy/inconsistent to a human reviewer.
*   **How it was fixed:** `git checkout -- utilities/transcribe_video.py` (single pending file, full revert was safe).
*   **Root cause:** Same family as the `build_md_toc.py` doc-only incidents above (models treat "add/improve comments" as license to over-document), plus a new failure mode: the model didn't preserve the exact leading-whitespace column of the comment it rewrote, even though the line's *content* was the only thing it should have changed.
*   **Files affected:** `utilities/transcribe_video.py` (reverted, no lasting damage)

### Process Note: `day-68-flask-auth/main.py` (Date: 2026-03-10)
*   **Anomaly:** Minimal change was required—only a docstring rewrite for the `login()` function, with no change to core logic or structure.
*   **Lesson:** Routine structural changes (like updating documentation) are generally safe when only minor comment updates occur and the surrounding code context is carefully managed.

---

## 2) General Rules Derived (Preventative Measures)

*These entries provide clear, actionable instructions intended to prevent recurring errors across all projects.*

### Rule: Initialization Order & Code Cleanup
*   **Rule:** When refactoring or adding new functionality, always ensure that **all required variables/constants are defined** before the functions that use them and crucially, before the primary execution block (`if __name__ == "__main__":`). Furthermore, completely remove old, redundant, or superseded blocks of code to prevent double execution or conflicting logic paths.
*   **Originates from:** `Amazon_Price_tracker/main.py` (Date: 2026-03-12)
*   **Scope:** All LLMs/models.

### Rule: Documenting Code Logic Changes
*   **Rule:** When improving documentation, ensure that the underlying functional code remains character-for-character identical, including indentation and line order. Absolutely no executable lines of code should be modified, moved, added, or removed (statements, imports, variable declarations/constants, function calls, etc.). This explicitly includes two cases LLMs tend to treat as "harmless documentation improvements" but which are NOT:
    1.  **`print()` / logging statements:** do not reword, reformat, split, or add new `print()`/logging calls, even to make output "clearer" or more consistent with new docstrings.
    2.  **Type hints in function/method signatures** (e.g. `def f(x: str) -> None:`): these are code, not documentation — adding or changing them is forbidden in a doc-only task. (Type hints *inside* a docstring's Args/Returns section are fine to add or improve.)
*   **Originates from:** `Amazon_Price_tracker/main.py` (2026-03-12); confirmed again in `utilities/build_md_toc.py` (2026-07-26, see incident above)
*   **Scope:** All LLMs/models.

### Rule: Contextual Awareness and Verification
*   **Rule:** When performing documentation or refactoring tasks, treat the source material as sacred ground. Always verify changes using a `diff` tool (e.g., `git diff`) to ensure that *only* comments/docstrings have changed and no functional code lines were accidentally altered. For multi-file projects, process files individually.
*   **Originates from:** Preventive rule, not yet tied to a documented incident
*   **Scope:** All LLMs/models.

### Rule: Comment/Docstring Style — Indentation & Conciseness
*   **Rule:** When adding, rewording, or improving a comment or docstring:
    1.  **Match the leading whitespace of the code it sits next to.** An inline `#` comment on its own line must be indented to the exact same column as the statement immediately below/around it — never less, never more. Copy the indentation character-for-character from the surrounding line rather than retyping it.
    2.  **Keep it as short as the original, or shorter.** Do not expand a one-line comment into a multi-line block, and do not add `Args:`/`Returns:`/`Raises:`/`ERRORS:` sections to a docstring unless the function's signature is genuinely non-obvious and the project's own style already uses that format elsewhere. A comment should only exist to explain a non-obvious *why* (a workaround, a platform quirk, a hidden constraint) — never to restate *what* the code already says via its names.
    3.  **After the edit, re-check the diff visually for indentation drift**, not just for wording — `git diff` can make a 4-space indentation change hard to spot at a glance next to a wording change; look at the leading whitespace column specifically.
*   **Originates from:** `utilities/transcribe_video.py` — Qwen incident (2026-08-10, see above)
*   **Scope:** All LLMs/models.

### ⚠️ To be classified
*(Add any general guidelines or errors here that do not fit neatly into the above chapters.)*