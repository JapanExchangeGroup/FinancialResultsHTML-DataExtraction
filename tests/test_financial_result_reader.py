import os
from pathlib import Path

import numpy as np
import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag

import scripts.financial_result_reader as frr


@pytest.fixture
def htmls() -> dict[str, BeautifulSoup]:
    data_dir = os.path.join(os.path.dirname(__file__), "data/raw")
    htmls = {}
    for path in Path(data_dir).glob("*.htm"):
        key = path.name
        htmls[key] = frr.read_financial_result_html(path)
    return htmls


class TestFinancialResultReader:
    def test_read_financial_result_html_from_str(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "data/raw/sample1.htm")
        html = frr.read_financial_result_html(path)
        assert html is not None

    def test_read_financial_result_html_from_path(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("data/raw/sample1.htm")
        html = frr.read_financial_result_html(path)
        assert html is not None

    def test_read_financial_result_html_when_none(self) -> None:
        path = Path(os.path.dirname(__file__)).joinpath("xxxxx")
        html = frr.read_financial_result_html(path)
        assert html is None

    def test_find_segment_tables(self, htmls: dict[str, BeautifulSoup]) -> None:
        for name in htmls:
            segment_tables = frr.find_segment_tables(htmls[name])
            for table in segment_tables:
                # Found tag should include table tag ()
                assert len(table.find_all("tr")) > 0
                # Found table tag should include "報告セグメント"
                assert "報告セグメント" in table.get_text()

            if name in ["sample3.htm", "sample4.htm"]:
                assert len(segment_tables) == 0
            else:
                assert len(segment_tables) > 0

    def test_read_table_period(self, htmls: dict[str, BeautifulSoup]) -> None:
        for name in htmls:
            segment_tables = frr.find_segment_tables(htmls[name])
            for i, t in enumerate(segment_tables):
                period = frr.read_table_period(t)
                assert period.kind is not None

                if name == "sample1.htm":
                    if i == 0:
                        assert period.kind == "previous"
                    else:
                        assert period.kind == "current"

    def get_current_tables(self, htmls: dict[str, BeautifulSoup]) -> dict[str, Tag]:
        tables = {}
        for name in htmls:
            segment_tables = frr.find_segment_tables(htmls[name])
            valid_tables = []
            for table in segment_tables:
                period = frr.read_table_period(table)
                if not period.kind:
                    continue
                segments = frr.read_table_segments(table)
                if len(segments) == 0:
                    continue
                accounts = frr.read_table_sales_profit(table)
                if len(accounts) != 2:
                    continue

                valid_tables.append(table)

            if len(valid_tables) > 0:
                tables[name] = valid_tables[1]  # 0=前期、1=当期
        return tables

    def test_read_table_segments(self, htmls: dict[str, BeautifulSoup]) -> None:
        tables = self.get_current_tables(htmls)

        for name in tables:
            segments = frr.read_table_segments(tables[name])
            names = [s.name for s in segments]
            if name == "sample1.htm":
                np.testing.assert_array_equal(
                    names,
                    [
                        "国内コンビニエンスストア事業",
                        "海外コンビニエンスストア事業",
                        "スーパーストア事業",
                        "百貨店・専門店事業",
                        "金融関連事業",
                        "その他の事業",
                    ],
                )
            elif name == "sample2.htm":
                np.testing.assert_array_equal(
                    names, ["国内ユニクロ事業", "海外ユニクロ事業", "ジーユー事業", "グローバルブランド事業"]
                )
            elif name == "sample5.htm":
                np.testing.assert_array_equal(
                    names, ["コンサルティング", "金融ITソリューション", "産業ITソリューション", "IT基盤サービス"]
                )
            elif name == "sample6.htm":
                np.testing.assert_array_equal(names, ["内視鏡", "治療機器", "科学", "その他"])
            elif name == "sample7.htm":
                np.testing.assert_array_equal(names, ["eコマース事業", "ロジスティクス事業"])

    def test_read_table_sales_profit(self, htmls: dict[str, BeautifulSoup]) -> None:
        tables = self.get_current_tables(htmls)

        for name in tables:
            accounts = frr.read_table_sales_profit(tables[name])
            names = [a.name for a in accounts]
            if name == "sample1.htm":
                np.testing.assert_array_equal(
                    names,
                    ["営業収益", "セグメント利益又は損失(△)"],
                )
            elif name == "sample2.htm":
                np.testing.assert_array_equal(names, ["売上収益", "営業利益又は損失(△)"])
            elif name == "sample5.htm":
                np.testing.assert_array_equal(names, ["売上収益", "営業利益"])
            elif name == "sample6.htm":
                np.testing.assert_array_equal(names, ["売上高", "営業利益又は損失"])
            elif name == "sample7.htm":
                np.testing.assert_array_equal(names, ["売上高", "セグメント利益又は損失(△)"])

    def test_read_segment_sales_profit(self, htmls: dict[str, BeautifulSoup]) -> None:
        tables = self.get_current_tables(htmls)

        for name in tables:
            segments = frr.read_table_segments(tables[name])
            accounts = frr.read_table_sales_profit(tables[name])
            if name == "sample1.htm":
                data = frr.read_segment_sales_profit(
                    tables[name], segments[0], accounts[0]
                )
                assert data.segment_name == "国内コンビニエンスストア事業"
                assert data.account_name == "営業収益"
                assert data.value == 215243.0

            elif name == "sample2.htm":
                data = frr.read_segment_sales_profit(
                    tables[name], segments[3], accounts[1]
                )
                assert data.segment_name == "グローバルブランド事業"
                assert data.account_name == "営業利益又は損失(△)"
                assert data.value == 720.0

            elif name == "sample5.htm":
                data = frr.read_segment_sales_profit(
                    tables[name], segments[1], accounts[1]
                )
                assert data.segment_name == "金融ITソリューション"
                assert data.account_name == "営業利益"
                assert data.value == 11678.0

            elif name == "sample7.htm":
                data = frr.read_segment_sales_profit(
                    tables[name], segments[0], accounts[0]
                )
                assert data.segment_name == "eコマース事業"
                assert data.account_name == "売上高"
                assert data.value == 418698.0
