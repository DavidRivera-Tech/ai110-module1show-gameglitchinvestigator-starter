from logic_utils import (
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

# FIX: check_guess now returns just the outcome string ("Win", "Too High",
# "Too Low"), so these starter tests work without changes.


# ---------------------------------------------------------------
# Starter tests (unchanged)
# ---------------------------------------------------------------


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ---------------------------------------------------------------
# Bug fix tests (generated with Claude, reviewed by me)
# ---------------------------------------------------------------


def test_too_high_hint_says_go_lower():
    # Bug #5: a guess that is too high should tell the player to go LOWER
    assert "LOWER" in get_hint_message("Too High")


def test_too_low_hint_says_go_higher():
    # Bug #5: a guess that is too low should tell the player to go HIGHER
    assert "HIGHER" in get_hint_message("Too Low")


def test_single_digit_guess_compared_as_number():
    # Bug #6: 9 vs 79 used to be compared as text ("9" > "79"),
    # giving "Too High"
    assert check_guess(9, 79) == "Too Low"


def test_same_guess_gives_same_result_every_time():
    # Bug #6: the same guess used to flip between hints on even/odd
    # attempts
    results = [check_guess(9, 79) for _ in range(4)]
    assert results == ["Too Low"] * 4


def test_out_of_range_guess_rejected_on_easy():
    # Bug #2: Easy is 1-20, so 101 should be rejected
    ok, value, err = parse_guess("101", 1, 20)
    assert ok is False
    assert value is None
    assert "between 1 and 20" in err


def test_non_numeric_input_rejected():
    # Bug #8 (input side): "abc" is invalid, so app.py does not count it
    # as an attempt
    ok, value, err = parse_guess("abc", 1, 100)
    assert ok is False
    assert err == "That is not a number."


def test_wrong_guess_never_adds_points():
    # Bug #11: "Too High" on an even attempt used to ADD 5 points
    assert update_score(0, "Too High", 2) == -5
    assert update_score(0, "Too Low", 3) == -5


def test_first_try_win_scores_100():
    # Score formula matches attempts starting at 0 (Bug #1 fix)
    assert update_score(0, "Win", 1) == 100


def test_hard_range_bigger_than_normal():
    # Bug #4: Hard used to have a smaller range than Normal
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


# ---------------------------------------------------------------
# Edge-case tests (Challenge 1: Advanced Edge-Case Testing)
# ---------------------------------------------------------------


def test_negative_number_rejected():
    # Edge case: negative numbers are never in range
    ok, value, err = parse_guess("-5", 1, 20)
    assert ok is False
    assert "between 1 and 20" in err


def test_decimal_rejected_not_truncated():
    # Edge case: "4.9" used to be silently cut to 4
    ok, value, err = parse_guess("4.9", 1, 20)
    assert ok is False
    assert err == "Please enter a whole number."


def test_extremely_large_number_rejected():
    # Edge case: a huge number should not crash, just be out of range
    ok, value, err = parse_guess("99999999999999999999", 1, 100)
    assert ok is False
    assert "between 1 and 100" in err


def test_empty_input_rejected():
    # Edge case: submitting nothing
    ok, value, err = parse_guess("", 1, 100)
    assert ok is False
    assert err == "Enter a guess."


def test_whitespace_around_number_accepted():
    # Edge case: " 7 " with spaces should still count as 7
    ok, value, err = parse_guess("  7  ", 1, 20)
    assert ok is True
    assert value == 7


def test_boundary_values():
    # Edge case: the exact ends of the range are allowed, one past them
    # is not
    assert parse_guess("1", 1, 20)[0] is True
    assert parse_guess("20", 1, 20)[0] is True
    assert parse_guess("0", 1, 20)[0] is False
    assert parse_guess("21", 1, 20)[0] is False


def test_win_score_never_below_10():
    # Edge case: winning on a very late attempt still gives at least
    # 10 points
    assert update_score(0, "Win", 20) == 10
