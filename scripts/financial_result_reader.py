import dataclasses
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup
from bs4.element import Tag


@dataclass
class Period:
    kind: str = ""
    description: str = ""
    begin: Optional[datetime] = None
    end: Optional[datetime] = None


@dataclass
class Segment:
    order: int = 0
    position: int = 0
    name: str = ""


@dataclass
class Account:
    order: int = 0
    position: int = 0
    kind: str = ""
    name: str = ""
    unit: int = 1


def read_financial_result_html(path: str | Path) -> Optional[BeautifulSoup]:
    """
    決算短信のHTMLをBeautiful Soupに読み込む。

    Parameters
    ----------
    path : str | Path
        決算短信のHTMLファイルのパス

    Returns
    -------
    Optional[BeautifulSoup]
        Beautiful Soupのオブジェクト
    """

    _path = path if isinstance(path, Path) else Path(path)
    text = ""
    if not _path.exists():
        return None

    with _path.open(encoding="utf-8") as r:
        lines = r.readlines()
        # 記載されたテキストの文字種を統一するため、Unicode正規化を行う
        lines = [unicodedata.normalize("NFKC", line) for line in lines]
        text = "".join(lines)

    html = BeautifulSoup(text, features="html.parser")
    return html


def find_segment_tables(html: BeautifulSoup) -> list[Tag]:
    """
    「報告セグメント」のテキストを含むテーブルを検索する

    Parameters
    ----------
    html: BeautifulSoup
        決算短信のHTMLを読み込んだBeautiful Soupのオブジェクト

    Returns
    -------
    list[Tag]
        「報告セグメント」のテキストを含むテーブルのリスト
    """

    tables = html.find_all("table")
    segment_tables = []
    for t in tables:
        text = t.find(text="報告セグメント")
        if text is not None:
            td = text.find_previous("td")
            if td is not None and "colspan" in td.attrs:
                segment_tables.append(t)

    return segment_tables


def read_table_period(table: Tag) -> Period:
    """
    セグメント報告のテーブル上部にあるテキストから、報告年月日を取得する

    Parameters
    ----------
    table: Tag
        セグメント報告のテーブル要素

    Returns
    -------
    Period
        報告年月日
    """

    FIND_LIMIT = 3
    PATTERN = re.compile(r".*(前|当).+(\d{4}年\d+月\d+日).+(\d{4}年\d+月\d+日)")
    DATE_PATTERN = re.compile(r"\d{4}年\d+月\d+日")
    period = Period()

    count = 0
    tag = table
    while count < FIND_LIMIT:
        p = tag.find_previous("p")
        if p is not None:
            text = p.get_text().strip()
            if re.search(PATTERN, text):
                period.description = text
                if "前" in text:
                    period.kind = "previous"
                elif "当" in text:
                    period.kind = "current"

                dates = DATE_PATTERN.findall(period.description)
                if len(dates) == 2:
                    from_date = dates[0].strip()
                    period.begin = datetime.strptime(from_date, "%Y年%m月%d日")
                    to_date = dates[1].strip()
                    period.end = datetime.strptime(to_date, "%Y年%m月%d日")
                break
        count += 1
        tag = p

    return period


def read_table_segments(table: Tag) -> list[Segment]:
    """
    セグメント報告のテーブルから、セグメントの位置を取得する

    Parameters
    ----------
    table: Tag
        セグメント報告のテーブル要素

    Returns
    -------
    list[Segment]
        セグメントのリスト
    """

    merged_cells = table.find_all("td", colspan=True)
    SEGMENT_TEXT = "報告セグメント"
    EXCLUDES = re.compile(r".{0,2}計$")
    NORMALIZER = re.compile(r"\s|\r|\n")
    segments = []  # type: list[Segment]

    segment_title_cells = [cell for cell in merged_cells if SEGMENT_TEXT in cell.text]
    if len(segment_title_cells) == 0:
        return segments
    else:
        segment_title_cell = segment_title_cells[0]
        num_segments = int(segment_title_cell.attrs["colspan"])

        segment_begin = 0
        skipped = 0
        for cell in segment_title_cell.find_previous("tr").find_all("td"):
            if cell.text.strip() == SEGMENT_TEXT:
                break
            else:
                if "rowspan" not in cell.attrs:
                    segment_begin += 1
                else:
                    skipped += 1

        segment_row = segment_title_cell.find_next("tr")
        order = 0
        for i, segment_cell in enumerate(segment_row.find_all("td")):
            if i < segment_begin:
                continue
            elif i < (segment_begin + num_segments):
                segment_text = NORMALIZER.sub("", segment_cell.text.strip())
                if segment_text and not EXCLUDES.match(segment_text):
                    segments.append(Segment(order, i + skipped, segment_text))
                    order += 1

    return segments


def read_table_sales_profit(table: Tag) -> list[Account]:
    """
    セグメント報告のテーブルから、売上・利益の勘定の位置を取得する

    Parameters
    ----------
    table: Tag
        セグメント報告のテーブル要素

    Returns
    -------
    list[Account]
        勘定のリスト
    """

    SUM = re.compile(r".*計$")
    NORMALIZER = re.compile(r"\s|\r|\n")
    UNIT_TEXT = "単位"
    unit = 1000000

    merged_cell = table.find_all("td", colspan=True)
    unit_cells = [cell for cell in merged_cell if UNIT_TEXT in cell.text]

    if len(unit_cells) > 0:
        cell = unit_cells[0]
        if "千円" in cell.text:
            unit = 1000
        elif "十億" in cell.text:
            unit = 1000000000

    rows = table.find_all("tr")

    skip_rows = 0
    sales = None
    profit = None
    for i, row in enumerate(rows):
        if skip_rows > 0:
            skip_rows -= 1
            continue

        account_cell = row.find_next("td")
        if "rowspan" in account_cell.attrs:
            skip_rows = int(account_cell.attrs["rowspan"]) - 1

        account_text = NORMALIZER.sub("", account_cell.text)
        if account_text:
            if sales is None:
                sales = Account(0, i, "Sales", account_text, unit)
                profit = None
            elif sales and SUM.match(account_text):
                sales = Account(0, i, "Sales", sales.name, unit)
                profit = None
            elif sales and profit is None:
                profit = Account(1, i, "Profit", account_text, unit)

    accounts = []
    if sales is not None:
        accounts.append(sales)
    if profit is not None:
        accounts.append(profit)

    return accounts


def read_segment_sales_profit(
    table: Tag, segment: Segment, account: Account
) -> pd.Series:
    """
    セグメント報告のテーブルから、セグメント、勘定を指定してデータを取得する

    Parameters
    ----------
    table: Tag
        セグメント報告のテーブル要素
    segment: Segment
        セグメントの位置
    account: Account
        勘定の位置

    Returns
    -------
    pd.Series
        指定されたセグメント、勘定のデータ
    """

    cell = table.find_all("tr")[account.position].find_all("td")[segment.position]
    data = {}
    data.update(
        {f"segment_{key}": value for key, value in dataclasses.asdict(segment).items()}
    )
    data.update(
        {f"account_{key}": value for key, value in dataclasses.asdict(account).items()}
    )
    value = cell.text.strip().replace("-", "").replace(",", "").replace("△", "-")
    try:
        data["value"] = float(value)
    except ValueError:
        data["value"] = None

    return pd.Series(data)
