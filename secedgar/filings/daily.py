import datetime
import os

from secedgar.filings._index import IndexFilings
from secedgar.utils import get_quarter


class DailyFilings(IndexFilings):
    """Class for retrieving all daily filings from https://www.sec.gov/Archives/edgar/daily-index.

    Attributes:
        date (datetime.datetime): Date of daily filing to fetch.
        client (secedgar.client._base.AbstractClient, optional): Client to use for fetching data.
            Defaults to ``secedgar.client.NetworkClient`` if none is given.
        entry_filter (function, optional): A boolean function to determine
            if the FilingEntry should be kept. Defaults to `lambda _: True`.
    """

    def __init__(self, date, client=None, entry_filter=lambda _: True):
        super().__init__(client=client, entry_filter=entry_filter)
        if not isinstance(date, datetime.datetime):
            raise TypeError(
                "Date must be given as datetime object. Was given type {type}.".format(
                    type=type(date)))
        self._date = date

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
        """Get quarter number from date attribute."""
        return get_quarter(self._date)

    @property
    def year(self):
        """Year of date for daily filing."""
        return self._date.year

    @property
    def idx_filename(self):
        """Main index filename to look for."""
        return "master.{date}.idx".format(date=self._get_idx_formatted_date())

    def get_file_names(self):
        """The .tar.gz filename for the current day."""
        if self.year < 1995 or (self.year == 1995 and self.quarter < 3):
            raise ValueError('Bulk downloading is only available starting 1995 Q3.')
        daily_file = '{date}.nc.tar.gz'.format(date=self._date.strftime("%Y%m%d"))
        return [daily_file]

    def _get_idx_formatted_date(self):
        """Format date for idx file.

        EDGAR changed its master.idx file format twice. In 1995 QTR 1 and in 1998 QTR 2.
        The format went from MMDDYY to YYMMDD to YYYYMMDD.

        Returns:
            date (str): Correctly formatted date for master.idx file.
        """
        if self._date.year < 1995:
            return self._date.strftime("%m%d%y")
        elif self._date < datetime.datetime(1998, 3, 31):
            return self._date.strftime("%y%m%d")
        else:
            return self._date.strftime("%Y%m%d")

    def save(self, directory, dir_pattern=None, file_pattern=None, date_format="%Y%m%d",
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

        formatted_dir = dir_pattern.format(date=self._date.strftime(date_format), cik="{cik}")
        self.save_filings(directory, dir_pattern=formatted_dir,
                          file_pattern=file_pattern, download_all=download_all)
