import pytest
from photo_print_order import extra_print_charge, order_valid, dispatch_status

# ---------- extra_print_charge ----------
def test_within_included_prints():
    assert extra_print_charge("4x6", 15, "matte", False) == 0

def test_unknown_size():
    with pytest.raises(ValueError, match="unknown print size"):
        extra_print_charge("11x14", 5, "matte", False)

def test_negative_copies():
    with pytest.raises(ValueError, match="invalid copies"):
        extra_print_charge("4x6", -1, "matte", False)

def test_zero_copies():
    assert extra_print_charge("4x6", 0, "matte", False) == 0

def test_exactly_included_boundary():
    # extra == 0 -> still free
    assert extra_print_charge("4x6", 20, "matte", False) == 0

def test_member_bonus_applies():
    # 4x6 member: included 25, extra 5 * matte 4
    assert extra_print_charge("4x6", 30, "matte", True) == 20

def test_member_bonus_not_for_8x10():
    # 8x10 member: included stays 10, extra 5 * 4
    assert extra_print_charge("8x10", 15, "matte", True) == 20

def test_non_member_no_bonus():
    # 5x7 non-member: included 15, extra 5 * 7
    assert extra_print_charge("5x7", 20, "glossy", False) == 35

def test_bulk_boundary_50_not_bulk():
    # extra exactly 50 -> no surcharge
    assert extra_print_charge("4x6", 70, "matte", False) == 50 * 4

def test_bulk_boundary_51_is_bulk():
    # extra 51 -> matte rate 4+2 = 6
    assert extra_print_charge("4x6", 71, "matte", False) == 51 * 6

def test_bulk_canvas():
    # extra 60 -> 7+2+5 = 14
    assert extra_print_charge("4x6", 80, "canvas", False) == 60 * 14

def test_bulk_glossy_no_canvas_extra():
    # extra 60 -> 7+2 = 9
    assert extra_print_charge("4x6", 80, "glossy", False) == 60 * 9

def test_canvas_small_order_no_bulk_surcharge():
    # extra 5 -> canvas falls into "else" rate 7, no bulk surcharge
    assert extra_print_charge("4x6", 25, "canvas", False) == 35

# ---------- order_valid ----------
def test_order_valid():
    assert order_valid(10, 100, False) is True

def test_rush_within_limit():
    assert order_valid(10, 50, True) is True

def test_rush_over_limit():
    assert order_valid(10, 51, True) is False

def test_rush_ignores_file_size():
    assert order_valid(100, 10, True) is True

def test_file_too_large():
    assert order_valid(26, 100, False) is False

def test_file_size_boundary_25():
    assert order_valid(25, 100, False) is True

def test_copies_boundary_500():
    assert order_valid(10, 500, False) is True

def test_copies_over_500():
    assert order_valid(10, 501, False) is False

# ---------- dispatch_status ----------
def test_on_time_standard():
    assert dispatch_status(12, False, False) == "on_time"

def test_tight_standard():
    assert dispatch_status(6, False, False) == "tight"

def test_missed_standard():
    assert dispatch_status(5, False, False) == "missed"

def test_on_time_framed():
    assert dispatch_status(24, True, False) == "on_time"

def test_tight_framed():
    assert dispatch_status(18, True, False) == "tight"

def test_missed_framed():
    assert dispatch_status(17, True, False) == "missed"

def test_international_on_time():
    assert dispatch_status(36, False, True) == "on_time"

def test_international_framed_tight():
    # cutoff 48, tight window 42..47
    assert dispatch_status(42, True, True) == "tight"

def test_international_missed():
    assert dispatch_status(10, False, True) == "missed"
