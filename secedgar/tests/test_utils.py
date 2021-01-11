import gzip
from datetime import datetime

import pytest
import requests
from secedgar.tests.utils import MockResponse, datapath
from secedgar.utils import get_cik_map, get_quarter, sanitize_date


@pytest.fixture(scope="module")
def mock_cik_map_response(monkeymodule):
    with gzip.open(datapath("utils", "cik_map.json.gz"), "rt") as f:
        content = bytes(f.read(), "utf-8")
    monkeymodule.setattr(requests.Session, "get",
                         MockResponse(content=content))


class TestUtils:
    @pytest.mark.parametrize(
        "bad_date",
        [
            "2012101",
            "201210",
            "1010",
            "2012011",
            2012011,
            2012101,
            2012,
            1010,
            201210
        ]
    )
    def test_bad_date_formats(self, bad_date):
        with pytest.raises(TypeError):
            sanitize_date(bad_date)

    @pytest.mark.parametrize(
        "good_date",
        [
            "20120101",
            20120101
        ]
    )
    def test_good_formats_no_change(self, good_date):
        """Tests formats that should not change from what is given. """
        assert sanitize_date(good_date) == good_date

    @pytest.mark.parametrize(
        "dt_date,expected",
        [
            (datetime(2018, 1, 1), "20180101"),
            (datetime(2020, 3, 4), "20200304"),
            (datetime(2020, 7, 18), "20200718")
        ]
    )
    def test_good_formats_datetime(self, dt_date, expected):
        assert sanitize_date(dt_date) == expected

    @pytest.mark.parametrize(
        "ticker,cik",
        [
            ("AAPL", "320193"),
            ("FB", "1326801"),
            ("MSFT", "789019")
        ]
    )
    def test_get_cik_map(self, ticker, cik, mock_cik_map_response):
        cik_map = get_cik_map()
        assert cik_map[ticker] == cik

    @pytest.mark.parametrize(
        "name,cik",
        [
            ("Apple Inc.", "320193"),
            ("NIKE, Inc.", "320187"),
            ("MICROSOFT CORP", "789019"),
        ]
    )
    def test_get_company_name_map(self, name, cik, mock_cik_map_response):
        name_map = get_cik_map(key="title")
        assert name_map[name] == cik

    @pytest.mark.parametrize(
        "key",
        [
            "Ticker",
            "Title",
            "CIK",
            "Company Name"
        ]
    )
    def test_get_cik_map_bad_keys(self, key):
        with pytest.raises(ValueError):
            get_cik_map(key=key)

    @pytest.mark.parametrize(
        "date,expected_quarter",
        [
            (datetime(2020, 1, 1), 1),
            (datetime(2020, 2, 1), 1),
            (datetime(2020, 3, 1), 1),
            (datetime(2020, 3, 31), 1),
            (datetime(2020, 4, 1), 2),
            (datetime(2020, 5, 1), 2),
            (datetime(2020, 6, 1), 2),
            (datetime(2020, 6, 30), 2),
            (datetime(2020, 7, 1), 3),
            (datetime(2020, 8, 1), 3),
            (datetime(2020, 9, 1), 3),
            (datetime(2020, 9, 30), 3),
            (datetime(2020, 10, 1), 4),
            (datetime(2020, 11, 1), 4),
            (datetime(2020, 12, 1), 4),
            (datetime(2020, 12, 31), 4),
        ]
    )
    def test_get_quarter(self, date, expected_quarter):
        assert get_quarter(date) == expected_quarter
