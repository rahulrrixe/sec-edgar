import warnings

import requests

from secedgar.client import NetworkClient
from secedgar.exceptions import CIKError, EDGARQueryError


def get_cik_map(key="ticker"):
    """Get dictionary of tickers to CIK numbers.

    Args:
        key (str): Should be either "ticker" or "title". Choosing "ticker"
            will give dict with tickers as keys. Choosing "title" will use
            company name as keys.

    Returns:
        Dictionary with either ticker or company name as keys, depending on
        ``key`` argument, and corresponding CIK as values.

    .. versionadded:: 0.1.6
    """
    if key not in ("ticker", "title"):
        raise ValueError("key must be 'ticker' or 'title'. Was given {key}.".format(key=key))
    response = requests.get("https://www.sec.gov/files/company_tickers.json")
    json_response = response.json()
    return {v[key]: str(v["cik_str"]) for v in json_response.values()}


class CIKLookup:
    """CIK Lookup object.

    Given list of tickers/company names to lookup, this object can return associated CIKs.

    Args:
        lookup (Union[str, list]): Ticker, company name, or list of tickers and/or company names.

    .. versionadded:: 0.1.5
    """

    def __init__(self, lookups, client=None, **kwargs):
        if lookups and isinstance(lookups, str):
            self._lookups = [lookups]  # make single string into list
        else:
            # Check that iterable only contains strings and is not empty
            if not (lookups and all(type(o) is str for o in lookups)):
                raise TypeError("CIKs must be given as string or iterable.")
            self._lookups = lookups
        self._params = {'action': 'getcompany'}
        self._client = client if client is not None else NetworkClient(**kwargs)
        self._lookup_dict = None
        self._ciks = None

    @property
    def ciks(self):
        """:obj:`list` of :obj:`str`: List of CIKs (as string of digits)."""
        if self._ciks is None:
            self._lookup_dict = self.get_ciks()
            self._ciks = list(self.lookup_dict.values())
        return self._ciks

    @property
    def lookups(self):
        """`list` of `str` to lookup (to get CIK values)."""
        return self._lookups

    @property
    def path(self):
        """str: Path to add to client base."""
        return "cgi-bin/browse-edgar"

    @property
    def client(self):
        """``secedgar.client_.base``: Client to use to fetch requests."""
        return self._client

    @property
    def params(self):
        """:obj:`dict` Search parameters to add to client."""
        return self._params

    @property
    def lookup_dict(self):
        """:obj:`dict`: Dictionary that makes tickers and company names to CIKs."""
        if self._lookup_dict is None:
            self._lookup_dict = self.get_ciks()
        return self._lookup_dict

    # TODO: Add mock to test this functionality
    def _get_lookup_soup(self, lookup):
        """Gets `BeautifulSoup` object for lookup.

        First tries to lookup using CIK. Then falls back to company name.

        .. warning::
           Only to be used internally by `_get_cik` to get CIK from lookup.

        Args:
            lookup (str): CIK, company name, or ticker symbol to lookup.

        Returns:
            soup (bs4.BeautifulSoup): `BeautifulSoup` object to be used to get
                company CIK.
        """
        try:  # try to lookup by CIK
            self._params['CIK'] = lookup
            return self._client.get_soup(self.path, self.params)
        except EDGARQueryError:  # fallback to lookup by company name
            self.params.pop('CIK')  # delete this parameter so no conflicts arise
            self._params['company'] = lookup
            return self._client.get_soup(self.path, self.params)

    def _get_cik(self, lookup):
        """Gets CIK from `BeautifulSoup` object.

        .. warning: This method will warn when lookup returns multiple possibilities for a
            CIK are found.

        Args:
            lookup (str): CIK, company name, or ticker symbol which was looked up.

        Returns:
            CIK (str): CIK for lookup.
        """
        self._validate_lookup(lookup)
        soup = self._get_lookup_soup(lookup)
        try:  # try to get single CIK for lookup
            span = soup.find('span', {'class': 'companyName'})
            return span.find('a').getText().split()[0]  # returns single CIK
        except AttributeError:  # warn and skip if multiple possibilities for CIK found
            warning_message = """Lookup '{0}' will be skipped.
                          Found multiple companies matching '{0}':
                          {1}""".format(lookup, '\n'.join(self._get_cik_possibilities(soup)))
            warnings.warn(warning_message)
        finally:
            # Delete parameters after lookup
            self._params.pop('company', None)
            self._params.pop('CIK', None)

    @staticmethod
    def _get_cik_possibilities(soup):
        """Get all CIK possibilities if multiple are listed.

        Args:
            soup (BeautifulSoup): BeautifulSoup object to search through.

        Returns:
            All possible companies that match lookup.
        """
        try:
            # Exclude table header
            table_rows = soup.find('table', {'summary': 'Results'}).find_all('tr')[1:]
            # Company names are in second column of table
            return [''.join(row.find_all('td')[1].find_all(text=True)) for row in table_rows]
        except AttributeError:
            # If there are no CIK possibilities, then no results were returned
            raise EDGARQueryError

    @staticmethod
    def _validate_cik(cik):
        """Check if CIK is 10 digit string."""
        if not (isinstance(cik, str) and len(cik) == 10 and cik.isdigit()):
            raise CIKError(cik)
        return cik

    @staticmethod
    def _validate_lookup(lookup):
        """Ensure that lookup is string.

        Args:
            lookup: Value to lookup.

        Raises:
            TypeError: If lookup is not a non-empty string.
        """
        if not (lookup and isinstance(lookup, str)):
            raise TypeError("Lookup value must be string. Given type {0}.".format(type(lookup)))
        return lookup

    def get_ciks(self):
        """Validate lookup values and return corresponding CIKs.

        Returns:
            ciks (dict): Dictionary with lookup terms as keys and CIKs as values.

        """
        ciks = dict()
        to_lookup = set(self.lookups)
        found = set()

        # First, try to get all CIKs with ticker map
        # Tickers in map are upper case, so look up with upper case
        ticker_map = get_cik_map(key="ticker")
        for lookup in to_lookup:
            try:
                ciks[lookup] = ticker_map[lookup.upper()]
                found.add(lookup)
            except KeyError:
                continue
        to_lookup -= found

        # If any more lookups remain, try to finish with company name map
        # Case varies from company, so lookup with what is given
        if to_lookup:
            company_map = get_cik_map(key="title")
            for lookup in to_lookup:
                try:
                    ciks[lookup] = company_map[lookup]
                    found.add(lookup)
                except KeyError:
                    continue
            to_lookup -= found

        # Finally, if lookups are still left, look them up through the SEC's search
        for lookup in to_lookup:
            try:
                result = self._get_cik(lookup)
                self._validate_cik(result)  # raises error if not valid CIK
                ciks[lookup] = result
            except CIKError:
                pass  # If multiple companies, found, just print out warnings
        return ciks
