"""Unit tests for text normalization utilities."""

from moneywiz_mcp_server.utils.text_utils import normalize_category_name


def test_normalize_category_name_collapses_nbsp_to_regular_space():
    """MoneyWiz stores some category names with non-breaking spaces."""
    assert (
        normalize_category_name("Food\xa0&\xa0Suplements\xa0Or\xa0Consumables")
        == "Food & Suplements Or Consumables"
    )


def test_normalize_category_name_matches_regular_space_input():
    stored = "Parking\xa0&\xa0Tolls"
    user_typed = "Parking & Tolls"
    assert normalize_category_name(stored) == normalize_category_name(user_typed)


def test_normalize_category_name_strips_and_collapses_runs():
    assert normalize_category_name("  Groceries   ") == "Groceries"
    assert normalize_category_name("Multi   space  name") == "Multi space name"


def test_normalize_category_name_leaves_plain_names_unchanged():
    assert normalize_category_name("Groceries") == "Groceries"
