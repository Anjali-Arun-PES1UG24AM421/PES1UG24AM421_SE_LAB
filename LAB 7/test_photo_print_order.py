import math
from hypothesis import given, strategies as st
from photo_print_order import parse_order, file_size_average, payable_amount

# Anything a caller might throw at the functions: text, None, numbers, bytes, lists
anything = st.one_of(
    st.text(),
    st.none(),
    st.integers(),
    st.floats(),
    st.binary(),
    st.lists(st.integers()),
)


# ---------- parse_order ----------
@given(st.text() | st.none())
def test_parse_order_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(anything)
def test_parse_order_any_type_no_crash(s):
    try:
        parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"


@given(anything)
def test_parse_order_result_shape(s):
    result = parse_order(s)
    if result is not None:
        size, copies = result
        assert isinstance(size, str) and size != ""
        assert size == size.strip().upper()
        assert isinstance(copies, int) and copies >= 0


@given(st.sampled_from(["4x6", "5x7", "8x10"]), st.integers(min_value=0, max_value=10**6))
def test_parse_order_valid_roundtrip(size, copies):
    assert parse_order(f" {size}:{copies} ") == (size.upper(), copies)


# ---------- file_size_average ----------
@given(st.text() | st.none())
def test_file_size_average_no_crash(s):
    try:
        file_size_average(s)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(anything)
def test_file_size_average_any_type_no_crash(s):
    try:
        file_size_average(s)
    except Exception as e:
        assert False, f"file_size_average crashed with: {e!r}"


@given(anything)
def test_file_size_average_result_shape(s):
    result = file_size_average(s)
    if result is not None:
        assert isinstance(result, int) and result >= 0


@given(st.lists(st.integers(min_value=0, max_value=10**6), min_size=1))
def test_file_size_average_between_min_and_max(values):
    csv = ",".join(str(v) for v in values)
    assert min(values) <= file_size_average(csv) <= max(values)


# ---------- payable_amount ----------
@given(st.text() | st.none())
def test_payable_amount_no_crash(s):
    try:
        payable_amount(s)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


@given(anything)
def test_payable_amount_any_type_no_crash(s):
    try:
        payable_amount(s)
    except Exception as e:
        assert False, f"payable_amount crashed with: {e!r}"


@given(anything)
def test_payable_amount_result_shape(s):
    result = payable_amount(s)
    if result is not None:
        assert isinstance(result, (int, float))
        assert math.isfinite(result) and result >= 0


@given(
    st.floats(min_value=0, max_value=1e9, allow_nan=False),
    st.floats(min_value=0, max_value=1e9, allow_nan=False),
)
def test_payable_amount_valid_inputs(amount, discount):
    result = payable_amount(f"{amount}|{discount}")
    assert result is not None
    assert math.isfinite(result) and result >= 0
