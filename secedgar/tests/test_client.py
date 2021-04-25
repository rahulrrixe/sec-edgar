import asyncio
import math
import os
import time

import pytest
import requests
from secedgar.client import NetworkClient
from secedgar.exceptions import EDGARQueryError
from secedgar.tests.utils import MockResponse


@pytest.fixture
def client():
    return NetworkClient()


@pytest.fixture
def mock_single_filing_type_good_response(monkeypatch):
    """Mock response with list of single filing type for single CIK."""
    monkeypatch.setattr(requests.Session, "get",
                        MockResponse(datapath_args=["CIK", "single_cik_multiple_filings_10k.html"]))


@pytest.fixture
def mock_multiple_cik_results_good_response(monkeypatch):
    monkeypatch.setattr(requests.Session, "get",
                        MockResponse(datapath_args=["CIK", "cik_multiple_results.html"]))


@pytest.fixture
def mock_single_filing_page_good_response(monkeypatch):
    monkeypatch.setattr(requests.Session, "get",
                        MockResponse(datapath_args=["CIK", "single_filing_page.html"]))


class TestNetworkClient:
    def test_client_bad_response_raises_error(self, client):
        no_cik_response = MockResponse(datapath_args=["CIK", "cik_not_found.html"])
        with pytest.raises(EDGARQueryError):
            NetworkClient()._validate_response(no_cik_response)

    def test_client_good_response_single_filing_type_passes(self,
                                                            mock_single_filing_type_good_response,
                                                            client):
        assert client.get_response("path")

    def test_client_good_response_multiple_cik_results_passes(self,
                                                              mock_multiple_cik_results_good_response,  # noqa: E501
                                                              client):
        assert client.get_response("path")

    def test_client_good_response_single_filing_passes(self,
                                                       mock_single_filing_page_good_response,
                                                       client):
        assert client.get_response("path")

    def test_429_returns_custom_message(self, client, monkeypatch):
        # with pytest.raises(requests.exceptions.HTTPError) as e:
        response = client._validate_response(MockResponse(
            content=bytes("", "utf-8"), status_code=429))
        assert "rate limit" in response.reason

    @pytest.mark.parametrize(
        "bad_retry_count,expectation",
        [
            (0.5, TypeError),
            ("2", TypeError),
            (-1, ValueError)
        ]
    )
    def test_client_bad_retry_count_setter(self, bad_retry_count, expectation, client):
        with pytest.raises(expectation):
            client.retry_count = bad_retry_count

    @pytest.mark.parametrize(
        "good_retry_count",
        range(10)
    )
    def test_client_good_retry_count_setter(self, good_retry_count, client):
        client.retry_count = good_retry_count
        assert client.retry_count == good_retry_count

    @pytest.mark.parametrize(
        "bad_backoff_factor",
        [
            "1",
            "1.0",
            "-1",
            "-1.0",
            [1, 2, 3],
        ]
    )
    def test_bad_backoff_factor_setter(self, bad_backoff_factor):
        with pytest.raises(TypeError):
            _ = NetworkClient(backoff_factor=bad_backoff_factor)

    @pytest.mark.parametrize(
        "good_backoff_factor",
        [
            -1,
            -1.0,
            1,
            1.0,
            2,
            10
        ]
    )
    def test_good_backoff_factor_setter(self, good_backoff_factor):
        client = NetworkClient()
        client.backoff_factor = good_backoff_factor
        assert client.backoff_factor == good_backoff_factor

    @pytest.mark.parametrize(
        "test_input,expectation",
        [
            (0, ValueError),
            (-1, ValueError),
            (11, ValueError),
            (-1.5, ValueError),
            (11.5, ValueError)
        ]
    )
    def test_client_bad_rate_limit(self, test_input, expectation, client):
        with pytest.raises(expectation):
            client.rate_limit = test_input

    @pytest.mark.parametrize(
        "good_rate_limit",
        range(1, 11)
    )
    def test_client_good_rate_limit(self, good_rate_limit, client):
        client.rate_limit = good_rate_limit
        assert client.rate_limit == good_rate_limit

    @pytest.mark.parametrize(
        "good_pause",
        [x / 10 for x in range(1, 11)]
    )
    def test_client_good_pause_setter(self, good_pause, client):
        client.pause = good_pause
        assert client.pause == good_pause

    @pytest.mark.parametrize(
        "test_input,expectation",
        [
            (0.5, TypeError),
            ("1", TypeError),
            (0, ValueError)
        ]
    )
    def test_client_bad_batch_size_setter(self, test_input, expectation, client):
        with pytest.raises(expectation):
            client.batch_size = test_input

    @pytest.mark.parametrize(
        "good_batch_size",
        range(1, 100, 10)
    )
    def test_client_good_batch_size_setter(self, good_batch_size, client):
        client.batch_size = good_batch_size
        assert client.batch_size == good_batch_size

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "rate_limit",
        range(1, 10)
    )
    def test_rate_limit_requests_per_second(self, tmp_data_directory, rate_limit,
                                            mock_filing_response):
        client = NetworkClient(rate_limit=rate_limit)
        min_seconds = 3
        num_requests = rate_limit * min_seconds
        inputs = [("https://google.com", os.path.join(tmp_data_directory, str(i)))
                  for i in range(num_requests)]
        loop = asyncio.get_event_loop()
        start = time.time()
        loop.run_until_complete(client.wait_for_download_async(inputs))
        end = time.time()
        assert num_requests / math.ceil(end - start) <= rate_limit
