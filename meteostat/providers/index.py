from datetime import datetime
from meteostat import types
from meteostat.enumerations import Granularity, Parameter, Provider, Priority


PROVIDERS: list[types.Provider] = [
    {
        "id": Provider.DWD_CLIMATE_HOURLY,
        "name": "DWD Climate Hourly",
        "granularity": Granularity.HOURLY,
        "priority": Priority.HIGHEST,
        "countries": ["DE"],
        "parameters": [Parameter.TEMP, Parameter.PRCP, Parameter.WDIR],
        "start": datetime(1939, 1, 1, 0, 0, 0),
        "license": "https://www.dwd.de/DE/service/copyright/copyright_node.html",
        "module": "meteostat.providers.dwd.climate_hourly",
    },
    {
        "id": Provider.DWD_CLIMATE_DAILY,
        "name": "DWD Climate Daily",
        "granularity": Granularity.DAILY,
        "priority": Priority.HIGHEST,
        "countries": ["DE"],
        "parameters": [Parameter.TEMP, Parameter.PRCP, Parameter.WDIR],
        "start": datetime(1781, 1, 1, 0, 0, 0),
        "license": "https://www.dwd.de/DE/service/copyright/copyright_node.html",
        "module": "meteostat.providers.dwd.climate_daily",
    },
    {
        "id": Provider.NOAA_ISD_LITE,
        "name": "NOAA ISD Lite",
        "granularity": Granularity.HOURLY,
        "priority": Priority.HIGH,
        "parameters": [Parameter.TEMP, Parameter.PRCP, Parameter.WDIR],
        "start": datetime(1931, 1, 1, 0, 0, 0),
        "module": "meteostat.providers.noaa.isd_lite",
    },
    {
        "id": Provider.NOAA_GHCND,
        "name": "NOAA GHCN Daily",
        "granularity": Granularity.DAILY,
        "priority": Priority.HIGH,
        "parameters": [
            Parameter.TAVG,
            Parameter.TMIN,
            Parameter.TMAX,
            Parameter.PRCP,
            Parameter.SNOW,
            Parameter.WSPD,
            Parameter.WDIR,
            Parameter.WPGT,
            Parameter.TSUN,
            Parameter.CLDC,
        ],
        "start": datetime(1931, 1, 1, 0, 0, 0),
        "module": "meteostat.providers.noaa.ghcnd",
    },
    {
        "id": Provider.SYNOP,
        "name": "Meteostat SYNOP",
        "granularity": Granularity.HOURLY,
        "priority": Priority.MEDIUM,
        "parameters": [
            Parameter.TEMP,
            Parameter.RHUM,
            Parameter.PRCP,
            Parameter.SNOW,
            Parameter.SNWD,
            Parameter.WDIR,
            Parameter.WSPD,
            Parameter.WPGT,
            Parameter.PRES,
            Parameter.TSUN,
            Parameter.SGHI,
            Parameter.SDNI,
            Parameter.SDHI,
            Parameter.CLDC,
            Parameter.VSBY,
            Parameter.COCO
        ],
        "start": datetime(2015, 8, 7, 17, 0, 0),
        "module": "meteostat.providers.meteostat.synop"
    },
    {
        "id": Provider.METAR,
        "name": "Meteostat METAR",
        "granularity": Granularity.HOURLY,
        "priority": Priority.LOW,
        "parameters": [
            Parameter.TEMP,
            Parameter.RHUM,
            Parameter.WDIR,
            Parameter.WSPD,
            Parameter.PRES,
            Parameter.COCO
        ],
        "start": datetime(2015, 8, 7, 17, 0, 0),
        "module": "meteostat.providers.meteostat.metar"
    },
    {
        "id": Provider.MOSMIX,
        "name": "Meteostat MOSMIX",
        "granularity": Granularity.HOURLY,
        "priority": Priority.LOWEST,
        "parameters": [
            Parameter.TEMP,
            Parameter.RHUM,
            Parameter.PRCP,
            Parameter.WDIR,
            Parameter.WSPD,
            Parameter.WPGT,
            Parameter.PRES,
            Parameter.TSUN,
            Parameter.SGHI,
            Parameter.CLDC,
            Parameter.VSBY,
            Parameter.COCO
        ],
        "start": datetime(2015, 8, 7, 17, 0, 0),
        "module": "meteostat.providers.meteostat.mosmix"
    }
]
