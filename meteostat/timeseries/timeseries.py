"""
TimeSeries Class

Meteorological data provided by Meteostat (https://dev.meteostat.net)
under the terms of the Creative Commons Attribution-NonCommercial
4.0 International Public License.

The code is licensed under the MIT license.
"""
from copy import copy
from datetime import datetime
from math import floor
from statistics import mean
from typing import Any, Callable, Optional
import pandas as pd
from meteostat.enumerations import Parameter, Granularity
from meteostat.typing import SequenceInput
from meteostat.utils.helpers import get_freq
from meteostat.utils.mutations import fill_df, localize, squash_df


class TimeSeries:
    """
    TimeSeries class which provides features which are
    used across all granularities
    """

    granularity: Granularity
    stations: pd.DataFrame
    start: datetime
    end: datetime
    timezone: Optional[str]
    _df = pd.DataFrame()

    def __init__(
        self,
        granularity: Granularity,
        stations: pd.DataFrame,
        df: pd.DataFrame,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        timezone: Optional[str] = None,
    ) -> None:
        self.granularity = granularity
        self.stations = stations
        self._df = df
        self.start = start if start else df.index.get_level_values("time").min()
        self.end = end if end else df.index.get_level_values("time").max()
        self.timezone = timezone

    def __len__(self) -> int:
        """
        Return number of rows in DataFrame
        """
        return len(self._df)

    @property
    def expected_row_count(self) -> int:
        """
        Expected number of non-NaN values
        """
        diff = self.end - self.start
        return (
            diff.days + 1
            if self.granularity is Granularity.DAILY
            else floor(diff.total_seconds() / 3600) + 1
        ) * len(self.stations)

    def apply(
        self,
        func: Callable,
        parameter: Optional[SequenceInput[Parameter | str] | Parameter | str] = None,
    ):
        """
        Apply a function to the whole time series or specific parameter(s)
        """
        temp = copy(self)

        # Apply function
        if parameter:
            parameter = (
                [parameter] if isinstance(parameter, (Parameter, str)) else parameter
            )
            for p in parameter:
                if p in temp._df.columns:
                    temp._df[p] = temp._df[p].apply(func)
        else:
            temp._df = temp._df.apply(func)

        return temp

    def merge(self, objs: list[Any]) -> Any:
        """
        Merge one or multiple Meteostat time series into the current one
        """
        temp = copy(self)

        if not all(
            obj.granularity == temp.granularity
            and obj.start == temp.start
            and obj.end == temp.end
            and obj.timezone == temp.timezone
            for obj in objs
        ):
            raise ValueError(
                "Can't concatenate time series objects with divergent granularity, start, end or timezone"
            )

        for obj in objs:
            temp._df = pd.concat([temp._df, obj._df], verify_integrity=True)
            temp.stations = pd.concat([temp.stations, obj.stations]).drop_duplicates()

        return temp

    def fetch(self, squash=True, fill=False) -> Optional[pd.DataFrame]:
        """
        Force specific granularity on the time series
        """
        df = copy(self._df)

        if len(self) == 0:
            return None

        if squash:
            df = squash_df(df)

        if fill:
            df = fill_df(df, self.start, self.end, get_freq(self.granularity))

        if self.timezone:
            df = localize(df, self.timezone)

        return df.sort_index()

    def count(self, parameter: Parameter | str) -> int:
        """
        Get number of non-NaN values for a specific parameter
        """
        return self._df[
            parameter if isinstance(parameter, Parameter) else parameter
        ].count()

    def completeness(self, parameter: Parameter | str | None = None) -> float:
        """
        Get completeness for a specific parameter or the whole DataFrame
        """
        df = self.fetch()

        if df is None:
            return 0

        if parameter:
            return round(
                self.count(parameter) / self.expected_row_count,
                2,
            )

        return round(mean([self.completeness(p) for p in df.columns]), 2)