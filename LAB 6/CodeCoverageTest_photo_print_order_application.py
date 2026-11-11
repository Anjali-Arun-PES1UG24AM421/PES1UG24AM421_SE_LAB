import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status

# ---------- extra_print_charge ----------
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0

def test_unknown_size():
    with pytest.raises(ValueError):
        extra_print_charge("11x14", 5, "matte", False)

def test_negative_copies():
    with pytest.raises(ValueError):
        extra_print_charge("4x6", -1, "matte", False)

def test_member_bonus_matte():
    # 4x6 member: included 25, copies 30 -> extra 5 * 4
    assert extra_print_charge("4x6", 30, "matte", True) == 20

def test_glossy_extra():
    # 4x6 non-member: included 20, extra 5 * 7
    assert extra_print_charge("4x6", 25, "glossy", False) == 35

def test_bulk_canvas():
    # 4x6 non-member: extra 60 -> rate 7+2+5 = 14
    assert extra_print_charge("4x6", 80, "canvas", False) == 60 * 14

# ---------- order_valid ----------
def test_order_valid():
    assert order_valid(10, 100, False) is True

def test_rush_order():
    assert order_valid(10, 40, True) is True

def test_large_file_rejected():
    assert order_valid(30, 100, False) is False

# ---------- dispatch_status ----------
def test_on_time():
    assert dispatch_status(30, True, False) == "on_time"

def test_tight():
    assert dispatch_status(8, False, False) == "tight"

def test_missed():
    assert dispatch_status(1, False, False) == "missed"

def test_international_cutoff():
    assert dispatch_status(40, False, True) == "on_time"
