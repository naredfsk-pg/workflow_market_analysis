from datetime import datetime, date


class MarketSchedule:
    def __init__(self):
        self.holidays = {
            date(2024, 1, 1),
            date(2024, 1, 15),
            date(2024, 2, 19),
            date(2024, 3, 29),
            date(2024, 5, 27),
            date(2024, 6, 19),
            date(2024, 7, 4),
            date(2024, 9, 2),
            date(2024, 11, 28),
            date(2024, 12, 25),
            date(2025, 1, 1),
            date(2025, 1, 20),
            date(2025, 2, 17),
            date(2025, 4, 18),
            date(2025, 5, 26),
            date(2025, 6, 19),
            date(2025, 7, 4),
            date(2025, 9, 1),
            date(2025, 11, 27),
            date(2025, 12, 25),
        }

    def is_trading_day(self, check_date=None):
        if check_date is None:
            check_date = datetime.now().date()

        if check_date.weekday() >= 5:
            return False

        if check_date in self.holidays:
            return False

        return True
