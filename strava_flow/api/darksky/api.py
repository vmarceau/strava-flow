from typing import Any, Optional, List

from strava_flow.api.darksky.http_client import DarkskyHttpClient


class DarkskyApi:
    _DEFAULT_LANGUAGE = 'en'
    _DEFAULT_UNITS = 'ca'
    _DEFAULT_FORECAST_EXCLUDE = 'minutely,alerts,flags'
    _DEFAULT_HISTORICAL_EXCLUDE = 'minutely,alerts,flags'

    def __init__(self, token: str) -> None:
        self._http_client = DarkskyHttpClient(token)

    def forecast(
        self,
        latitude: float,
        longitude: float,
        extend: bool = False,
        exclude: Optional[List[str]] = None,
        lang: Optional[str] = None,
        units: Optional[str] = None,
    ) -> Any:
        url = f'/{latitude:.4f},{longitude:.4f}'
        params = {
            'extend': 'hourly' if extend else None,
            'exclude': exclude if exclude else self._DEFAULT_FORECAST_EXCLUDE,
            'lang': lang if lang else self._DEFAULT_LANGUAGE,
            'units': units if units else self._DEFAULT_UNITS,
        }
        return self._http_client.get(url=url, params=params)

    def historical(
        self,
        latitude: float,
        longitude: float,
        time: int,
        exclude: Optional[List[str]] = None,
        lang: Optional[str] = None,
        units: Optional[str] = None,
    ) -> Any:
        url = f'/{latitude:.4f},{longitude:.4f},{time}'
        params = {
            'exclude': exclude if exclude else self._DEFAULT_HISTORICAL_EXCLUDE,
            'lang': lang if lang else self._DEFAULT_LANGUAGE,
            'units': units if units else self._DEFAULT_UNITS,
        }
        return self._http_client.get(url=url, params=params)


if __name__ == '__main__':
    import json
    import datetime
    import pytz
    from strava_flow.configuration.config import load_config
    from strava_flow.utils.time import timestamp_from_datetime

    config = load_config()
    api = DarkskyApi(token=config['darksky_token'])

    latitude = 46.8
    longitude = -71.3
    start_date = datetime.datetime.strptime('2019-03-01T17:01:49Z', '%Y-%m-%dT%H:%M:%SZ')
    start_date = start_date.astimezone(pytz.utc)
    timestamp = int(timestamp_from_datetime(start_date))

    res = api.historical(latitude=latitude, longitude=longitude, time=timestamp)
    res_json = json.dumps(res, indent=2)
    print(res_json)
