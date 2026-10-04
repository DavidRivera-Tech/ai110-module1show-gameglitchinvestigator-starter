# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?

 When I first ran the game with `python -m streamlit run app.py`, it opened in my browser with a game controller icon, the title "Game Glitch Investigator," and the caption "An AI-generated guessing game. Something is off." The main screen had a "Make a guess" section with an input box, Submit Guess and New Game buttons, a Show hint checkbox, and a Developer Debug Info dropdown that showed the secret number, attempts, score, difficulty, and guess history. On the left, a Settings sidebar let me pick Easy, Normal, or Hard, and showed the range and number of attempts allowed for each. At first glance it looked like a normal number-guessing game, but something seemed off right away: The game opened on Normal, the sidebar said "Attempts allowed: 8" while the main box said "Attempts left: 7" before I had made a single guess.

- List at least two concrete bugs you noticed at the start
(for example: "the hints were backwards").

1. **Attempts are off by one.** On Normal, the sidebar said "Attempts allowed: 8" but the main box said "Attempts left: 7" before I made any guess, and the debug panel already showed "Attempts: 1."
  2. **Out-of-range guesses are accepted.** On Easy (range 1–20), I guessed 101, 0, and -20, and the game accepted all of them with no error.
  3. **New Game doesn't start a fresh game.** After clicking New Game, my score stayed at -35 and my old guesses stayed in History.
  4. **Hard mode is easier than Normal.** Hard has a range of 1–50 while Normal has 1–100.
  5. **The hints are backwards.** With a secret of 79, I guessed 80 and the game said "Go HIGHER!", and when I guessed 50 it said "Go LOWER!"
  6. **The same guess can get opposite hints.** With a secret of 79, I submitted 9 twice in a row; the first hint said "Go HIGHER!" and the second said "Go LOWER!"
  7. **The blue box always says "between 1 and 100."** On Easy, the sidebar said 1 to 20, but the main box still said 1 and 100.
  8. **Invalid input uses up an attempt.** When I typed "abc," the game showed "That is not a number." but Attempts left still went down by one.
  9. **Changing difficulty keeps the old secret.** When I switched from Normal to Easy, the secret stayed the same, even when it was outside Easy's 1–20 range.
  10. **The debug panel lags one guess behind.** I submitted 9 twice, but the History in Developer Debug Info only showed it once.
  11. **Wrong guesses can increase the score.** After two invalid inputs and four wrong guesses, my score was 5 instead of going down.


**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| # | Input Used | Expected Behavior | Actual Behavior | Console Error / Output | Suspected Code Location |
|---|------------|-------------------|-----------------|------------------------|-------------------------|
| 1 | Normal mode, before any guess | "Attempts left: 8" | "Attempts left: 7"; debug shows Attempts: 1 | none | `app.py` — `st.session_state.attempts = 1` (should start at 0) |
| 2 | Easy mode (1–20), guesses 101, 0, -20 | Error: guess must be between 1 and 20 | All three accepted, no error | none | `app.py` — `parse_guess()` has no range check |
| 3 | Click "New Game" after playing | Score 0, history cleared, fresh game starts | Score stayed -35, old guesses stayed in History | none | `app.py` — `if new_game:` block only resets `attempts` and `secret`, not `status`, `score`, or `history` |
| 4 | Select Hard difficulty | Wider range than Normal (1–100) | Range is 1–50 (easier than Normal) | none | `app.py` — `get_range_for_difficulty()` returns `1, 50` for Hard |
| 5 | Normal, secret 79, guess 80 | "Go LOWER" | "📈 Go HIGHER!" | none | `app.py` — `check_guess()`: Too High / Too Low messages are swapped |
| 6 | Normal, secret 79, guess 9 submitted twice | Same hint both times ("Go HIGHER") | 1st: "📈 Go HIGHER!", 2nd: "📉 Go LOWER!" | none | `app.py` — secret converted to `str` on even attempts, so `"9" > "79"` is a text comparison |
| 7 | Switch to Easy | Blue box says "between 1 and 20" | Blue box says "between 1 and 100" | none | `app.py` — `st.info(...)` message is hardcoded to 1–100 |
| 8 | Type `abc`, click Submit | Error shown, attempt not used | Error shown, Attempts left went down by 1 | "That is not a number." | `app.py` — `attempts += 1` runs before `parse_guess()` |
| 9 | Normal mode, note secret, switch to Easy | New secret within 1–20 | Secret stayed the same number | none | `app.py` — secret only created once (`if "secret" not in st.session_state`) |
| 10 | Submit guess 9 twice | Debug History shows both guesses | History shows 9 only once | none | `app.py` — debug expander is drawn before the `if submit:` block |
| 11 | Normal, secret 79, guesses 80, 50, 9 (no win) | Score goes down for wrong guesses | Score went up to 5 | none | `app.py` — `update_score()` adds +5 for "Too High" on even attempts |


**Game Session Trace**
```
Difficulty: Normal | Secret (from Debug Info): 79
Start: sidebar "Attempts allowed: 8", blue box "Attempts left: 7", debug Attempts: 1
Guess "abc"  -> "That is not a number."  (attempt still used)
Guess "abc"  -> "That is not a number."  (attempt still used)
Guess 80     -> "📈 Go HIGHER!"  (80 is above 79, should say Go LOWER)
Guess 50     -> "📉 Go LOWER!"   (50 is below 79, should say Go HIGHER)
Guess 9      -> "📈 Go HIGHER!"
Guess 9      -> "📉 Go LOWER!"   (same guess, opposite hint)
Debug panel after 6 submits: Attempts 6, Score 5, History ["abc","abc",80,50,9]
  -> score went UP without winning; History missing the last 9
```

**Starter test run**
```
(.venv) PS C:\Users\Solom\Desktop\ai110-module1show-gameglitchinvestigator-starter> python -m pytest
====================================================== test session starts ======================================================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Solom\Desktop\ai110-module1show-gameglitchinvestigator-starter
plugins: anyio-4.15.1
collected 3 items                                                                                                                

tests\test_game_logic.py FFF                                                                                               [100%]

=========================================================== FAILURES ============================================================
______________________________________________________ test_winning_guess _______________________________________________________

    def test_winning_guess():
        # If the secret is 50 and guess is 50, it should be a win
>       result = check_guess(50, 50)
                 ^^^^^^^^^^^^^^^^^^^

tests\test_game_logic.py:5: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

guess = 50, secret = 50

    def check_guess(guess, secret):
        """
        Compare guess to secret and return (outcome, message).
    
        outcome examples: "Win", "Too High", "Too Low"
        """
>       raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
E       NotImplementedError: Refactor this function from app.py into logic_utils.py

logic_utils.py:21: NotImplementedError
______________________________________________________ test_guess_too_high ______________________________________________________

    def test_guess_too_high():
        # If secret is 50 and guess is 60, hint should be "Too High"
>       result = check_guess(60, 50)
                 ^^^^^^^^^^^^^^^^^^^

tests\test_game_logic.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

guess = 60, secret = 50

    def check_guess(guess, secret):
        """
        Compare guess to secret and return (outcome, message).
    
        outcome examples: "Win", "Too High", "Too Low"
        """
>       raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
E       NotImplementedError: Refactor this function from app.py into logic_utils.py

logic_utils.py:21: NotImplementedError
______________________________________________________ test_guess_too_low _______________________________________________________

    def test_guess_too_low():
        # If secret is 50 and guess is 40, hint should be "Too Low"
>       result = check_guess(40, 50)
                 ^^^^^^^^^^^^^^^^^^^

tests\test_game_logic.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

guess = 40, secret = 50

    def check_guess(guess, secret):
        """
        Compare guess to secret and return (outcome, message).
    
        outcome examples: "Win", "Too High", "Too Low"
        """
>       raise NotImplementedError("Refactor this function from app.py into logic_utils.py")
E       NotImplementedError: Refactor this function from app.py into logic_utils.py

logic_utils.py:21: NotImplementedError
==================================================== short test summary info ====================================================
FAILED tests/test_game_logic.py::test_winning_guess - NotImplementedError: Refactor this function from app.py into logic_utils.py
FAILED tests/test_game_logic.py::test_guess_too_high - NotImplementedError: Refactor this function from app.py into logic_utils.py
FAILED tests/test_game_logic.py::test_guess_too_low - NotImplementedError: Refactor this function from app.py into logic_utils.py
======================================================= 3 failed in 0.15s =======================================================
(.venv) PS C:\Users\Solom\Desktop\ai110-module1show-gameglitchinvestigator-starter> 
```


---

## 2. How did you use AI as a teammate?

- **Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?**

I used Claude as my AI teammate. I pasted my files (app.py, the tests, reflection.md) into the chat and asked it to explain bugs, help refactor the logic into logic_utils.py, and generate pytest cases.

- **AI explanation of a bug:**

  When I saw the same guess of 9 get "Go HIGHER!" and then "Go LOWER!" with a secret of 79, Claude explained that app.py converts the secret to a string on every even attempt (`secret = str(st.session_state.secret)`). Comparing a number to a string raises a TypeError, so check_guess falls into its `except TypeError` block and compares text instead of numbers. Since "9" comes after "7" alphabetically, "9" > "79" is True, so the game called 9 "Too High."


- **Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).**

 Claude suggested changing check_guess to return only the outcome ("Win", "Too High", "Too Low") and moving the hint text into a separate function, get_hint_message. This was correct because the starter tests expected a plain string like "Win," but the original function returned a tuple, so the tests could never pass. Splitting them also made it easy to fix the swapped "Go HIGHER"/"Go LOWER" messages in one place. I verified it by running `python -m pytest`: the 3 starter tests went from 3 failed to 3 passed without changing them. I also played the game, guessed higher than the secret, and saw "Go LOWER!"

- **Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.**

Claude first suggested adding FIXME comments for only the 3 bugs I planned to fix first. I changed that and asked it to mark all 11 bugs from my Bug Reproduction Log, because I wanted every bug in my table connected to the exact line of code causing it, so anyone reading the code could match them up. I verified it by checking that each FIXME was numbered to match my table and sat directly above the code it described, and that the game still ran the same afterward before I committed it.

---

## 3. Debugging and testing your fixes

- **How did you decide whether a bug was really fixed?**

 I counted a bug as fixed only when two things were true: a pytest test targeting that bug passed, and I could no longer reproduce the bug in the live game using the same input from my Bug Reproduction Log. For example, for the backwards hints I guessed higher than the secret and confirmed the game now says "📉 Go LOWER!", and for New Game I won a game, clicked New Game, and saw the score reset to 0 and the History list cleared.

- **Describe at least one test you ran (manual or using pytest) and what it showed you about your code.**

  `test_single_digit_guess_compared_as_number` checks that `check_guess(9, 79)` returns "Too Low." In the original code, a guess of 9 against a secret of 79 got "Too High" on even attempts because the secret was turned into a string and "9" > "79" as text. The test passing shows the comparison is now always numeric. Before my fixes, `python -m pytest` showed **3 failed** (NotImplementedError, because logic_utils.py was empty). After moving the logic and fixing it, all **19 tests pass**:

```
  tests/test_game_logic.py::test_winning_guess PASSED
  tests/test_game_logic.py::test_guess_too_high PASSED
  tests/test_game_logic.py::test_guess_too_low PASSED
  tests/test_game_logic.py::test_too_high_hint_says_go_lower PASSED
  tests/test_game_logic.py::test_too_low_hint_says_go_higher PASSED
  tests/test_game_logic.py::test_single_digit_guess_compared_as_number PASSED
  tests/test_game_logic.py::test_same_guess_gives_same_result_every_time PASSED
  tests/test_game_logic.py::test_out_of_range_guess_rejected_on_easy PASSED
  tests/test_game_logic.py::test_non_numeric_input_rejected PASSED
  tests/test_game_logic.py::test_wrong_guess_never_adds_points PASSED
  tests/test_game_logic.py::test_first_try_win_scores_100 PASSED
  tests/test_game_logic.py::test_hard_range_bigger_than_normal PASSED
  tests/test_game_logic.py::test_negative_number_rejected PASSED
  tests/test_game_logic.py::test_decimal_rejected_not_truncated PASSED
  tests/test_game_logic.py::test_extremely_large_number_rejected PASSED
  tests/test_game_logic.py::test_empty_input_rejected PASSED
  tests/test_game_logic.py::test_whitespace_around_number_accepted PASSED
  tests/test_game_logic.py::test_boundary_values PASSED
  tests/test_game_logic.py::test_win_score_never_below_10 PASSED
  ============================= 19 passed in 0.08s ==============================
```

  I also ran into a setup issue: plain `pytest` failed with `ModuleNotFoundError: No module named 'logic_utils'`, because pytest wasn't adding the project folder to Python's import path. Running `python -m pytest` instead fixed it.

- **Did AI help you design or understand any tests? How?**

  Yes. Claude generated the bug-fix tests and the edge-case tests (negative numbers, decimals, extremely large numbers, empty input, extra spaces, and the exact edges of the range). I read each one to make sure it matched a bug from my table and checked that the expected values made sense, for example that 1 and 20 are allowed on Easy but 0 and 21 are not. The edge cases also made me realize that inputs like "4.9" used to be silently cut to 4, which I hadn't noticed while playing.

---

## 4. What did you learn about Streamlit and state?

- **How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?**

  Before this project I didn't know what Streamlit or session state were. Streamlit is a Python library that turns a Python script into a web page, and I learned that every time you click a button or change a setting, it reruns the entire script from top to bottom. That means normal variables reset on every click, so anything the game needs to remember, like the secret number, score, attempts, and guess history, has to be saved in `st.session_state`, which acts like the app's memory between reruns. 

  The way I would explain to a friend would be: Imagine a whiteboard that gets completely erased and redrawn every time you touch it. Because of this, regular variables forget everything on each click. Session state (`st.session_state`) is like a notebook next to the whiteboard that doesn't get erased, so anything the app needs to remember between clicks has to be saved there.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.

I want to keep reproducing a bug and writing down the exact input, expected result, and actual result before trying to fix anything. Having the Bug Reproduction Log made it easy to check each fix later, because I could repeat the same input and see if the behavior changed. I also want to keep committing at milestones instead of all at once, since it shows the story of how the project changed.

- What is one thing you would do differently next time you work with AI on a coding task?

I would slow down and go one step at a time from the beginning. Early on, the AI was giving me several steps at once and I got lost, so I had to stop and ask it to go step by step. I would also question the AI's reasoning sooner: when I asked why Hard mode was set to 1–200 with 5 tries, the AI worked out that a perfect player would need 8 guesses for that range, which made me realize its suggestions are choices I can push back on, not facts. 

- In one or two sentences, describe how this project changed the way you think about AI generated code.

 AI-generated code can look finished and still be full of bugs. This game ran without crashing but had at least 11 problems. Now I see AI as a fast teammate that still needs a human in the loop to test, verify, and decide what to accept.