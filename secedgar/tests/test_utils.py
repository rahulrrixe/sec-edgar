from datetime import date, datetime

import pytest
import secedgar.utils as utils


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
            utils.sanitize_date(bad_date)

    @pytest.mark.parametrize(
        "good_date",
        [
            "20120101",
            20120101
        ]
    )
    def test_good_formats_no_change(self, good_date):
        """Tests formats that should not change from what is given. """
        assert utils.sanitize_date(good_date) == good_date

    @pytest.mark.parametrize(
        "dt_date,expected",
        [
            (datetime(2018, 1, 1), "20180101"),
            (datetime(2020, 3, 4), "20200304"),
            (datetime(2020, 7, 18), "20200718"),
            (date(2018, 1, 1), "20180101"),
            (date(2020, 3, 4), "20200304"),
            (date(2020, 7, 18), "20200718")
        ]
    )
    def test_good_formats_datetime(self, dt_date, expected):
        assert utils.sanitize_date(dt_date) == expected

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
        assert utils.get_quarter(date) == expected_quarter

    @pytest.mark.parametrize(
        "bad_quarter",
        [
            0.0,
            0,
            5.0,
            5,
            1.0,
            2.0
        ]
    )
    def test_get_month_bad_quarter(self, bad_quarter):
        with pytest.raises(TypeError):
            utils.get_month(bad_quarter)

    @pytest.mark.parametrize(
        "quarter,month",
        [
            (1, 1),
            (2, 4),
            (3, 7),
            (4, 10)
        ]
    )
    def test_get_month(self, quarter, month):
        assert utils.get_month(quarter) == month

    @pytest.mark.parametrize(
        "year,quarter,expected",
        [
            (2020, 1, (2020, 2)),
            (2020, 4, (2021, 1)),
            (2020, 2, (2020, 3)),
            (2020, 3, (2020, 4))
        ]
    )
    def test_add_quarter(self, year, quarter, expected):
        assert utils.add_quarter(year, quarter) == expected

    @pytest.mark.parametrize(
        "bad_quarter",
        [
            0,
            5
        ]
    )
    def test_add_quarter_bad_quarter(self, bad_quarter):
        with pytest.raises(TypeError):
            utils.add_quarter(2020, bad_quarter)
