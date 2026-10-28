import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ---------- process_order_batch : line-hitting cases ----------

def test_small_plain_completed():
    # size 'small' line + COMPLETED return (no customizations, not member)
    orders = [{"paid": True, "size": "small", "customizations": []}]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 3.0, "status": "COMPLETED"}


def test_medium_member_standard_mod():
    # size 'medium' line, 'else' customization line, member-discount line
    orders = [{
        "paid": True, "size": "medium", "is_member": True,
        "customizations": [{"type": "standard", "cost": 0.5}],
    }]
    result = process_order_batch(orders, 0.1)
    # 4.5 + 0.5 = 5.0 -> *0.9 member = 4.5 -> *1.1 tax = 4.95
    assert result == {"total": 4.95, "status": "COMPLETED"}


def test_large_syrup_under_and_over_cap():
    # size 'large' line + syrup line (both sides of the 1.5 cap ternary)
    orders = [{
        "paid": True, "size": "large",
        "customizations": [{"type": "syrup", "cost": 1.0},
                           {"type": "syrup", "cost": 2.0}],
    }]
    result = process_order_batch(orders, 0.0)
    # 6.0 + 1.0 + 1.5(capped) = 8.5
    assert result == {"total": 8.5, "status": "COMPLETED"}


def test_unpaid_skip_and_invalid_size_reject():
    # 'continue' for unpaid order + 'else' reject line for invalid size + NO_SALE
    orders = [{"paid": False, "size": "small"},
              {"paid": True, "size": "jumbo"}]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_negative_cost_mod_rejected():
    # 'cost < 0' reject+continue line
    orders = [{
        "paid": True, "size": "small",
        "customizations": [{"type": "syrup", "cost": -1.0},
                           {"type": "syrup", "cost": 0.5}],
    }]
    result = process_order_batch(orders, 0.0)
    # 3.0 + 0.5 = 3.5  (negative mod skipped)
    assert result == {"total": 3.5, "status": "COMPLETED"}


def test_allergen_strict_breaks_to_zero():
    # allergen_alert line + strict_allergy True branch (item_total=0, break)
    orders = [{
        "paid": True, "size": "medium", "strict_allergy": True,
        "customizations": [{"type": "allergen_alert", "cost": 0.0},
                           {"type": "syrup", "cost": 1.0}],
    }]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_audit_rejected_over_four():
    # rejected_items > 4 -> AUDIT_REJECTED line
    orders = [{"paid": True, "size": "jumbo"} for _ in range(5)]
    orders.append({"paid": True, "size": "small", "customizations": []})
    result = process_order_batch(orders, 0.0)
    # 5 invalid sizes rejected, one valid small = 3.0
    assert result == {"total": 3.0, "status": "AUDIT_REJECTED"}


def test_invalid_input_raises():
    # 'raise ValueError' line (both: not a list, and negative tax)
    with pytest.raises(ValueError):
        process_order_batch("not_a_list", 0.1)
    with pytest.raises(ValueError):
        process_order_batch([], -0.5)


# ---------- check_espresso_machine : line-hitting cases ----------

def test_machine_no_data():
    # 'NO_DATA' line
    assert check_espresso_machine([]) == "NO_DATA"


def test_machine_optimal():
    # OPTIMAL line + overheat increment + reset (else) line
    assert check_espresso_machine([[95.0, 97.0, 90.0]]) == "OPTIMAL"


def test_machine_shutdown():
    # SHUTDOWN line (two consecutive temps > 96.0)
    assert check_espresso_machine([[97.0, 98.0]]) == "SHUTDOWN"