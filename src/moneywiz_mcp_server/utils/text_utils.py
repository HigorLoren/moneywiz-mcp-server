"""Text normalization utilities for MoneyWiz MCP Server."""


def normalize_category_name(name: str) -> str:
    """Normalize whitespace in a category name for comparison purposes.

    MoneyWiz's default category set stores some names (typically ones
    with "&") using non-breaking spaces (U+00A0) instead of regular
    spaces. They render identically, so a user-typed filter with normal
    spaces silently fails to match. str.split() treats NBSP as
    whitespace, so this collapses any whitespace run to a single
    regular space without altering the displayed name elsewhere.
    """
    return " ".join(name.split())
