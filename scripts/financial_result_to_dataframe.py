import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

import scripts.financial_result_reader as frr


@dataclass
class ReadResult:
    read_html_failed: bool = False
    segment_table_not_exist: bool = False
    period_not_found: bool = False
    segment_not_found: bool = False
    account_not_found: bool = False
    value_read_failed: bool = False
    completed: bool = False


def financial_result_to_dataframe(
    path: str | Path,
) -> tuple[Optional[pd.DataFrame], ReadResult]:
    result = ReadResult()

    html = frr.read_financial_result_html(path)
    if html is None:
        result.read_html_failed = True
        return None, result

    segment_tables = frr.find_segment_tables(html)
    if len(segment_tables) == 0:
        result.segment_table_not_exist = True
        return None, result

    data = []
    interrupted = False
    for table in segment_tables:
        period = frr.read_table_period(table)
        if not period.kind:
            result.period_not_found = True
            interrupted = True
            break

        segments = frr.read_table_segments(table)
        if len(segments) == 0:
            result.segment_not_found = True
            interrupted = True
            break

        accounts = frr.read_table_sales_profit(table)
        if len(accounts) != 2:
            result.account_not_found = True
            interrupted = True
            break

        period_dict = {
            f"period_{key}": value for key, value in dataclasses.asdict(period).items()
        }
        _period = pd.Series(period_dict)
        for s in segments:
            for a in accounts:
                _data = frr.read_segment_sales_profit(table, s, a)
                if _data.value is not None:
                    data.append(pd.concat([_period, _data]))
                else:
                    result.value_read_failed = True
                    interrupted = True
                    break

        if interrupted:
            break

    if interrupted:
        return None, result
    else:
        result.completed = True
        return pd.DataFrame(data), result
