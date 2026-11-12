from hypothesis import given, strategies as st
from processor import (
    lookup_drink_code,
    calculate_average_shot_cost,
    parse_order_modifiers,
)


@given(st.text() | st.none())
def test_lookup_drink_code_no_crash(s):
    # Property: the function must never crash, whatever string (or None) it gets.
    try:
        lookup_drink_code(s)
    except Exception as e:
        assert False, f"lookup_drink_code crashed with {type(e).__name__}: {e} on input {s!r}"


@given(st.text() | st.none())
def test_calculate_average_shot_cost_safe(s):
    # Property: averaging must handle non-numeric, empty and None input without crashing.
    try:
        calculate_average_shot_cost(s)
    except Exception as e:
        assert False, f"calculate_average_shot_cost crashed with {type(e).__name__}: {e} on input {s!r}"


@given(st.text() | st.none())
def test_parse_order_modifiers_safe(s):
    # Property: parsing modifiers must handle missing/extra ':' and None without crashing.
    try:
        parse_order_modifiers(s)
    except Exception as e:
        assert False, f"parse_order_modifiers crashed with {type(e).__name__}: {e} on input {s!r}"