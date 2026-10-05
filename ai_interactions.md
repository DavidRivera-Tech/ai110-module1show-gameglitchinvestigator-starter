# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

AI agent used: **Claude**, working agentically with its own code workspace: it edited the files, ran flake8 and pytest, and played the game with Streamlit's testing tool before handing the files to me.

**What task did you give the agent?**

Add a "High Score" tracker: when I win, save my score to a file if it beats the best score for that difficulty, show "New high score!" when that happens, show the best score for Easy, Normal, and Hard in the sidebar, and keep the scores after the game is closed and reopened. Keep the core game logic working and add tests.

**What did the agent do?**

Files modified:
- `logic_utils.py`: added `load_high_scores()`, `save_high_scores()`, and `update_high_score()` with docstrings. Loading treats a missing or broken file as "no scores yet" instead of crashing.
- `app.py`: on a win, checks and saves the high score and shows "🏆 New high score for <difficulty>!"; added a "🏆 High Scores" list to the sidebar. Scores are saved to `high_scores.json` next to `app.py`.
- `tests/test_game_logic.py`: added 5 tests (first win sets a record, lower score doesn't replace it, scores are tracked per difficulty, save/load round trip, missing or broken file returns no scores).

Steps the agent took:
1. Wrote the three high score functions in `logic_utils.py` and ran flake8 and the docstring examples.
2. Noticed that the sidebar is drawn before the guess is processed (the same problem as Bug #10), so a new record wouldn't appear until the next click. It used an `st.sidebar.empty()` placeholder filled in at the end of the script instead.
3. Wired the functions into `app.py` and added the 5 tests (27 total, all passing, flake8 clean).
4. Simulated games with Streamlit's testing tool: won on the first try (score 100, record saved and shown immediately), restarted the app (score still there), won with a lower score (record unchanged), and lost a game on Easy (no record created). The first simulation run timed out after 3 seconds; the agent recognized this was the testing tool's default time limit, not a bug in the game, and reran it with a longer limit.

**What did you have to verify or fix manually?**

I replaced my files with the agent's versions and checked everything myself instead of trusting the agent's report: I ran `python -m pytest` (27 passed) and flake8 (no warnings), then played the game. I won a game and saw "🏆 New high score for Normal!" and the sidebar update to my score of 70. I closed the game, restarted it, and confirmed the high score was still there. I also added `high_scores.json` to `.gitignore` so my personal test scores aren't committed to GitHub. While testing, I noticed the game never explained how points work, so I asked the agent to add a "How scoring works" panel to the sidebar. Its first version still confused me (I couldn't tell how a 3rd-guess win added up), so I asked it to clarify, and it rewrote the panel to show the score's two parts with a worked example: miss, miss, win on guess 3 = -5 - 5 + 80 = 70. I confirmed that matched my real game earlier, where I guessed 100, 50, then 95 and finished with 70.

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

**Result:** all tests pass. Originally 19 (3 starter, 9 bug-fix, 7 edge-case); 3 hot/cold tests were added for Challenge 4 and 5 high score tests for Challenge 2, for 27 total. Full output is in `README.md` and `test_results.txt`.

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