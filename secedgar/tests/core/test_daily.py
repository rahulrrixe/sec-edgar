import os
from datetime import date, datetime

import pytest
import secedgar.utils as utils
from secedgar.core.daily import DailyFilings
from secedgar.tests.utils import MockResponse, datapath

cik_file_pairs = [("1000228", "0001209191-18-064398.txt"),
                  ("1000275", "0001140361-18-046093.txt"),
                  ("1000275", "0001140361-18-046095.txt"),
                  ("1000694", "0001144204-18-066755.txt"),
                  ("1001085", "0001104659-18-075315.txt")]


@pytest.fixture(scope="module")
def mock_daily_quarter_directory(monkeymodule):
    """Mocks directory of all daily filings for quarter."""
    monkeymodule.setattr(
        DailyFilings, "_get_listings_directory",
        MockResponse(
            datapath_args=["filings", "daily", "daily_index_2018_QTR4.htm"]))


@pytest.fixture(scope="module")
def mock_daily_idx_file(monkeymodule):
    """Mock idx file from DailyFilings."""

    def _mock_daily_idx_file(*args, **kwargs):
        with open(datapath("filings", "daily", "master.20181231.idx")) as f:
            return f.read()

    monkeymodule.setattr(DailyFilings, "_get_master_idx_file",
                         _mock_daily_idx_file)


class TestDaily:

    @pytest.mark.parametrize("date,expected", [(date(2020, 1, 1), 1),
                                               (date(2020, 3, 31), 1),
                                               (date(2020, 4, 1), 2),
                                               (date(2020, 6, 30), 2),
                                               (date(2020, 7, 1), 3),
                                               (date(2020, 9, 30), 3),
                                               (date(2020, 10, 1), 4),
                                               (date(2020, 12, 31), 4)])
    def test_quarter(self, date, expected):
        assert DailyFilings(date=date).quarter == expected

    @pytest.mark.parametrize("date,expected_filename", [
        (date(2020, 1, 1), "master.20200101.idx"),
        (date(2020, 3, 31), "master.20200331.idx"),
        (date(2020, 4, 1), "master.20200401.idx"),
        (date(2020, 6, 30), "master.20200630.idx"),
    ])
    def test_idx_filename(self, date, expected_filename):
        assert DailyFilings(date=date).idx_filename == expected_filename

    @pytest.mark.parametrize("bad_date", [1.0, 12, "12/31/2018"])
    def test_bad_date_format_fails(self, bad_date):
        with pytest.raises(TypeError):
            DailyFilings(bad_date)

    @pytest.mark.parametrize("key,url", [(cik,
                                          "http://www.sec.gov/Archives/edgar/data/{cik}/{f}".format(
                                              cik=cik, f=f))
                                         for cik, f in cik_file_pairs])
    def test_get_urls(self, mock_daily_quarter_directory, mock_daily_idx_file,
                      key, url):
        daily_filing = DailyFilings(date(2018, 12, 31))
        assert url in daily_filing.get_urls()[key]

    def test_get_listings_directory(self, mock_daily_quarter_directory):
        daily_filing_listing_directory = DailyFilings(date(
            2018, 12, 31))._get_listings_directory()
        assert daily_filing_listing_directory.status_code == 200
        assert "master.20181231.idx" in daily_filing_listing_directory.text

    @pytest.mark.parametrize("company_name", [
        "HENRY SCHEIN INC", "ROYAL BANK OF CANADA", "NOVAVAX INC",
        "BROOKFIELD ASSET MANAGEMENT INC.",
        "PERUSAHAAN PERSEROAN PERSERO PT TELEKOMUNIKASI INDONESIA TBK"
    ])
    def test_get_master_idx_file(self, mock_daily_quarter_directory,
                                 mock_daily_idx_file, company_name):
        daily_filing = DailyFilings(date(2018, 12, 31))
        assert company_name in daily_filing._get_master_idx_file()

    @pytest.mark.parametrize("year,month,day,quarter", [(2018, 1, 1, 1),
                                                        (2017, 5, 1, 2),
                                                        (2016, 6, 30, 2),
                                                        (2015, 7, 1, 3),
                                                        (2014, 9, 30, 3),
                                                        (2013, 10, 1, 4),
                                                        (2012, 11, 20, 4),
                                                        (2011, 12, 31, 4)])
    def test_path_property(self, year, month, day, quarter):
        daily_filing = DailyFilings(date(year, month, day))
        assert daily_filing.path == "Archives/edgar/daily-index/{year}/QTR{quarter}/".format(
            year=year, quarter=quarter)

    @pytest.mark.parametrize("date", [
        date(2020, 1, 1),
        date(2020, 3, 30),
        date(1993, 12, 31),
        datetime(2020, 1, 1)
    ])
    def test_good_date_setter(self, date):
        daily_filing = DailyFilings(date=date)
        assert daily_filing.date == date

    @pytest.mark.parametrize("bad_date", [20201231, "20201231", "2020/12/31"])
    def test_bad_date_on_init(self, bad_date):
        with pytest.raises(TypeError):
            _ = DailyFilings(date=bad_date)

    @pytest.mark.parametrize("bad_date", [20201231, "20201231", "2020/12/31"])
    def test_bad_date_setter_after_init(self, bad_date):
        daily_filing = DailyFilings(date=date(2020, 1, 1))
        with pytest.raises(TypeError):
            daily_filing.date = bad_date

    def test_no_params(self):
        """Params should always be empty."""
        daily_filing = DailyFilings(date(2020, 1, 1))
        assert not daily_filing.params

    @pytest.mark.parametrize("date_tuple,formatted", [
        ((1994, 1, 2), "010294"),
        ((1994, 12, 31), "123194"),
        ((1995, 1, 1), "950101"),
        ((1995, 1, 2), "950102"),
        ((1998, 1, 1), "980101"),
        ((1998, 1, 2), "980102"),
        ((1998, 3, 31), "19980331"),
        ((1998, 4, 1), "19980401"),
        ((1999, 1, 1), "19990101"),
    ])
    def test_master_idx_date_format(self, date_tuple, formatted):
        daily_filing = DailyFilings(date(*date_tuple))
        assert daily_filing._get_idx_formatted_date() == formatted

    @pytest.mark.parametrize("cik,file", cik_file_pairs)
    def test_save_default(self, tmp_data_directory,
                          mock_daily_quarter_directory, mock_daily_idx_file,
                          mock_filing_response, cik, file):
        daily_filing = DailyFilings(date(2018, 12, 31))
        daily_filing.save(tmp_data_directory)
        subdir = os.path.join("20181231", cik)
        path_to_check = os.path.join(tmp_data_directory, subdir, file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize("file", [cf[1] for cf in cik_file_pairs])
    def test_save_with_single_level_date_dir_pattern(
            self, tmp_data_directory, mock_daily_quarter_directory,
            mock_daily_idx_file, mock_filing_response, file):
        daily_filing = DailyFilings(date(2018, 12, 31))
        daily_filing.save(tmp_data_directory,
                          dir_pattern="{date}",
                          date_format="%Y-%m-%d")
        path_to_check = os.path.join(tmp_data_directory, "2018-12-31", file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize("cik,file", cik_file_pairs)
    def test_save_with_single_level_cik_dir_pattern(
            self, tmp_data_directory, mock_daily_quarter_directory,
            mock_daily_idx_file, mock_filing_response, cik, file):
        daily_filing = DailyFilings(date(2018, 12, 31))
        daily_filing.save(tmp_data_directory, dir_pattern="{cik}")
        path_to_check = os.path.join(tmp_data_directory, cik, file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize("cik,file", cik_file_pairs)
    def test_save_with_multi_level_dir_pattern(self, tmp_data_directory,
                                               mock_daily_quarter_directory,
                                               mock_daily_idx_file,
                                               mock_filing_response, cik, file):
        daily_filing = DailyFilings(date(2018, 12, 31))
        daily_filing.save(tmp_data_directory,
                          dir_pattern="{date}/{cik}",
                          date_format="%Y-%m-%d")
        subdir = os.path.join("2018-12-31", cik)
        path_to_check = os.path.join(tmp_data_directory, subdir, file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize("cik,file", cik_file_pairs)
    def test_save_with_multi_level_dir_pattern_date_not_first(
            self, tmp_data_directory, mock_daily_quarter_directory,
            mock_daily_idx_file, mock_filing_response, cik, file):
        daily_filing = DailyFilings(date(2018, 12, 31))
        daily_filing.save(tmp_data_directory,
                          dir_pattern="{cik}/{date}",
                          date_format="%Y-%m-%d")
        subdir = os.path.join(cik, "2018-12-31")
        path_to_check = os.path.join(tmp_data_directory, subdir, file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize("year,quarter", [(1995, 2), (1995, 1), (1994, 4)])
    def test__get_tar_bad_year_quarter(self, year, quarter):
        with pytest.raises(ValueError):
            d = DailyFilings(date=date(year, utils.get_month(quarter), 1))
            d._get_tar_urls()

    def test__get_tar_valid(self):
        d = DailyFilings(date=date(2020, 1, 2))
        urls = d._get_tar_urls()
        assert urls[0].endswith('20200102.nc.tar.gz')
        assert urls[0].startswith('http')

    @pytest.mark.parametrize(
        "bad_entry_filter",
        [
            "entry_filter",
            True,
            False,
            1,
            1.0
        ]
    )
    def test_set_bad_entry_filter(self, bad_entry_filter):
        with pytest.raises(ValueError):
            d = DailyFilings(date=date(2020, 1, 2))
            d.entry_filter = bad_entry_filter

    @pytest.mark.parametrize(
        "good_entry_filter",
        [
            lambda _: True,
            lambda _: False,
            lambda f: f.name.lower().startswith("a")
        ]
    )
    def test_set_good_entry_filter(self, good_entry_filter):
        d = DailyFilings(date=date(2020, 1, 2))
        d.entry_filter = good_entry_filter
        assert callable(d.entry_filter)

    def test_download_all(self, monkeypatch):
        pass
