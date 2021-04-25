from datetime import date

import pytest
from secedgar.core.combo import ComboFilings


def lambda_matches(a, b):
    return a.__code__.co_code == b.__code__.co_code


def line_matches(a, b):
    return a[0] == b[0] and a[1] == b[1] and lambda_matches(a[2], b[2])


def quarterly_list_matches(l1, l2):
    return all(line_matches(a, b) for (a, b) in zip(l1, l2))


class TestComboFilings:

    def test_combo_quarterly_only_one_year(self):
        combo = ComboFilings(start_date=date(2020, 1, 1),
                             end_date=date(2020, 12, 31))
        expected = [(2020, 1, lambda _: True), (2020, 2, lambda _: True),
                    (2020, 3, lambda _: True), (2020, 4, lambda _: True)]
        assert quarterly_list_matches(combo.quarterly_date_list, expected)
        assert len(combo.daily_date_list) == 0

    def test_combo_quarterly_only_multiple_years(self):
        combo = ComboFilings(start_date=date(2018, 10, 1),
                             end_date=date(2020, 6, 30))
        expected = [
            (2018, 4, lambda _: True),
            (2019, 1, lambda _: True),
            (2019, 2, lambda _: True),
            (2019, 3, lambda _: True),
            (2019, 4, lambda _: True),
            (2020, 1, lambda _: True),
            (2020, 2, lambda _: True),
        ]
        assert quarterly_list_matches(combo.quarterly_date_list, expected)
        assert len(combo.daily_date_list) == 0

    def test_combo_daily_only_single_day(self):
        combo = ComboFilings(start_date=date(2020, 12, 10),
                             end_date=date(2020, 12, 10))
        assert [str(s) for s in combo.daily_date_list] == ["2020-12-10"]
        assert len(combo.quarterly_date_list) == 0

    def test_combo_daily_only_multiple_days(self):
        combo = ComboFilings(start_date=date(2020, 12, 10),
                             end_date=date(2020, 12, 12))
        expected = ["2020-12-10", "2020-12-11", "2020-12-12"]
        assert [str(s) for s in combo.daily_date_list] == expected
        assert len(combo.quarterly_date_list) == 0

    @pytest.mark.parametrize(
        "start_date,end_date,quarterly_expected,daily_expected", [
            (date(2019, 12, 28), date(
                2020, 4, 1), [(2020, 1, lambda _: True)], [
                    "2019-12-28", "2019-12-29", "2019-12-30", "2019-12-31",
                    "2020-04-01"
            ]),
            (date(2020, 3, 30), date(2020, 10, 2), [
                (2020, 2, lambda _: True), (2020, 3, lambda _: True)
            ], ["2020-03-30", "2020-03-31", "2020-10-01", "2020-10-02"]),
            (date(2020, 1, 1), date(2020, 4, 2), [
                (2020, 1, lambda _: True)
            ], ["2020-04-01", "2020-04-02"]),
            (date(2020, 3, 30), date(2020, 9, 30), [
                (2020, 2, lambda _: True), (2020, 3, lambda _: True)
            ], ["2020-03-30", "2020-03-31"]),
            # (date(2020, 1, 1), date(2020, 6, 28), [], [(2020, 1, lambda _: True),
            #                                            (2020, 2, lambda x: date(x['date_filed']) <= date(2020, 6, 28))])  # noqa
        ])
    def test_combo_daily_quarterly_mixed(self, start_date, end_date,
                                         quarterly_expected, daily_expected):
        combo = ComboFilings(start_date=start_date, end_date=end_date)
        assert [str(s) for s in combo.daily_date_list] == daily_expected
        assert quarterly_list_matches(combo.quarterly_date_list, quarterly_expected)
