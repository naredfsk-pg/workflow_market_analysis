from datetime import datetime, date


class MarketSchedule:
    def __init__(self):
        # NYSE Holidays for 2024 and 2025
        self.holidays = {
            date(2024, 1, 1),  # New Year's Day
            date(2024, 1, 15),  # Martin Luther King, Jr. Day
            date(2024, 2, 19),  # Washington's Birthday
            date(2024, 3, 29),  # Good Friday
            date(2024, 5, 27),  # Memorial Day
            date(2024, 6, 19),  # Juneteenth National Independence Day
            date(2024, 7, 4),  # Independence Day
            date(2024, 9, 2),  # Labor Day
            date(2024, 11, 28),  # Thanksgiving Day
            date(2024, 12, 25),  # Christmas Day
            date(2025, 1, 1),  # New Year's Day
            date(2025, 1, 20),  # Martin Luther King, Jr. Day
            date(2025, 2, 17),  # Washington's Birthday
            date(2025, 4, 18),  # Good Friday
            date(2025, 5, 26),  # Memorial Day
            date(2025, 6, 19),  # Juneteenth National Independence Day
            date(2025, 7, 4),  # Independence Day
            date(2025, 9, 1),  # Labor Day
            date(2025, 11, 27),  # Thanksgiving Day
            date(2025, 12, 25),  # Christmas Day
        }

    def is_trading_day(self, check_date=None):
        if check_date is None:
            check_date = datetime.now().date()

        # Check if weekend (Saturday=5, Sunday=6)
        if check_date.weekday() >= 5:
            return False

        # Check if holiday
        if check_date in self.holidays:
            return False

        return True
