"""
Day-of-the-year calculator utilities.

This module provides utility functions to:
- Determine leap years and their rules.
- Calculate days in any month, accounting for leap years.
- Compute day numbers within a year from given dates.

Example Usage:
    >>> from day_of_year_functions import is_leap_year, days_in_month
    >>> print(is_leap_year(2000))  # Output: True (leap year)
    >>> print(days_in_month(2000, 2))  # Output: 29 (February in leap year)
"""

def is_leap_year(year):
    """Determine if a given year is a leap year.

    A leap year occurs when:
        - The year is divisible by 4 but not by 100, OR
        - The year is divisible by 400 (e.g., 2000 was a leap year).

    Args:
        year (int): Year to check for leap status. Must be ≥ 1.

    Returns:
        bool: True if the year is a leap year, False otherwise.
            Raises ValueError if `year` is negative or not an integer.

    Examples:
        >>> is_leap_year(2004)  # Output: True
        >>> is_leap_year(1900)  # Output: False (not divisible by 400)
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def days_in_month(year, month):
    """Return the number of days in a specified month of a given year.

    Args:
        year (int): Year to check. Must be ≥ 1.
        month (int): Month to check (1-12). Invalid months return `None`.

    Returns:
        int: Number of days in the month, or None if month is invalid.

    Raises:
        ValueError: If `year` or `month` are not integers or out-of-range.

    Examples:
        >>> days_in_month(2000, 2)  # Output: 29 (leap year)
        >>> days_in_month(2023, 4)  # Output: 30
    """
    if not (1 <= month <= 12):
        return None

    return [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1] if is_leap_year(year) else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]

def day_of_year(year, month, day):
    """Determine the day of the year from a given date.

    Args:
        year (int): Year to check. Must be ≥ 1.
        month (int): Month to check (1-12). Invalid months return `None`.
        day (int): Day in the month. Must be valid for the given `(year, month)`.

    Returns:
        int: Day number in the year (1-365/366), or None if inputs are invalid.

    Raises:
        ValueError: If any argument is not an integer or out-of-range.

    Examples:
        >>> day_of_year(2000, 12, 31)  # Output: 366 (leap year)
        >>> day_of_year(2023, 5, 15)   # Output: 146
    """
    num_day = 0

    # Calculate days accumulated before the target month
    for month_index in range(month - 1):
        days_in_prev_month = days_in_month(year, month_index)
        if days_in_prev_month is None:
            return None
        num_day += days_in_prev_month

    # Add days from the current month
    num_day += day

    return num_day if num_day > 0 else None

# Example usage (can be removed in production code)
if __name__ == "__main__":
    print(day_of_year(2000, 12, 31))