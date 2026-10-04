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

**Result:** all 19 tests pass (3 starter, 9 bug-fix, 7 edge-case). Full output is in `README.md` and `test_results.txt`.

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->
