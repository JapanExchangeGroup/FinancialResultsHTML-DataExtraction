import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd
from bs4.element import Tag

import scripts.financial_result_reader as frr


@dataclass
class ReadResult:
    read_html_failed: bool = False
    segment_table_not_exist: bool = False
    too_little_segment_table: bool = False
    too_much_segment_tables: bool = False
    period_not_found: bool = False
    segment_not_found: bool = False
    account_not_found: bool = False
    value_read_failed: bool = False
    completed: bool = False


class ReadException(Exception):
    def __init__(self, index: int, read_result: str, html: Tag) -> None:
        super().__init__(read_result)
        self.index = index
        self.read_result = read_result
        self.html = html


class ReadLog:
    def __init__(self, status: ReadResult, logs: list[ReadException]) -> None:
        self.status = status
        self.logs = logs


def financial_result_to_dataframe(
    path: str | Path,
) -> tuple[Optional[pd.DataFrame], ReadLog]:
    result = ReadResult()
    logs = []

    html = frr.read_financial_result_html(path)
    if html is None:
        result.read_html_failed = True
        logs.append(ReadException(-1, "read_html_failed", None))
        return None, ReadLog(result, logs)

    segment_tables = frr.find_segment_tables(html)
    if len(segment_tables) == 0:
        result.segment_table_not_exist = True
        logs.append(ReadException(-1, "segment_table_not_exist", None))
        return None, ReadLog(result, logs)
    elif len(segment_tables) < 2:
        result.too_little_segment_table = True
    elif len(segment_tables) > 2:
        result.too_much_segment_tables = True

    data = []
    number_of_completed_table = 0
    read_current = False
    read_previous = False
    for i, table in enumerate(segment_tables):
        period = frr.read_table_period(table)
        if not period.kind:
            result.period_not_found = True
            logs.append(ReadException(i, "period_not_found", table))

        segments = frr.read_table_segments(table)
        if len(segments) == 0:
            result.segment_not_found = True
            logs.append(ReadException(i, "segment_not_found", table))

        accounts = frr.read_table_sales_profit(table)
        if len(accounts) != 2:
            result.account_not_found = True
            logs.append(ReadException(i, "account_not_found", table))

        if (
            not result.period_not_found
            and not result.segment_not_found
            and not result.account_not_found
        ):
            period_dict = {
                f"period_{key}": value
                for key, value in dataclasses.asdict(period).items()
            }
            _period = pd.Series(period_dict)
            for s in segments:
                for a in accounts:
                    _data = frr.read_segment_sales_profit(table, s, a)
                    if _data.value is not None:
                        data.append(pd.concat([_period, _data]))
                    else:
                        result.value_read_failed = True
                        logs.append(ReadException(i, "value_read_failed", table))
                        break

            if not result.value_read_failed:
                if period.kind == "previous":
                    read_previous = True
                elif period.kind == "current":
                    read_current = True
                number_of_completed_table += 1

    if number_of_completed_table == 2 and read_previous and read_current:
        result.completed = True
        return pd.DataFrame(data), ReadLog(result, logs)
    else:
        return pd.DataFrame(data), ReadLog(result, logs)
