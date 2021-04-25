import datetime
import os

from secedgar.core._index import IndexFilings
from secedgar.utils import get_quarter


class DailyFilings(IndexFilings):
    """Class for retrieving all daily filings from https://www.sec.gov/Archives/edgar/daily-index.

    Attributes:
        date (datetime.date): Date of daily filing to fetch.
        client (secedgar.client._base.AbstractClient, optional): Client to use for fetching data.
            Defaults to ``secedgar.client.NetworkClient`` if none is given.
        entry_filter (function, optional): A boolean function to determine
            if the FilingEntry should be kept. Defaults to `lambda _: True`.
            The ``FilingEntry`` object exposes 7 variables which can be
            used to filter which filings to keep. These are "cik", "company_name",
            "form_type", "date_filed", "file_name", and "path".
        kwargs: Keyword arguments to pass to ``secedgar.filings._index.IndexFilings``.

    Using ``entry_filter``
    ----------------------

    To only download filings from a company named "Company A", the following
    function would suffice for only getting those filings:

    .. code-block:: python

        def get_company_a_filings(filing_entry):
            return filing_entry.company_name == "Company A"

    To only download Company A or Company B's 10-K fillings from
    a specific day, a well-defined ``entry_filter`` would be:

    .. code-block:: python

        def get_company_ab_10k(filing_entry):
            return filing_entry.company_name in ("Company A", "Company B") and
                   filing_entry.form_type.lower() == "10-k"

    To use the second function as an ``entry_filter``, the following code could be used:

    .. code-block:: python

        from datetime import date
        from secedgar.core import DailyFilings

        d = DailyFilings(date=date(2020, 12, 10), entry_filter=get_company_ab_10k)

    """

    def __init__(self, date, client=None, entry_filter=lambda _: True):
        super().__init__(client=client, entry_filter=entry_filter)
        self.date = date

    @property
    def path(self):
        """str: Path added to client base.

        .. note::
            The trailing slash at the end of the path is important.
            Omitting will raise EDGARQueryError.
        """
        return "Archives/edgar/daily-index/{year}/QTR{num}/".format(
            year=self.year, num=self.quarter)

    @property
    def quarter(self):
        """int: Get quarter number from date attribute."""
        return get_quarter(self._date)

    @property
    def year(self):
        """int: Year of date for daily filing."""
        return self._date.year

    @property
    def date(self):
        """datetime.date: Date of daily filing."""
        return self._date

    @date.setter
    def date(self, val):
        if not isinstance(val, (datetime.date, datetime.datetime)):
            raise TypeError(
                """Date must be given as datetime.date or datetime.datetime object.
                            Was given type {type}.""".format(type=type(val)))
        self._date = val

    @property
    def idx_filename(self):
        """Main index filename to look for."""
        return "master.{date}.idx".format(date=self._get_idx_formatted_date())

    def _get_tar_urls(self):
        """The .tar.gz filename for the current day."""
        if self.year < 1995 or (self.year == 1995 and self.quarter < 3):
            raise ValueError(
                'Bulk downloading is only available starting 1995 Q3.')
        daily_file = '{date}.nc.tar.gz'.format(
            date=self._date.strftime("%Y%m%d"))
        daily_url = f'{self.client._BASE}{self.tar_path}{daily_file}'
        return [daily_url]

    def _get_idx_formatted_date(self):
        """Format date for idx file.

        EDGAR changed its master.idx file format twice. In 1995 QTR 1 and in 1998 QTR 2.
        The format went from MMDDYY to YYMMDD to YYYYMMDD.

        Returns:
            date (str): Correctly formatted date for master.idx file.
        """
        if self._date.year < 1995:
            return self._date.strftime("%m%d%y")
        elif self._date < datetime.date(1998, 3, 31):
            return self._date.strftime("%y%m%d")
        else:
            return self._date.strftime("%Y%m%d")

    def save(self,
             directory,
             dir_pattern=None,
             file_pattern="{accession_number}",
             date_format="%Y%m%d",
             download_all=False):
        """Save all daily filings.

        Store all filings for each unique company name under a separate subdirectory
        within given directory argument. Creates directory with date in YYYYMMDD format
        within given directory.

        Args:
            directory (str): Directory where filings should be stored. Will be broken down
                further by company name and form type.
            dir_pattern (str): Format string for subdirectories. Default is `{date}/{cik}`.
                Valid options that must be wrapped in curly braces are `date` and `cik`.
            date_format (str): Format string to use for the `{date}` pattern. Default is ``%Y%m%d``.
            file_pattern (str): Format string for files. Default is `{accession_number}`.
                Valid options are `accession_number`.
            download_all (bool): Type of downloading system, if true downloads all data for the day,
                if false downloads each file in index. Default is `False`.
        """
        if dir_pattern is None:
            dir_pattern = os.path.join("{date}", "{cik}")

        # If "{cik}" is in dir_pattern, it will be passed on and if not it will be ignored
        formatted_dir = dir_pattern.format(
            date=self._date.strftime(date_format), cik="{cik}")
        self._save_filings(directory,
                           dir_pattern=formatted_dir,
                           file_pattern=file_pattern,
                           download_all=download_all)
