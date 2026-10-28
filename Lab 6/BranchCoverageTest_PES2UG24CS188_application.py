
import pytest
from coffee_shop_order import process_order_batch, check_espresso_machine


# ---------- process_order_batch ----------

def test_invalid_input_not_list():
    # if-guard True side (not a list)
    with pytest.raises(ValueError):
        process_order_batch("not_a_list", 0.1)


def test_invalid_input_negative_tax():
    # if-guard True side (negative tax rate)
    with pytest.raises(ValueError):
        process_order_batch([], -0.5)


def test_empty_orders_no_sale():
    # if-guard False side + for-loop body never entered + NO_SALE
    result = process_order_batch([], 0.0)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_unpaid_order_skipped():
    # 'paid' guard True (unpaid -> continue) and False (paid) both exercised
    orders = [{"paid": False, "size": "small"},
              {"paid": True, "size": "small", "customizations": []}]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 3.0, "status": "COMPLETED"}


def test_small_size():
    orders = [{"paid": True, "size": "small", "customizations": []}]
    assert process_order_batch(orders, 0.0)["total"] == 3.0


def test_medium_size_member_else_mod():
    # medium branch, 'else' customization branch, member True branch
    orders = [{
        "paid": True, "size": "medium", "is_member": True,
        "customizations": [{"type": "standard", "cost": 0.5}],
    }]
    assert process_order_batch(orders, 0.1)["total"] == 4.95


def test_large_syrup_cap_both_sides():
    # large branch, syrup branch, cost<=1.5 True and False
    orders = [{
        "paid": True, "size": "large",
        "customizations": [{"type": "syrup", "cost": 1.0},
                           {"type": "syrup", "cost": 2.0}],
    }]
    assert process_order_batch(orders, 0.0)["total"] == 8.5


def test_invalid_size_rejected():
    # else branch of the size decision (reject + continue)
    orders = [{"paid": True, "size": "jumbo"}]
    result = process_order_batch(orders, 0.0)
    assert result == {"total": 0.0, "status": "NO_SALE"}


def test_negative_cost_mod_branch():
    # cost < 0 True branch (skip mod) and False branch (apply mod)
    orders = [{
        "paid": True, "size": "small",
        "customizations": [{"type": "syrup", "cost": -1.0},
                           {"type": "syrup", "cost": 0.5}],
    }]
    assert process_order_batch(orders, 0.0)["total"] == 3.5


def test_allergen_strict_true_breaks():
    # allergen_alert True + strict_allergy True (item_total=0, break)
    orders = [{
        "paid": True, "size": "medium", "strict_allergy": True,
        "customizations": [{"type": "allergen_alert", "cost": 0.0},
                           {"type": "syrup", "cost": 1.0}],
    }]
    assert process_order_batch(orders, 0.0) == {"total": 0.0, "status": "NO_SALE"}


def test_allergen_strict_false_no_break():
    # allergen_alert True + strict_allergy False (no break, continue processing)
    orders = [{
        "paid": True, "size": "medium", "strict_allergy": False,
        "customizations": [{"type": "allergen_alert", "cost": 0.0},
                           {"type": "standard", "cost": 1.0}],
    }]
    result = process_order_batch(orders, 0.0)
    # 4.5 + 1.0 = 5.5 ; one rejected (allergen), status still COMPLETED
    assert result == {"total": 5.5, "status": "COMPLETED"}


def test_non_member_branch():
    # is_member False branch (no discount applied)
    orders = [{"paid": True, "size": "small", "is_member": False,
               "customizations": []}]
    assert process_order_batch(orders, 0.0)["total"] == 3.0


def test_audit_rejected_branch():
    # rejected_items > 4 True branch -> AUDIT_REJECTED
    orders = [{"paid": True, "size": "jumbo"} for _ in range(5)]
    orders.append({"paid": True, "size": "small", "customizations": []})
    assert process_order_batch(orders, 0.0)["status"] == "AUDIT_REJECTED"


# ---------- check_espresso_machine ----------

def test_machine_no_data_branch():
    # 'not temperature_cycles' True branch
    assert check_espresso_machine([]) == "NO_DATA"


def test_machine_empty_cycle_inner_loop_skipped():
    # not-empty outer list (False side of guard) but empty inner cycle
    # -> inner for-loop body never entered, returns OPTIMAL
    assert check_espresso_machine([[]]) == "OPTIMAL"


def test_machine_optimal_with_reset():
    # temp > 96 True (streak=1, <2) and False (else: reset) both exercised
    assert check_espresso_machine([[95.0, 97.0, 90.0]]) == "OPTIMAL"


def test_machine_shutdown_branch():
    # overheat_streak >= 2 True branch -> SHUTDOWN
    assert check_espresso_machine([[97.0, 98.0]]) == "SHUTDOWN"