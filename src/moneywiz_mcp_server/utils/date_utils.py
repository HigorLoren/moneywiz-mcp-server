"""Date utility functions for MoneyWiz MCP Server."""

import calendar
from datetime import datetime, timedelta
import re

from moneywiz_mcp_server.models.transaction import DateRange

_MONTH_NAMES = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

_RELATIVE_UNIT_RE = re.compile(r"last\s+(\d+)\s+(day|days|month|months|year|years)")
_YEAR_ONLY_RE = re.compile(r"(?:in\s+)?(\d{4})")
_MONTH_YEAR_RE = re.compile(r"([a-z]+)\s+(\d{4})")


def get_date_range_from_months(months: int) -> DateRange:
    """
    Create a DateRange for the last N months.

    Args:
        months: Number of months to go back

    Returns:
        DateRange covering the last N months
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)  # Approximate

    return DateRange(start_date=start_date, end_date=end_date)


def get_date_range_from_days(days: int) -> DateRange:
    """
    Create a DateRange for the last N days.

    Args:
        days: Number of days to go back

    Returns:
        DateRange covering the last N days
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    return DateRange(start_date=start_date, end_date=end_date)


def parse_natural_language_date(text: str) -> DateRange:
    """
    Parse natural language date expressions.

    Args:
        text: Natural language date expression

    Returns:
        DateRange corresponding to the expression

    Raises:
        ValueError: If the expression doesn't match any supported format

    Examples:
        "last 3 months" -> DateRange for last 3 months
        "last 45 days" -> DateRange for last 45 days
        "last month"/"last year" -> DateRange for the preceding period
        "this year"/"this month" -> DateRange for the current period
        "2023" / "in 2023" -> DateRange spanning that calendar year
        "January 2023" -> DateRange spanning that calendar month
    """
    original = text
    text = text.lower().strip()

    if text == "this year":
        now = datetime.now()
        return DateRange(start_date=datetime(now.year, 1, 1), end_date=now)

    if text == "this month":
        now = datetime.now()
        return DateRange(start_date=datetime(now.year, now.month, 1), end_date=now)

    if text == "last month":
        return get_date_range_from_months(1)

    if text == "last week":
        return get_date_range_from_days(7)

    if text == "last year":
        return get_date_range_from_months(12)

    relative_match = _RELATIVE_UNIT_RE.search(text)
    if relative_match:
        count = int(relative_match.group(1))
        unit = relative_match.group(2)
        if unit in ("day", "days"):
            return get_date_range_from_days(count)
        if unit in ("month", "months"):
            return get_date_range_from_months(count)
        return get_date_range_from_months(count * 12)  # year/years

    year_match = _YEAR_ONLY_RE.fullmatch(text)
    if year_match:
        return _year_date_range(int(year_match.group(1)))

    month_year_match = _MONTH_YEAR_RE.fullmatch(text)
    if month_year_match and month_year_match.group(1) in _MONTH_NAMES:
        month = _MONTH_NAMES[month_year_match.group(1)]
        year = int(month_year_match.group(2))
        return _month_date_range(year, month)

    raise ValueError(
        f"Could not parse time period '{original}'. Supported formats: "
        "'last N days/months/years', 'last week/month/year', 'this month', "
        "'this year', a bare year like '2023', or 'Month YYYY' like "
        "'January 2023'."
    )


def _year_date_range(year: int) -> DateRange:
    """Build a DateRange spanning a calendar year, capped at now."""
    now = datetime.now()
    start_date = datetime(year, 1, 1)
    end_date = now if year >= now.year else datetime(year, 12, 31, 23, 59, 59)
    return DateRange(start_date=start_date, end_date=end_date)


def _month_date_range(year: int, month: int) -> DateRange:
    """Build a DateRange spanning a calendar month, capped at now."""
    now = datetime.now()
    start_date = datetime(year, month, 1)
    if (year, month) >= (now.year, now.month):
        end_date = now
    else:
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)
    return DateRange(start_date=start_date, end_date=end_date)


def core_data_timestamp_to_datetime(timestamp: float) -> datetime:
    """
    Convert Core Data timestamp to Python datetime.

    Core Data uses NSDate which counts seconds since 2001-01-01 00:00:00 UTC.

    Args:
        timestamp: Core Data timestamp

    Returns:
        Python datetime object
    """
    # NSDate epoch: January 1, 2001 00:00:00 UTC
    nsdate_epoch = datetime(2001, 1, 1)
    return datetime.fromtimestamp(nsdate_epoch.timestamp() + timestamp)


def datetime_to_core_data_timestamp(dt: datetime) -> float:
    """
    Convert Python datetime to Core Data timestamp.

    Args:
        dt: Python datetime object

    Returns:
        Core Data timestamp
    """
    nsdate_epoch = datetime(2001, 1, 1)
    return dt.timestamp() - nsdate_epoch.timestamp()


def format_date_range_for_display(date_range: DateRange) -> str:
    """
    Format a DateRange for user display.

    Args:
        date_range: DateRange to format

    Returns:
        Human-readable date range string
    """
    start_str = date_range.start_date.strftime("%Y-%m-%d")
    end_str = date_range.end_date.strftime("%Y-%m-%d")

    return f"{start_str} to {end_str}"
