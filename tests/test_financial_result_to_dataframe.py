import os
from pathlib import Path

from scripts.financial_result_to_dataframe import financial_result_to_dataframe


class TestFinancialResultToDataFrame:
    def test_read_html_failed(self) -> None:
        df, log = financial_result_to_dataframe("xxxxx")
        assert df is None
        assert log.status.read_html_failed

    def test_segment_table_not_exist(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("data/raw/sample3.htm")
        df, log = financial_result_to_dataframe(path)
        assert df is None
        assert not log.status.read_html_failed
        assert log.status.segment_table_not_exist

    def test_too_little_segment_table(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/too_little_segment_table.htm"
        )
        _, log = financial_result_to_dataframe(path)
        assert log.status.too_little_segment_table

    def test_too_much_segment_tables(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/too_much_segment_tables.htm"
        )
        _, log = financial_result_to_dataframe(path)
        assert log.status.too_much_segment_tables

    def test_period_not_found(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/period_not_exist.htm"
        )
        _, log = financial_result_to_dataframe(path)
        assert not log.status.read_html_failed
        assert not log.status.segment_table_not_exist
        assert log.status.period_not_found

    def test_account_not_found(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/account_not_found.htm"
        )
        _, log = financial_result_to_dataframe(path)
        assert not log.status.read_html_failed
        assert not log.status.segment_table_not_exist
        assert not log.status.period_not_found
        assert not log.status.segment_not_found
        assert log.status.account_not_found

    def test_value_read_failed(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/value_read_failed.htm"
        )
        _, log = financial_result_to_dataframe(path)
        assert not log.status.read_html_failed
        assert not log.status.segment_table_not_exist
        assert not log.status.period_not_found
        assert not log.status.segment_not_found
        assert not log.status.account_not_found
        assert log.status.value_read_failed

    def test_financial_result_to_dataframe(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("data/raw/sample1.htm")
        _, log = financial_result_to_dataframe(path)
        assert not log.status.read_html_failed
        assert not log.status.segment_table_not_exist
        assert not log.status.period_not_found
        assert not log.status.segment_not_found
        assert not log.status.account_not_found
        assert not log.status.value_read_failed
        assert log.status.completed
