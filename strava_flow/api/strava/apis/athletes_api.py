from typing import Any, Dict

from strava_flow.api.strava.apis.abc import StravaBaseApi
from strava_flow.api.strava.http_client import StravaHttpClient


class StravaAthletesApi(StravaBaseApi):
    def __init__(self, http_client: StravaHttpClient) -> None:
        super().__init__(http_client=http_client)

    def get_athlete(self) -> Any:
        url = f'/v3/athlete'
        params: Dict[str, Any] = {}
        return self._http_client.get(url=url, params=params)
