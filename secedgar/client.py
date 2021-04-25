"""Client to communicate with EDGAR database."""
import asyncio
import os
import time

import aiohttp
import requests
import tqdm
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from secedgar.exceptions import EDGARQueryError
from secedgar.utils import make_path


class NetworkClient:
    """Class in charge of sending and handling requests to EDGAR database.

    Args:
        retry_count (int): Number of times to retry connecting to URL if not successful.
            Defaults to 3.
        batch_size (int): Number of filings to receive per request (helpful if pagination needed).
            Defaults to 10.
        backoff_factor (float): Backoff factor to use with ``urllib3.util.retry.Retry``.
            See urllib3 docs for more info. Defaults to 0.
        rate_limit (int): Number of requests per second to limit to.
            Defaults to 10.
        user_agent (str): Value used for HTTP header "User-Agent" for all requests.
            Defaults to "github.com/sec-edgar/sec-edgar"

    .. note:
       It is highly suggested to keep rate_limit <= 10, as the SEC will block your IP
       temporarily if you exceed this rate.
    """

    _BASE = "http://www.sec.gov/"

    def __init__(self,
                 retry_count=3,
                 batch_size=10,
                 backoff_factor=0,
                 rate_limit=10,
                 user_agent="github.com/sec-edgar/sec-edgar"):
        self.retry_count = retry_count
        self.batch_size = batch_size
        self.backoff_factor = backoff_factor
        self.rate_limit = rate_limit
        self.user_agent = user_agent

    @property
    def retry_count(self):
        """int: Number of times to retry request."""
        return self._retry_count

    @retry_count.setter
    def retry_count(self, value):
        if not isinstance(value, int):
            raise TypeError("Retry count must be int. Given type {0}.".format(
                type(value)))
        elif value < 0:
            raise ValueError(
                "Retry count must be greater than 0. Given {0}.".format(value))
        self._retry_count = value

    @property
    def batch_size(self):
        """int: The Number of results to show per page."""
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value):
        if not isinstance(value, int):
            raise TypeError("Batch size must be int. Given type {0}".format(
                type(value)))
        elif value < 1:
            raise ValueError("Batch size must be positive integer.")
        self._batch_size = value

    @property
    def backoff_factor(self):
        """float: Backoff factor to pass to ``urllib3.util.retry.Retry``."""
        return self._backoff_factor

    @backoff_factor.setter
    def backoff_factor(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(
                "Backoff factor must be int or float. Given type {0}".format(
                    type(value)))
        self._backoff_factor = value

    @property
    def rate_limit(self):
        """int: Number of requests to limit client to per second."""
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, value):
        if not (0 < value <= 10):
            raise ValueError(
                "Rate must be greater than 0 and less than or equal to 10.")
        else:
            self._rate_limit = value

    @property
    def user_agent(self):
        """str: Value used for HTTP header "User-Agent" for all requests."""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value):
        if not isinstance(value, str):
            raise TypeError("user_agent must be str. Given type {0}.".format(type(value)))
        self._user_agent = value

    @staticmethod
    def _prepare_query(path):
        """Prepare the query url.

        Args:
            url (str): End of url.

        Returns:
            url (str): A formatted url.
        """
        return "{base}{path}".format(base=NetworkClient._BASE, path=path)

    def _validate_response(self, response, *args, **kwargs):
        """Ensure response from EDGAR is valid.

        Args:
            response (requests.response): A requests.response object.

        Raises:
            EDGARQueryError: If response contains EDGAR error message.
        """
        error_messages = ("The value you submitted is not valid",
                          "No matching Ticker Symbol.", "No matching CIK.",
                          "No matching companies.")
        status_code = response.status_code

        if status_code == 429:
            response.reason = """Error: You have hit the rate limit.
            SEC has banned your IP for 10 minutes.
            Please wait 10 minutes before making another request.
            https://www.sec.gov/privacy.htm#security"""
        elif any(m in response.text for m in error_messages):
            raise EDGARQueryError(
                "No results were found or the value submitted was not valid.")

        return response

    def get_response(self, path, params=None, **kwargs):
        """Execute HTTP request and returns response if valid.

        Args:
            path (str): A properly-formatted path
            params (dict): Dictionary of parameters to pass
                to request. Defaults to None.
            backoff_factor (float): Backoff factor to pass to ``urllib3.util.Retry``.
            kwargs: Keyword arguments to pass to ``requests.Session.get``.

        Returns:
            response (requests.Response): A ``requests.Response`` object.

        Raises:
            EDGARQueryError: If problems arise when making query.
        """
        prepared_url = self._prepare_query(path)
        headers = {"User-Agent": self.user_agent}
        with requests.Session() as session:
            retry = Retry(self.retry_count,
                          backoff_factor=self.backoff_factor,
                          raise_on_status=True)
            session.mount(self._BASE, adapter=HTTPAdapter(max_retries=retry))
            session.hooks["response"].append(self._validate_response)
            response = session.get(prepared_url, params=params,
                                   headers=headers, **kwargs)
            return response

    def get_soup(self, path, params, **kwargs):
        """Return BeautifulSoup object from response text. Uses lxml parser.

        Args:
            path (str): A properly-formatted path
            params (dict): Dictionary of parameters to pass
                to request.

        Returns:
            BeautifulSoup object from response text.
        """
        return BeautifulSoup(self.get_response(path, params, **kwargs).text,
                             features='lxml')

    @staticmethod
    async def fetch(link, session):
        """Asynchronous get request.

        Args:
            link (str): URL to fetch.
            session (aiohttp.ClientSession): Asynchronous client session to use to perform
                get request.

        Returns:
            Content: Contents of response from get request.
        """
        async with await session.get(link) as response:
            contents = await response.read()
        return contents

    async def wait_for_download_async(self, inputs):
        """Asynchronously download links into files using rate limit.

        inputs (list of tuples of str): List of tuples with length 2. First element
            in tuple should be URL to request and second element should be path
            where content after requesting URL is stored.
        """
        async def fetch_and_save(link, path, session):
            """Fetch link and save to path using session."""
            contents = await self.fetch(link, session)
            make_path(os.path.dirname(path))
            with open(path, "wb") as f:
                f.write(contents)

        conn = aiohttp.TCPConnector(limit=self.rate_limit)
        headers = {
            "Connection": "keep-alive",
            "User-Agent": self.user_agent,
        }
        client = aiohttp.ClientSession(connector=conn, headers=headers,
                                       raise_for_status=True)

        def batch(iterable, n):
            length = len(iterable)
            for ndx in range(0, length, n):
                yield iterable[ndx:min(ndx + n, length)]

        conn = aiohttp.TCPConnector(limit=self.rate_limit)
        client = aiohttp.ClientSession(connector=conn,
                                       headers={'Connection': 'keep-alive'},
                                       raise_for_status=True)

        async with client:
            for group in tqdm.tqdm(batch(inputs, self.rate_limit),
                                   total=len(inputs) // self.rate_limit,
                                   unit_scale=self.rate_limit):
                start = time.monotonic()
                tasks = [
                    fetch_and_save(link, path, client) for link, path in group
                ]
                await asyncio.gather(
                    *tasks)  # If results are needed they can be assigned here
                execution_time = time.monotonic() - start
                # If execution time > 1, requests are essentially wasted, but a small price to pay
                await asyncio.sleep(max(0, 1 - execution_time))
