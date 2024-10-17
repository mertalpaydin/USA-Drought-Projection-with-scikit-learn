from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_month_ranges(start_time: str, end_time: str) -> tuple:
    """
    Returns two lists: one with the start of each month and one with the start of the next month
    within the given time range.

    :param start_time: The starting date in the format "YYYY-MM-DD".
    :param end_time: The ending date in the format "YYYY-MM-DD".
    :return: A tuple of two lists: (list of start of months, list of start of next months).
    """

    # Convert input strings to datetime objects
    start_date = datetime.strptime(start_time, "%Y-%m-%d")
    end_date = datetime.strptime(end_time, "%Y-%m-%d")

    # Lists to store the results
    start_dates = []
    next_month_starts = []

    # Iterate over each month between the start and end dates
    current_date = start_date.replace(day=1)  # Ensure we start at the beginning of the first month
    while current_date <= end_date:
        # Append the start of the current month
        start_dates.append(current_date.strftime("%Y-%m-%d"))

        # Append the start of the next month
        next_month_start = (current_date + relativedelta(months=1)).replace(day=1)
        next_month_starts.append(next_month_start.strftime("%Y-%m-%d"))

        # Move to the next month
        current_date = next_month_start

    return start_dates, next_month_starts
