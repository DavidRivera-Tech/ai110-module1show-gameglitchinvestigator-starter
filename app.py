import random
from pathlib import Path

import streamlit as st

# FIX: Refactored game logic out of app.py into logic_utils.py (done with
# Claude), so the rules can be tested with pytest separately from the UI.
from logic_utils import (
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    get_temperature,
    load_high_scores,
    parse_guess,
    save_high_scores,
    update_high_score,
    update_score,
)

# FEATURE (Challenge 2): High scores are saved next to app.py, so they
# survive closing and reopening the game.
HIGH_SCORES_PATH = str(Path(__file__).with_name("high_scores.json"))


def start_new_game(low: int, high: int, difficulty: str) -> None:
    """Reset every piece of game state for a fresh game.

    Args:
        low: The smallest possible secret number.
        high: The largest possible secret number.
        difficulty: The difficulty this game is being played on.
    """
    # FIX (Bug #3): New Game used to reset only attempts and secret. Now
    # it resets status, score, and history too, and picks the secret from
    # the current difficulty's range.
    st.session_state.secret = random.randint(low, high)
    # FIX (Bug #1): Attempts start at 0, so "Attempts left" matches
    # "Attempts allowed".
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    # FEATURE (Challenge 4): One row per valid guess for the session
    # summary table.
    st.session_state.guess_log = []
    st.session_state.difficulty = difficulty


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

# FEATURE (Challenge 2): Reserve a sidebar spot for the high scores and
# fill it in at the END, so a new record shows up right away (same idea
# as the Bug #10 fix).
high_score_box = st.sidebar.empty()

# FEATURE: Explain the scoring rules (from update_score in logic_utils.py)
# so players know why their score goes up or down.
with st.sidebar.expander("ℹ️ How scoring works"):
    st.markdown(
        "Your score has two parts:\n\n"
        "1. ❌ **Each wrong guess:** -5 points\n"
        "2. 🎯 **Win bonus:** 100 if you win on guess 1, 90 on guess 2, "
        "80 on guess 3, and so on (never less than 10)\n\n"
        "**Example:** miss, miss, then win on guess 3 "
        "→ -5 - 5 + 80 = **70**\n\n"
        "⚠️ Invalid input (like `abc`) costs nothing and doesn't use "
        "an attempt. 🏆 Only wins count toward your high score."
    )

# FIX (Bug #9): Start a fresh game on first load AND whenever the
# difficulty changes, so the secret is always inside the selected range.
difficulty_changed = st.session_state.get("difficulty") != difficulty
missing_state = "secret" not in st.session_state or (
    "guess_log" not in st.session_state
)
if missing_state or difficulty_changed:
    start_new_game(low, high, difficulty)

st.subheader("Make a guess")

# FIX (Bug #10): Reserve a spot for the info box now, but fill it in at
# the END, after the guess is processed, so "Attempts left" is never one
# step behind.
info_box = st.empty()

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game(low, high, difficulty)
    st.success("New game started.")

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

elif submit:
    # FIX (Bug #2): Pass the current range so out-of-range guesses are
    # rejected.
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX (Bug #8): Invalid input shows an error but does NOT use up
        # an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX (Bug #6, part 1 of 2): Removed the code that turned the
        # secret into a string on even attempts. The secret is always
        # compared as a number now.
        outcome = check_guess(guess_int, st.session_state.secret)
        hint = get_hint_message(outcome)
        label, emoji, color = get_temperature(
            guess_int, st.session_state.secret, low, high
        )

        if show_hint:
            # FIX (Bug #5): Hint text now comes from get_hint_message(),
            # where the swapped "Go HIGHER"/"Go LOWER" messages were
            # corrected.
            # FEATURE (Challenge 4): The hint is color-coded by how close
            # the guess was, with a hot/cold emoji.
            direction = "" if outcome == "Win" else f" {hint}"
            st.markdown(f"### :{color}[{emoji} {label}!]{direction}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        st.session_state.guess_log.append(
            {
                "Attempt": st.session_state.attempts,
                "Guess": guess_int,
                "Hint": hint,
                "Temperature": f"{emoji} {label}",
                "Score": st.session_state.score,
            }
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
            # FEATURE (Challenge 2): Save the score if it beats the best
            # score for this difficulty. Only wins count.
            high_scores, is_record = update_high_score(
                load_high_scores(HIGH_SCORES_PATH),
                difficulty,
                st.session_state.score,
            )
            if is_record:
                try:
                    save_high_scores(high_scores, HIGH_SCORES_PATH)
                    st.success(f"🏆 New high score for {difficulty}!")
                except OSError:
                    st.warning("Couldn't save the high score file.")
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"Out of attempts! "
                f"The secret was {st.session_state.secret}. "
                f"Score: {st.session_state.score}"
            )

# FIX (Bug #7): Message uses the real range for the selected difficulty
# instead of always saying "1 and 100".
info_box.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

# FEATURE (Challenge 2): Show the best score for every difficulty.
saved_scores = load_high_scores(HIGH_SCORES_PATH)
with high_score_box.container():
    st.subheader("🏆 High Scores")
    for level in ["Easy", "Normal", "Hard"]:
        best = saved_scores.get(level)
        st.caption(f"{level}: {best if best is not None else '—'}")

# FEATURE (Challenge 4): Session summary table of every valid guess in
# this game, so the player can see how they homed in on the secret.
if st.session_state.guess_log:
    st.subheader("📊 Session Summary")
    st.dataframe(st.session_state.guess_log, hide_index=True)

# FIX (Bug #10): Debug panel moved to the end so it shows the state AFTER
# the latest guess.
with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
