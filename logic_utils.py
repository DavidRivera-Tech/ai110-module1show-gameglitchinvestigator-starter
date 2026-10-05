"""Core game logic for Game Glitch Investigator.

These functions hold the rules of the number-guessing game. They are kept
separate from the Streamlit UI in ``app.py`` so they can be tested with
pytest without running the app.
"""


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """Return the inclusive guessing range for a difficulty level.

    Args:
        difficulty: One of ``"Easy"``, ``"Normal"``, or ``"Hard"``.
            Any other value falls back to the Normal range.

    Returns:
        A ``(low, high)`` tuple of the smallest and largest allowed
        guesses.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
    """
    # FIX (Bug #4): Hard now uses 1-200 so it is harder than Normal
    # (1-100). Moved from app.py into logic_utils.py with Claude's help.
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 200
    return 1, 100


def parse_guess(
    raw: str | None, low: int = 1, high: int = 100
) -> tuple[bool, int | None, str | None]:
    """Convert the player's raw text input into a validated integer guess.

    Leading and trailing spaces are ignored. Decimals, non-numbers, empty
    input, and numbers outside ``low``-``high`` are rejected with a
    message the UI can show to the player.

    Args:
        raw: The text the player typed, or ``None`` if nothing was sent.
        low: The smallest allowed guess (inclusive). Defaults to 1.
        high: The largest allowed guess (inclusive). Defaults to 100.

    Returns:
        A tuple ``(ok, value, error)``:

        * ``ok`` -- ``True`` if the input is a valid guess.
        * ``value`` -- the guess as an ``int``, or ``None`` if invalid.
        * ``error`` -- a message for the player, or ``None`` if valid.

    Examples:
        >>> parse_guess(" 7 ", 1, 20)
        (True, 7, None)
        >>> parse_guess("101", 1, 20)
        (False, None, 'Guess must be between 1 and 20.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    raw = str(raw).strip()
    if raw == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw)
    except ValueError:
        # FIX: Decimals like "4.9" used to be silently cut to 4;
        # now the player is told to enter a whole number.
        try:
            float(raw)
        except ValueError:
            return False, None, "That is not a number."
        return False, None, "Please enter a whole number."

    # FIX (Bug #2): Added a range check so 101, 0, or -20 are rejected
    # on Easy (1-20). Suggested by Claude; low/high come from app.py.
    if value < low or value > high:
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """Compare a guess to the secret number.

    Args:
        guess: The player's validated guess.
        secret: The secret number for the current game.

    Returns:
        ``"Win"`` if the guess matches, ``"Too High"`` if it is above the
        secret, or ``"Too Low"`` if it is below the secret.

    Examples:
        >>> check_guess(60, 50)
        'Too High'
    """
    # FIX (Bug #6, part 2 of 2): Removed the TypeError/string fallback.
    # Both values are always ints now, so a text comparison like
    # "9" > "79" can no longer happen.
    # FIX: Returns only the outcome (not a tuple) so the starter tests
    # pass unchanged.
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str) -> str:
    """Return the hint text shown to the player for an outcome.

    Args:
        outcome: The result from :func:`check_guess` (``"Win"``,
            ``"Too High"``, or ``"Too Low"``).

    Returns:
        The message to display, or an empty string for an unknown
        outcome.

    Examples:
        >>> get_hint_message("Too High")
        '📉 Go LOWER!'
    """
    # FIX (Bug #5): Messages were swapped. A guess that is too high now
    # says "Go LOWER". Claude suggested splitting the message out of
    # check_guess so it is easy to test on its own.
    messages = {
        "Win": "🎉 Correct!",
        "Too High": "📉 Go LOWER!",
        "Too Low": "📈 Go HIGHER!",
    }
    return messages.get(outcome, "")


def get_temperature(
    guess: int, secret: int, low: int, high: int
) -> tuple[str, str, str]:
    """Describe how close a guess is to the secret as a hot/cold rating.

    Closeness is measured as a fraction of the difficulty's range, so a
    guess 5 away "feels" the same on Easy (1-20) as a guess 25 away on
    Normal (1-100).

    Args:
        guess: The player's validated guess.
        secret: The secret number for the current game.
        low: The smallest number in the current range.
        high: The largest number in the current range.

    Returns:
        A tuple ``(label, emoji, color)``. ``label`` is one of
        ``"Correct"``, ``"Hot"``, ``"Warm"``, ``"Cool"``, or ``"Cold"``.
        ``color`` is a Streamlit markdown color name used by the UI.

    Examples:
        >>> get_temperature(50, 50, 1, 100)
        ('Correct', '🎯', 'green')
        >>> get_temperature(52, 50, 1, 100)
        ('Hot', '🔥', 'red')
        >>> get_temperature(5, 95, 1, 100)
        ('Cold', '🧊', 'blue')
    """
    # FEATURE (Challenge 4): Hot/cold meter added with Claude. Pure logic
    # only, so it can be unit tested without the Streamlit UI.
    if guess == secret:
        return "Correct", "🎯", "green"

    span = max(high - low, 1)
    closeness = abs(guess - secret) / span

    if closeness <= 0.05:
        return "Hot", "🔥", "red"
    if closeness <= 0.15:
        return "Warm", "☀️", "orange"
    if closeness <= 0.35:
        return "Cool", "🌥️", "gray"
    return "Cold", "🧊", "blue"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """Return the new score after a guess.

    A win earns ``100 - 10 * (attempt_number - 1)`` points, never less
    than 10. Every wrong guess costs 5 points.

    Args:
        current_score: The score before this guess.
        outcome: The result from :func:`check_guess`.
        attempt_number: Which valid guess this was, starting at 1.

    Returns:
        The updated score.

    Examples:
        >>> update_score(0, "Win", 1)
        100
        >>> update_score(0, "Too Low", 3)
        -5
    """
    if outcome == "Win":
        # FIX: Uses (attempt_number - 1) so a first-try win is worth 100
        # points, since attempts now start at 0 (see Bug #1 fix).
        points = 100 - 10 * (attempt_number - 1)
        return current_score + max(points, 10)

    # FIX (Bug #11): Every wrong guess now costs 5 points. Before,
    # "Too High" on even attempts ADDED 5 points.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
