from typing import Optional, Union
from urllib.error import HTTPError
from numpy import isnan
import pandas as pd
from meteostat.core.logger import logger
from meteostat.utils.decorators import cache
from meteostat.typing import QueryDict
from meteostat.utils.converters import ms_to_kmh, temp_dwpt_to_rhum

ISD_LITE_ENDPOINT = "https://www.ncei.noaa.gov/pub/data/noaa/isd-lite/"
COLSPECS = [
    (0, 4),
    (5, 7),
    (8, 10),
    (11, 13),
    (13, 19),
    (19, 25),
    (25, 31),
    (31, 37),
    (37, 43),
    (43, 49),
    (49, 55),
]
COLUMN_NAMES = ["time", "temp", "dwpt", "pres", "wdir", "wspd", "cldc", "prcp"]


def map_sky_code(code: Union[int, str]) -> Optional[int]:
    """
    Only accept okta
    """
    return int(code) if not isnan(code) and int(code) >= 0 and int(code) <= 8 else None


@cache(60 * 60 * 24, "pickle")
def get_df(usaf: str, wban: str, year: int) -> Optional[pd.DataFrame]:
    if not usaf:
        return None

    filename = f"{usaf}-{wban if wban else '99999'}-{year}.gz"

    try:
        df = pd.read_fwf(
            f"{ISD_LITE_ENDPOINT}/{year}/{filename}",
            parse_dates={"time": [0, 1, 2, 3]},
            na_values=["-9999", -9999],
            header=None,
            colspecs=COLSPECS,
            compression="gzip",
        )

        # Rename columns
        df.columns = COLUMN_NAMES

        # Adapt columns
        df["temp"] = df["temp"].div(10)
        df["dwpt"] = df["dwpt"].div(10)
        df["pres"] = df["pres"].div(10)
        df["wspd"] = df["wspd"].div(10).apply(ms_to_kmh)
        df["cldc"] = df["cldc"].apply(map_sky_code)
        df["prcp"] = df["prcp"].div(10)

        # Calculate humidity data
        # pylint: disable=unnecessary-lambda
        df["rhum"] = df.apply(lambda row: temp_dwpt_to_rhum(row), axis=1)

        # Drop dew point column
        # pylint: disable=no-member
        df = df.drop("dwpt", axis=1)

        # Set index
        df = df.set_index("time")

        # Round decimals
        return df.round(1)

    except HTTPError as error:
        if error.status == 404:
            logger.info(f"ISD Lite file not found: {filename}")
        else:
            logger.error(
                f"Couldn't load ISD Lite file {filename} (status: {error.status})"
            )
        return None

    except Exception as error:
        logger.error(error)
        return None


def fetch(query: QueryDict) -> Optional[pd.DataFrame]:
    """ """
    years = range(query["start"].year, query["end"].year + 1)
    data = tuple(
        map(
            lambda i: get_df(*i),
            (
                (
                    query["station"]["identifiers"]["usaf"]
                    if "usaf" in query["station"]["identifiers"]
                    else None,
                    query["station"]["identifiers"]["wban"]
                    if "wban" in query["station"]["identifiers"]
                    else None,
                    year,
                )
                for year in years
            ),
        )
    )

    return pd.concat(data) if len(data) and not all(d is None for d in data) else None
