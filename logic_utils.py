"""Core game logic for Game Glitch Investigator (kept separate from the Streamlit UI)."""


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIX (Bug #4): Hard now uses 1-200 so it is actually harder than Normal (1-100).
    # Moved from app.py into logic_utils.py with Claude's help.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(raw, low: int = 1, high: int = 100):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    raw = str(raw).strip()
    if raw == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw)
    except ValueError:
        # FIX: Decimals like "4.9" used to be silently cut to 4; now the player is told why.
        try:
            float(raw)
        except ValueError:
            return False, None, "That is not a number."
        return False, None, "Please enter a whole number."

    # FIX (Bug #2): Added a range check so 101, 0, or -20 are rejected on Easy (1-20).
    # Suggested by Claude; low/high are passed in from app.py based on difficulty.
    if value < low or value > high:
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """
    Compare guess to secret and return the outcome.

    outcome: "Win", "Too High", or "Too Low"
    """
    # FIX (Bug #6, part 2 of 2): Removed the TypeError/string fallback. Both values are
    # always ints now, so "9" vs "79" text comparison can no longer happen.
    # FIX: Returns only the outcome (not a tuple) so the starter tests pass unchanged.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str) -> str:
    """Return the hint text shown to the player for a given outcome."""
    # FIX (Bug #5): Messages were swapped. A guess that is too high now says "Go LOWER".
    # Claude suggested splitting the message out of check_guess so it is easy to test.
    messages = {
        "Win": "🎉 Correct!",
        "Too High": "📉 Go LOWER!",
        "Too Low": "📈 Go HIGHER!",
    }
    return messages.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Update score based on outcome and attempt number (attempt_number starts at 1)."""
    if outcome == "Win":
        # FIX: Uses (attempt_number - 1) so a first-try win is worth 100 points,
        # since attempts now start counting at 0 (see Bug #1 fix in app.py).
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # FIX (Bug #11): Every wrong guess now costs 5 points. Before, "Too High" on even
    # attempts ADDED 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
