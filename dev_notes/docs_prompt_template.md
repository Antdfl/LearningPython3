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

---

## Detailed / Junior-Friendly Prompt Template (via Cline, local LLM)

Use this variant instead of the core template above only when you explicitly want richer explanations (e.g. "document for a junior programmer", "explain the advanced concepts") rather than a light touch-up of existing one-liners.

> **Style note (updated 2026-08-18):** `utilities/build_md_toc.py` is now the **literal format to copy**, not just a tone reference — module docstring with `Purpose:`/`Audience Note for Junior Programmers:`/`Functionality Overview:`/`Dependencies:` sections, function docstrings with a short discursive "why" followed by `Parameters:`/`Returns:` sections when relevant. This applies to Cline/local models too, not only to Claude writing directly. That file's original author was Claude (not Cline) precisely because local models (Qwen 3.5 9B, Gemma-4-e4b) had repeatedly failed on files of this shape — see the 2026-08-11/2026-08-12 entries in `dev_notes/lessons_learned.md`. The prompt below carries extra guardrails specifically to compensate for that known risk when a local model is the one producing this format; do not drop those guardrails just because the format itself is now allowed.

```
Add DETAILED documentation to the following Python code, at a level suitable for a junior programmer, following the format used in utilities/build_md_toc.py: a module-level docstring with Purpose / Audience Note for Junior Programmers / Functionality Overview / Dependencies sections where relevant, and function/method docstrings with a short discursive "why" explanation followed by Parameters:/Returns: sections when the function has parameters or a non-trivial return value. Stay strictly within these binding rules (restated here even though they also live in .clinerules — do not rely on that file alone):

1. DO NOT modify, move, reorder, add, or remove any executable line of code (statements, imports, variable/constant declarations, function calls, control-flow structure). The functional code must remain character-for-character identical, including indentation and line order.
2. DO NOT add type hints to function/method signatures (type hints INSIDE a docstring's Parameters:/Returns: prose are fine and expected). DO NOT reword, split, or add print()/logging calls.
3. DO NOT add new functions, try/except blocks, __main__ guards, or any other logic. If you spot a real bug or design issue, report it SEPARATELY as a comment at the end of your response — do not fix it yourself.
4. Parameters:/Returns: MUST exactly match the function's real signature — same parameter names, same order, nothing invented. Before writing a Parameters: section, re-read the function's actual `def ...(...):` line as it currently stands in the file (not from memory) and only document parameters that are genuinely there. Inventing a parameter that doesn't exist is a factual error, not a style issue — this has happened before (a fabricated `post_id` parameter documented for a zero-argument route function).
5. NEVER add, remove, or duplicate a """ delimiter, an import line, or any other block already present in the file — a single stray/missing delimiter breaks the whole file, and even a correctly-delimited edit can silently delete adjacent real code without any py_compile error (see rule 8 below).
6. Comments/docstrings in English only, regardless of the language used in this conversation. Any non-Latin-script character appearing in your output is a hard stop signal — stop and say so instead of continuing.
7. Work on ONE function/class docstring per turn (never the whole file, never more than one docstring at once), using a small, targeted edit. The module-level docstring is its OWN separate turn — never combined with an edit that also touches import lines or any other code. State which step you are on ("Step X of N") against a numbered plan you propose before starting.
   - The module docstring MUST be the very first statement in the file — before ANY import line, not after them (a shebang or encoding comment may still precede it). A triple-quoted string placed after the imports is NOT a real module docstring in Python (it won't populate `__doc__`, `help()`, or Sphinx output) even though it compiles fine — it's just an inert string sitting in the wrong place. Moving it to the top does not require changing the text of any import line, only its own position relative to them.
   - For ORM/dataclass model classes, a `Fields:` list (name, type, constraints) is allowed alongside the discursive explanation — make sure it matches the class's real declared fields exactly.
8. Your search/replace block must start and end exactly at the docstring's """ delimiters (existing, or the exact insertion point). It must NEVER include, in either the search or the replacement, any executable code line immediately before or after the docstring (e.g. __tablename__, a field declaration, a decorator, a return statement) — these longer, structured docstrings are proven to increase the risk of a search/replace block silently swallowing adjacent code.
9. After EVERY step: show the exact `git diff -- <file>` output for that step and classify every single removed (`-`) line as comment/docstring-only before calling the step done. Additionally, run a quick presence check for the real code immediately surrounding the docstring you just touched (e.g. grep/Select-String count of expected field names, __tablename__, decorators) and confirm the count is unchanged BEFORE moving to the next item. An empty/silent tool result is NOT success — treat it as unverified and re-run.
10. Before declaring the whole task complete: run `git diff --stat` on the WHOLE file and explicitly list every item from the original numbered plan with its individual status (done/not done). An aggregate line count is not proof of completion.
11. Run `.venv\Scripts\python.exe -m py_compile <file>` after every step and paste its real output.

File to document (one at a time): [FILE PATH HERE]
```

### Extra guidance for this variant

*   **File size:** if the target file is over ~100-150 lines, expect this to take multiple turns — do not ask Cline to "document the whole file" in one shot even if it accepts. Past ~300 lines, don't show the full file at once either (extract just the target function/section per turn), per the context-budgeting rules in `.clinerules`.
*   **Restate rules every turn/task, not just once:** correction given mid-conversation on one file did not carry over to a fresh task on a different file even with `.clinerules` already updated (see `day-71-blog-for-deployment/main.py` incidents, 2026-08-11/12). Paste the numbered rule block above again each time you start a new Cline task, not just the first.
*   **If Cline stalls, self-contradicts, or the conversation exceeds ~15-20 turns on the same file:** stop and start a fresh task, seeding it with only the current on-disk file state + the remaining plan items — not the full prior chat history.
*   **If local-model attempts keep failing on a file of this shape/size:** consider asking Claude to write the documentation directly instead of continuing to route it through Cline — reserve the local-LLM route for smaller, more atomic files, or for continuing/finishing a file Claude already started.

---

## Commit Message Prompt Template (via Cline, local LLM)

Use this whenever asking Cline/a local model to draft a commit message for pending changes. Added 2026-08-18 after a real incident: a commit message for a docs-only change on `day-68-flask-auth/main.py` described the file's existing authentication functionality (User model, password hashing, Flask-Login) as if it had just been implemented by that commit, when the diff only added docstrings. See `.clinerules`, section "Regole per la generazione di messaggi di commit", and the corresponding rule in `dev_notes/lessons_learned.md`.

```
Draft a commit message for the currently staged/pending changes. Follow these binding rules:

1. Base the message ONLY on the actual `git diff` / `git diff --stat` output for the changed file(s) — run it yourself first, don't rely on your general knowledge of what the file does. Read the diff before writing a single word of the message.
2. If the diff only adds/changes comments, docstrings, or other documentation (zero executable code lines changed), the message MUST say so explicitly (e.g. "no executable code was changed") and must NOT describe application functionality (models, routes, auth, forms, etc.) as if it were implemented by this commit.
3. Do not list pre-existing, untouched functionality under a verb like "Implemented"/"Add"/"Create" just because it happens to be present in the file — only describe what the `+`/`-` lines in the diff actually show changing.
4. If multiple unrelated files/concerns are staged together (e.g. course-exercise code alongside unrelated process/config files), point this out and suggest splitting into separate commits rather than writing one message that covers both.
5. Keep the subject line under ~70 characters; put any detail in the body.

Show me the `git diff --stat` you based this on alongside the proposed message, so I can check the message actually matches it.
```
