import os
from datetime import date

import pytest
from secedgar.filings.master import MasterFilings
from secedgar.tests.utils import MockResponse


@pytest.fixture(scope="module")
def mock_master_quarter_directory(monkeymodule):
    """Mock directory of all filings for quarter.

    Use for MasterFilings object.
    """
    monkeymodule.setattr(MasterFilings, "_get_listings_directory",
                         MockResponse(datapath_args=[
                             "filings", "master", "master_index_1993_QTR4.html"
                         ]))


@pytest.fixture
def mock_master_idx_file(monkeypatch):
    monkeypatch.setattr(MasterFilings, "_get_master_idx_file",
                        lambda *args:
                        MockResponse(datapath_args=["filings", "master", "master.idx"]).text)


class TestMaster:
    @pytest.mark.parametrize(
        "bad_year,expected_error",
        [
            (-1, ValueError),
            (0.0, TypeError),
            (1990, ValueError),
            (1991, ValueError),
            (1992, ValueError),
            ("1993", TypeError),
            ("1993.0", TypeError),

        ]
    )
    def test_bad_year(self, bad_year, expected_error):
        with pytest.raises(expected_error):
            _ = MasterFilings(year=bad_year, quarter=1)

    def test_good_year(self):
        for year in range(1993, date.today().year + 1):
            mf = MasterFilings(year=year, quarter=1)
            assert mf.year == year

    @pytest.mark.parametrize(
        "bad_quarter,expected_error",
        [
            (0.0, TypeError),
            (1.0, TypeError),
            ("1", TypeError),
            ("1.0", TypeError),
            (0, ValueError),
            (5, ValueError),
            (6, ValueError),
            (2020, ValueError)

        ]
    )
    def test_bad_quarter(self, bad_quarter, expected_error):
        with pytest.raises(expected_error):
            _ = MasterFilings(year=2020, quarter=bad_quarter)

    def test_good_quarters(self):
        for quarter in range(1, 5):
            mf = MasterFilings(year=2019, quarter=quarter)
            assert mf.quarter == quarter

    @pytest.mark.parametrize(
        "year,quarter",
        [
            (2018, 1),
            (2019, 2),
            (2020, 3)
        ]
    )
    def test_idx_filename_is_always_the_same(self, year, quarter):
        mf = MasterFilings(year=year, quarter=quarter)
        assert mf.idx_filename == "master.idx"

    def test_always_false_entry_filter(self, mock_master_idx_file):
        master_filing = MasterFilings(year=1993, quarter=4, entry_filter=lambda _: False)
        urls = master_filing.get_urls()
        assert len(urls) == 0

    @pytest.mark.parametrize(
        "subdir,file",
        [
            ("1095785", "9999999997-02-056978.txt"),
            ("11860", "0000011860-94-000005.txt"),
            ("17206", "0000017206-94-000007.txt"),
            ("205239", "0000205239-94-000003.txt"),
            ("20762", "0000950131-94-000025.txt"),
        ]
    )
    def test_save(self, tmp_data_directory,
                  mock_filing_data,
                  mock_master_quarter_directory,
                  mock_master_idx_file,
                  mock_filing_response,
                  subdir,
                  file):
        master_filing = MasterFilings(year=1993, quarter=4)
        master_filing.save(tmp_data_directory)
        subdir = os.path.join("1993", "QTR4", subdir)
        path_to_check = os.path.join(tmp_data_directory, subdir, file)
        assert os.path.exists(path_to_check)

    @pytest.mark.parametrize(
        "original_path,clean_path",
        [
            ("Apple Inc.", "Apple_Inc"),
            ("Microsoft Corporation", "Microsoft_Corporation"),
            ("Bed, Bath, & Beyond", "Bed_Bath__Beyond"),
            ("Company with \\lots\\ of /slashes/", "Company_with_lots_of_slashes")
        ]
    )
    def test_clean_path(self, original_path, clean_path):
        master_filing = MasterFilings(year=2000, quarter=1)
        assert master_filing.clean_directory_path(original_path) == clean_path
