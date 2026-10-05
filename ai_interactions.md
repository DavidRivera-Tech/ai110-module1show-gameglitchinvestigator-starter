# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

AI assistant used: **Claude**

**Prompt used (for all tests below):**
```
Generate pytest cases in tests/test_game_logic.py that target each bug I fixed,
plus at least three edge cases (negative numbers, decimals, extremely large
values, empty input, non-numeric strings).
```

I reviewed each generated test against my Bug Reproduction Log in `reflection.md` and checked that the expected values were correct before running them.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Negative number (`"-5"` on Easy) | Prompt above | `test_negative_number_rejected` | ✅ Yes | The original game accepted -20 on Easy, so negatives must be rejected. |
| Decimal (`"4.9"`) | Prompt above | `test_decimal_rejected_not_truncated` | ✅ Yes | The original code silently cut 4.9 down to 4; the player should be told to enter a whole number instead. |
| Extremely large number (`"99999999999999999999"`) | Prompt above | `test_extremely_large_number_rejected` | ✅ Yes | Makes sure a huge number doesn't crash the game and is rejected as out of range. |
| Empty input (`""`) | Prompt above | `test_empty_input_rejected` | ✅ Yes | Clicking Submit with nothing typed should show an error, not count as a guess. |
| Spaces around a number (`"  7  "`) | Prompt above | `test_whitespace_around_number_accepted` | ✅ Yes | A player might accidentally type spaces; a valid number should still work. |
| Range boundaries (`1`, `20`, `0`, `21` on Easy) | Prompt above | `test_boundary_values` | ✅ Yes | Checks the exact edges: 1 and 20 allowed, 0 and 21 rejected, which catches off-by-one mistakes. |
| Very late win (attempt 20) | Prompt above | `test_win_score_never_below_10` | ✅ Yes | A late win should still give the minimum 10 points, not zero or negative. |

**Result:** all tests pass. Originally 19 (3 starter, 9 bug-fix, 7 edge-case); 3 hot/cold tests were added later for Challenge 4, for 22 total. Full output is in `README.md` and `test_results.txt`.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

AI assistant used: **Claude** | Linter: **flake8** (checks code against PEP 8, Python's official style guide)

**Prompt used:**

```
Add professional docstrings (Args, Returns, Examples) to every function in
logic_utils.py. Then review app.py, logic_utils.py, and tests/test_game_logic.py
for PEP 8 compliance and fix every warning flake8 reports, without changing how
the game works.
```

**Linting output before** (`python -m flake8 app.py logic_utils.py tests/test_game_logic.py`, full list in `lint_before.txt`):

```
app.py: 13 x E501 line too long, 1 x W292 no newline at end of file
logic_utils.py: 12 x E501 line too long
tests/test_game_logic.py: 3 x E501 line too long, 16 x E302 expected 2 blank lines, 1 x W292 no newline at end of file
Total: 46 warnings
```

**Linting output after** (saved in `lint_after.txt`):

```
(no output - 0 warnings)
```

**Changes the AI suggested and which I applied:**

| Warning | What it means | AI's suggested fix | Applied? |
|---------|---------------|--------------------|----------|
| E501 (line too long) | Lines over 79 characters | Split long `# FIX:` comments and code lines across multiple lines | ✅ Yes |
| E302 (expected 2 blank lines) | Functions need 2 blank lines between them | Added 2 blank lines between every test function | ✅ Yes |
| W292 (no newline at end of file) | Files should end with a newline | Added a final newline to `app.py` and the test file | ✅ Yes |
| Docstrings | `logic_utils.py` had short or missing docstrings | Added full docstrings with Args, Returns, and Examples to all 5 functions (get_temperature, added later for Challenge 4, also has one) | ✅ Yes |
| Import order | Imports weren't grouped | Sorted imports alphabetically and separated Python's built-in `random` from third-party `streamlit` | ✅ Yes |

Naming was already PEP 8 compliant (functions and variables use `snake_case`), so no renaming was needed.

**How I verified it:** I ran flake8 again and got no output, ran `python -m pytest` (still 19 passed), and played the game to confirm nothing about how it works changed.

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

I gave ChatGPT and Claude the exact same prompt, each in a fresh chat with no other context: the original buggy `check_guess` function from the starter code, plus a description of two bugs (Bug #5: the "Go HIGHER"/"Go LOWER" hints were backwards, and Bug #6: the secret sometimes arrived as a string, causing wrong hints). I asked each model to fix the function and explain why it was broken.

| | Model A | Model B |
|-|---------|---------|
| **Model name** | ChatGPT | Claude |
| **Response summary** | Found both bugs. Fixed them by converting `guess` and `secret` to `int` at the top of the function, then swapping the hint messages. Explained the string bug step by step: `9 > "10"` raises a TypeError, the fallback compares `"9" > "10"`, and that is True because Python compares the first characters ("9" vs "1"). | Found both bugs. Same core fix (convert both to `int` up front), but wrapped the conversion in `try/except (TypeError, ValueError)` and returns `"Invalid"` for input like `"abc"`. Also explained why `42 == "42"` is False, and warned that the new `"Invalid"` outcome might need handling by the caller. |
| **More Pythonic?** | Concise, but uses `else` after a `return` and would crash with a `ValueError` on non-numeric input. | ✅ More Pythonic: uses early returns with no unnecessary `else`, catches specific exceptions instead of crashing, and removes the duplicated fallback so there is one code path. |
| **Clearer explanation?** | ✅ Easier to follow: it walks through each value one step at a time with small examples, and ends with a simple lesson ("normalize the data before making decisions with it"). | Also clear and slightly more complete, but denser to read. |

**Which did you prefer and why?**

I preferred Claude's fix because it handles bad input instead of crashing and is written in a cleaner, more Pythonic way. I preferred ChatGPT's explanation because breaking the string comparison down step by step made the bug easier to understand. Neither fix was exactly right for my project, though: both still returned a tuple like `("Win", "🎉 Correct!")`, which would fail the starter tests that expect just `"Win"`. In my final code, `check_guess` returns only the outcome, the hint text lives in a separate `get_hint_message` function, and input validation happens earlier in `parse_guess`, so I combined ideas from both instead of copying either one.

**Each model's fixed code (copied from their responses):**

ChatGPT:
```python
def check_guess(guess, secret):
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win", "🎉 Correct!"

    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    else:
        return "Too Low", "📈 Go HIGHER!"
```

Claude:
```python
def check_guess(guess, secret):
    # Normalize: the secret sometimes arrives as a string, so coerce both to int.
    try:
        guess = int(guess)
        secret = int(secret)
    except (TypeError, ValueError):
        return "Invalid", "⚠️ Please enter a valid number."

    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"
```