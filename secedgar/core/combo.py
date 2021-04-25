from datetime import date, timedelta
from functools import reduce

from secedgar.core.daily import DailyFilings
from secedgar.core.quarterly import QuarterlyFilings
from secedgar.exceptions import EDGARQueryError, NoFilingsError
from secedgar.utils import add_quarter, get_month, get_quarter


class ComboFilings:
    """Class for retrieving all filings between specified dates.

    Args:
        start_date (Union[str, datetime.datetime, datetime.date], optional): Date before
            which not to fetch reports. Stands for "date after."
            Defaults to None (will fetch all filings before ``end_date``).
        end_date (Union[str, datetime.datetime, datetime.date], optional):
            Date after which not to fetch reports.
            Stands for "date before." Defaults to today.
        client (secedgar.client._base.AbstractClient, optional): Client to use for fetching data.
            Defaults to ``secedgar.client.NetworkClient`` if none is given.
        entry_filter (function, optional): A boolean function to determine
            if the FilingEntry should be kept. Defaults to `lambda _: True`.
            The ``FilingEntry`` object exposes 7 variables which can be
            used to filter which filings to keep. These are "cik", "company_name",
            "form_type", "date_filed", "file_name", "path", and "num_previously_valid".
        balancing_point (int): Number of days from which to change lookup method from using
            ``DailyFilings`` to ``QuarterlyFilings``. If ``QuarterlyFilings`` is used, an
            additional filter will be added to limit which days are included.
            Defaults to 30.

    .. versionadded:: 0.4.0
    """

    def __init__(self,
                 start_date: date,
                 end_date: date,
                 client=None,
                 entry_filter=lambda _: True,
                 balancing_point=30):
        self.entry_filter = entry_filter
        self.start_date = start_date
        self.end_date = end_date
        self.quarterly = QuarterlyFilings(year=self.start_date.year,
                                          quarter=get_quarter(self.start_date),
                                          client=client,
                                          entry_filter=self.entry_filter)
        self.daily = DailyFilings(date=self.start_date,
                                  client=client,
                                  entry_filter=self.entry_filter)
        self.balancing_point = balancing_point
        self._recompute()

    def _recompute(self):
        """Recompute the best list of quarters and days to use based on the start and end date."""
        current_date = self.start_date
        self.quarterly_date_list = []
        self.daily_date_list = []
        while current_date <= self.end_date:
            current_quarter = get_quarter(current_date)
            current_year = current_date.year
            next_year, next_quarter = add_quarter(current_year, current_quarter)
            next_start_quarter_date = date(next_year, get_month(next_quarter),
                                           1)

            days_till_next_quarter = (next_start_quarter_date -
                                      current_date).days
            days_till_end = (self.end_date - current_date).days
            if days_till_next_quarter <= days_till_end:
                current_start_quarter_date = date(current_year,
                                                  get_month(current_quarter), 1)
                if current_start_quarter_date == current_date:
                    self.quarterly_date_list.append(
                        (current_year, current_quarter, lambda x: True))
                    current_date = next_start_quarter_date
                elif days_till_next_quarter > self.balancing_point:
                    self.quarterly_date_list.append(
                        (current_year, current_quarter,
                         lambda x: date(x['date_filed']) >= self.start_date))
                    current_date = next_start_quarter_date
                else:
                    while current_date < next_start_quarter_date:
                        self.daily_date_list.append(current_date)
                        current_date += timedelta(days=1)
            else:
                if days_till_end > self.balancing_point:
                    if days_till_next_quarter - 1 == days_till_end:
                        self.quarterly_date_list.append(
                            (current_year, current_quarter, lambda x: True))
                        current_date = next_start_quarter_date
                    else:
                        self.quarterly_date_list.append(
                            (current_year, current_quarter,
                             lambda x: date(x['date_filed']) <= self.end_date))
                        current_date = self.end_date
                else:
                    while current_date <= self.end_date:
                        self.daily_date_list.append(current_date)
                        current_date += timedelta(days=1)

    def get_urls(self):
        """Get all urls between ``start_date`` and ``end_date``."""
        # Use functools.reduce for speed
        # see https://stackoverflow.com/questions/10461531/merge-and-sum-of-two-dictionaries
        def reducer(accumulator, dictionary):
            for key, value in dictionary.items():
                accumulator[key] = accumulator.get(key, []) + value
            return accumulator

        list_of_dicts = []
        for (year, quarter, f) in self.quarterly_date_list:
            self.quarterly.year = year
            self.quarterly.quarter = quarter
            self.quarterly.entry_filter = lambda x: f(x) and self.entry_filter(x)
            list_of_dicts.append(self.quarterly.get_urls())

        for d in self.daily_date_list:
            self.daily.date = d
            try:
                list_of_dicts.append(self.daily.get_urls())
            except EDGARQueryError:
                pass

        complete_dictionary = reduce(reducer, list_of_dicts, {})
        return complete_dictionary

    def save(self,
             directory,
             dir_pattern=None,
             file_pattern="{accession_number}",
             download_all=False,
             daily_date_format="%Y%m%d"):
        """Save all filings between ``start_date`` and ``end_date``.

        Only filings that satisfy args given at initialization will
        be saved.

        Args:
            directory (str): Directory where filings should be stored.
            dir_pattern (str, optional): Format string for subdirectories. Defaults to None.
            file_pattern (str, optional): Format string for files. Defaults to "{accession_number}".
            download_all (bool, optional): Type of downloading system, if true downloads
                all data for each day, if false downloads each file in index.
                Defaults to False.
            daily_date_format (str, optional): Format string to use for the `{date}` pattern.
                Defaults to "%Y%m%d".
        """
        for (year, quarter, f) in self.quarterly_date_list:
            self.quarterly.year = year
            self.quarterly.quarter = quarter
            self.quarterly.entry_filter = lambda x: f(x) and self.entry_filter(x)
            self.quarterly.save(directory=directory,
                                dir_pattern=dir_pattern,
                                file_pattern=file_pattern,
                                download_all=download_all)

        for d in self.daily_date_list:
            self.daily.date = d
            try:
                self.daily.save(directory=directory,
                                dir_pattern=dir_pattern,
                                file_pattern=file_pattern,
                                download_all=download_all,
                                date_format=daily_date_format)
            except (EDGARQueryError, NoFilingsError):
                pass
