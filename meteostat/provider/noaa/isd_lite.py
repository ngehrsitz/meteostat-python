from datetime import datetime
import gzip
from io import BytesIO
from typing import Union
from numpy import isnan
import pandas as pd
from meteostat.core.pool import Pool
from meteostat.interface.types import Station
from meteostat.provider.noaa.shared import get_ftp_connection
from meteostat.utilities.units import ms_to_kmh, temp_dwpt_to_rhum

# Column ranges
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
# Column names
NAMES = ["time", "temp", "dwpt", "pres", "wdir", "wspd", "cldc", "prcp"]

def map_sky_code(code: Union[int, str]) -> Union[int, None]:
    """
    Only accept okta
    """
    return int(code) if not isnan(code) and int(code) >= 0 and int(code) <= 8 else None

def fetch(usaf: str, wban: str, year: int) -> pd.DataFrame:
    if not usaf:
        return pd.DataFrame()

    ftp = get_ftp_connection()
    ftp.cwd("/pub/data/noaa/isd-lite/" + str(year))

    filename = f"{usaf}-{wban if wban else '99999'}-{year}.gz"

    if filename in ftp.nlst():
        # Download file
        buffer = BytesIO()
        ftp.retrbinary("RETR " + filename, buffer.write)

        # Unzip file
        # BUFFER IS ISSUE
        file = gzip.open(buffer, "rb")
        raw = file.read()
        file.close()

        print(raw)
        exit()

        df = pd.read_fwf(
            BytesIO(raw),
            parse_dates={"time": [0, 1, 2, 3]},
            na_values=["-9999", -9999],
            header=None,
            colspecs=COLSPECS,
        )

        # Rename columns
        df.columns = NAMES

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
        df = df.round(1)

def handler(station: Station, start: datetime, end: datetime, pool: Pool):
    """
    """
    years = range(start.year, end.year + 1)
    data = pool.map(lambda i: fetch(*i), ((
        station["identifiers"]["usaf"] if "usaf" in station["identifiers"] else None,
        station["identifiers"]["wban"] if "wban" in station["identifiers"] else None,
        year
    ) for year in years))
    print(pd.concat(data))
    exit()
    return pd.concat(data)