import asyncio
import os
import warnings
from datetime import date

from secedgar.cik_lookup import CIKLookup
from secedgar.client import NetworkClient
from secedgar.core._base import AbstractFiling
from secedgar.core.filing_types import FilingType
from secedgar.exceptions import FilingTypeError
from secedgar.utils import sanitize_date


class CompanyFilings(AbstractFiling):
    """Base class for receiving EDGAR filings.

    Args:
        cik_lookup (str): Central Index Key (CIK) for company of interest.
        filing_type (Union[secedgar.core.filing_types.FilingType, None]): Valid filing type
            enum. Defaults to None. If None, then all filing types for CIKs will be returned.
        user_agent (Union[str, NoneType]): Value used for HTTP header "User-Agent" for all requests.
            If given None, a valid client with user_agent must be given.
            See the SEC's statement on
            `fair access <https://www.sec.gov/os/accessing-edgar-data>`_
            for more information.
        start_date (Union[str, datetime.datetime, datetime.date], optional): Date before
            which not to fetch reports. Stands for "date after."
            Defaults to None (will fetch all filings before ``end_date``).
        end_date (Union[str, datetime.datetime, datetime.date], optional):
            Date after which not to fetch reports.
            Stands for "date before." Defaults to today.
        count (int): Number of filings to fetch. Will fetch up to `count` if that many filings
            are available. Defaults to all filings available.
        ownership (str): Must be in {"include", "exclude"}. Whether or not to include ownership
            filings.
        match_format (str): Must be in {"EXACT", "AMEND", "ALL"}.
        kwargs: See kwargs accepted for :class:`secedgar.client.NetworkClient`.

    Examples:
        Restrict the start and end dates by using the ``start_date`` and ``end_date`` arguments.

        .. code-block:: python

            from secedgar import FilingType, CompanyFilings
            from datetime import date

            filing = CompanyFilings(cik_lookup="aapl",
                                    filing_type=FilingType.FILING_10K,
                                    start_date=date(2015, 1, 1),
                                    end_date=date(2019, 1, 1),
                                    user_agent="Name (email)")

        If you would like to find all filings from some ``start_date`` until today,
        simply exclude ``end_date``. The end date defaults to today's date.

        .. code-block:: python

            from secedgar import FilingType, CompanyFilings
            from datetime import date

            # end date defaults to today
            filing = CompanyFilings(cik_lookup="aapl",
                                    filing_type=FilingType.FILING_10K,
                                    start_date=date(2015, 1, 1),
                                    user_agent="Name (email)")

        You can also look up a specific filing type for multiple companies.

        .. code-block:: python

            from secedgar import FilingType, CompanyFilings
            from datetime import date

            filing = CompanyFilings(cik_lookup=["aapl", "msft", "fb"],
                                    filing_type=FilingType.FILING_10K,
                                    start_date=date(2015, 1, 1),
                                    user_agent="Name (email)")

        *For a full list of the available filing types, please see*
        :class:`secedgar.core.FilingType`.


        SEC requests that traffic identifies itself via a user agent string. You can
        customize this according to your preference using the ``user_agent`` argument.

        .. code-block:: python

            from secedgar import FilingType, CompanyFilings
            from datetime import date

            filing = CompanyFilings(cik_lookup=["aapl", "msft", "fb"],
                                    filing_type=FilingType.FILING_10K,
                                    start_date=date(2015, 1, 1),
                                    user_agent="Name (email)")

    .. versionadded:: 0.4.0
    """

    def __init__(self,
                 cik_lookup,
                 filing_type=None,
                 user_agent=None,
                 start_date=None,
                 end_date=date.today(),
                 client=None,
                 count=None,
                 ownership="include",
                 match_format="ALL",
                 **kwargs):
        self._params = {
            "action": "getcompany",
            "output": "xml",
            "start": 0
        }
        self.start_date = start_date
        self.end_date = end_date
        self.filing_type = filing_type
        self.count = count
        self.match_format = match_format
        # Make default client NetworkClient and pass in kwargs
        self._client = client or NetworkClient(user_agent=user_agent, **kwargs)
        # make CIKLookup object for users if not given
        self.cik_lookup = cik_lookup
        self.ownership = ownership

    @property
    def path(self):
        """str: Path added to client base."""
        return "cgi-bin/browse-edgar"

    @property
    def params(self):
        """:obj:`dict`: Parameters to include in requests."""
        if self.start_date:
            self._params["datea"] = sanitize_date(self.start_date)
        else:
            self._params.pop("datea", None)  # if no start date, make sure it isn't in params

        if self.end_date:
            self._params["dateb"] = sanitize_date(self.end_date)
        else:
            self._params.pop("dateb", None)  # if no end date, make sure it isn't in params

        self._params["ownership"] = self.ownership
        return self._params

    @property
    def client(self):
        """``secedgar.client.NetworkClient``: Client to use to make requests."""
        return self._client

    @property
    def start_date(self):
        """Union([datetime.date, datetime.datetime, str]): Date before which no filings fetched."""
        return self._start_date

    @property
    def match_format(self):
        """The match format to use when searching for filings."""
        return self._match_format

    @match_format.setter
    def match_format(self, val):
        if val not in ("EXACT", "AMEND", "ALL"):
            raise ValueError("Format must be 'EXACT', 'AMEND', or 'ALL'.")
        self._match_format = val

    @start_date.setter
    def start_date(self, val):
        sanitize_date(val)  # make sure start date is valid
        self._start_date = val

    @property
    def end_date(self):
        """Union([datetime.date, datetime.datetime, str]): Date after which no filings fetched."""
        return self._end_date

    @end_date.setter
    def end_date(self, val):
        sanitize_date(val)  # make sure end date is valid
        self._end_date = val

    @property
    def filing_type(self):
        """``secedgar.core.FilingType``: FilingType enum of filing."""
        return self._filing_type

    @filing_type.setter
    def filing_type(self, filing_type):
        if isinstance(filing_type, FilingType):
            self._params["type"] = filing_type.value
        elif filing_type is not None:
            raise FilingTypeError(
                f"filing_type must be of type FilingType. Given {type(filing_type)}."
            )
        self._filing_type = filing_type

    @property
    def count(self):
        """Number of filings to fetch."""
        return self._count

    @count.setter
    def count(self, val):
        if val is None:
            self._count = None
        elif not isinstance(val, int):
            raise TypeError("Count must be positive integer or None.")
        elif val < 1:
            raise ValueError("Count must be positive integer or None.")
        else:
            self._count = val
            self._params["count"] = val

    @property
    def cik_lookup(self):
        """``secedgar.cik_lookup.CIKLookup``: CIKLookup object."""
        return self._cik_lookup

    @cik_lookup.setter
    def cik_lookup(self, val):
        if not isinstance(val, CIKLookup):
            val = CIKLookup(val, client=self.client)
        self._cik_lookup = val

    @property
    def ownership(self):
        """str: Whether or not to include ownership in search."""
        return self._ownership

    @ownership.setter
    def ownership(self, val):
        if val not in ("include", "exclude"):
            raise ValueError(f"Ownership must be 'include' or 'exclude'. Given {val}.")
        self._ownership = val

    def get_urls(self, **kwargs):
        """Get urls for all CIKs given to Filing object.

        Args:
            **kwargs: Anything to be passed to requests when making get request.
                See keyword arguments accepted for
                ``secedgar.client.NetworkClient.get_soup``.

        Returns:
            urls (list): List of urls for txt files to download.
        """
        return {
            key: self._get_urls_for_cik(cik, **kwargs)
            for key, cik in self.cik_lookup.lookup_dict.items()
        }

    def _filter_filing_links(self, data):
        """Filter filing links from data to only include exact matches.

        Args:
            data (``bs4.BeautifulSoup``): ``BeautifulSoup`` object to parse.

        Returns:
            list of str: List of URLs that match ``filing_type``.
        """
        filings = data.find_all("filing")
        if self.filing_type is None:
            return [f.filinghref.string for f in filings]
        else:
            return [f.filinghref.string for f in filings if f.type.string == self.filing_type.value]

    # TODO: Change this to return accession numbers that are turned into URLs later
    def _get_urls_for_cik(self, cik, **kwargs):
        """Get all urls for specific company according to CIK.

        Must match start date, end date, filing_type, and count parameters.

        Args:
            cik (str): CIK for company.
            **kwargs: Anything to be passed to requests when making get request.
                See keyword arguments accepted for
                ``secedgar.client.NetworkClient.get_soup``.

        Returns:
            txt_urls (list of str): Up to the desired number of URLs for that specific company
            if available.
        """
        self.params["CIK"] = cik
        links = []
        self.params["start"] = 0  # set start back to 0 before paginating
        while self.count is None or len(links) < self.count:
            data = self.client.get_soup(self.path, self.params, **kwargs)
            filtered_links = self._filter_filing_links(data)
            links.extend(filtered_links)
            self.params["start"] += self.client.batch_size
            if len(data.find_all("filinghref")) == 0:  # no more filings
                break

        txt_urls = [link[:link.rfind("-")].strip() + ".txt" for link in links]

        if isinstance(self.count, int) and len(txt_urls) < self.count:
            warnings.warn(
                "Only {num} of {count} filings were found for {cik}.".format(
                    num=len(txt_urls), count=self.count, cik=cik))
        # Takes `count` filings at most
        return txt_urls[:self.count]

    def save(self, directory, dir_pattern=None, file_pattern=None):
        """Save files in specified directory.

        Each txt url looks something like:
        https://www.sec.gov/Archives/edgar/data/1018724/000101872419000043/0001018724-19-000043.txt

        Args:
            directory (str): Path to directory where files should be saved.
            dir_pattern (str): Format string for subdirectories. Default is "{cik}/{type}".
                Valid options are {cik} and/or {type}.
            file_pattern (str): Format string for files. Default is "{accession_number}".
                Valid options are {accession_number}.

        Returns:
            None

        Raises:
            ValueError: If no text urls are available for given filing object.
        """
        urls = self.get_urls_safely()

        if dir_pattern is None:
            dir_pattern = os.path.join("{cik}", "{type}")
        if file_pattern is None:
            file_pattern = "{accession_number}"

        inputs = []
        for cik, links in urls.items():
            # If no filing type, just leave all filings for CIK under directory named after CIK
            if self.filing_type is None:
                formatted_dir = cik
            else:
                formatted_dir = dir_pattern.format(cik=cik,
                                                   type=self.filing_type.value)
            for link in links:
                formatted_file = file_pattern.format(
                    accession_number=self.get_accession_number(link))
                path = os.path.join(directory, formatted_dir, formatted_file)
                inputs.append((link, path))

        asyncio.run(self.client.wait_for_download_async(inputs))
