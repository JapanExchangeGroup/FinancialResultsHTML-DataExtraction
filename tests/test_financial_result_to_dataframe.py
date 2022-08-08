import os
from pathlib import Path

from scripts.financial_result_to_dataframe import financial_result_to_dataframe


class TestFinancialResultToDataFrame:
    def test_read_html_failed(self) -> None:
        df, result = financial_result_to_dataframe("xxxxx")
        assert df is None
        assert result.read_html_failed

    def test_segment_table_not_exist(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("data/raw/sample3.htm")
        df, result = financial_result_to_dataframe(path)
        assert df is None
        assert not result.read_html_failed
        assert result.segment_table_not_exist

    def test_period_not_found(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/sample1_period_not_exist.htm"
        )
        df, result = financial_result_to_dataframe(path)
        assert df is None
        assert not result.read_html_failed
        assert not result.segment_table_not_exist
        assert result.period_not_found

    def test_account_not_found(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/sample1_account_not_found.htm"
        )
        df, result = financial_result_to_dataframe(path)
        assert df is None
        assert not result.read_html_failed
        assert not result.segment_table_not_exist
        assert not result.period_not_found
        assert not result.segment_not_found
        assert result.account_not_found

    def test_value_read_failed(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath(
            "data/raw/exceptions/sample1_value_read_failed.htm"
        )
        df, result = financial_result_to_dataframe(path)
        assert df is None
        assert not result.read_html_failed
        assert not result.segment_table_not_exist
        assert not result.period_not_found
        assert not result.segment_not_found
        assert not result.account_not_found
        assert result.value_read_failed

    def test_financial_result_to_dataframe(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("data/raw/sample1.htm")
        df, result = financial_result_to_dataframe(path)
        assert df is not None
        assert not result.read_html_failed
        assert not result.segment_table_not_exist
        assert not result.period_not_found
        assert not result.segment_not_found
        assert not result.account_not_found
        assert not result.value_read_failed
        assert result.completed
