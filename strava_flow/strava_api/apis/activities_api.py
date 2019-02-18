from typing import Dict, Any

from strava_flow.strava_api.apis.abc import StravaBaseApi
from strava_flow.strava_api.http_client import StravaHttpClient


class StravaActivitiesApi(StravaBaseApi):
    def __init__(self, http_client: StravaHttpClient) -> None:
        super().__init__(http_client=http_client)

    def get_activity(self, activity_id: str, include_all_efforts: bool = False) -> Dict[str, Any]:
        url = f'/v3/activities/{activity_id}'
        params = {'include_all_efforts': include_all_efforts}
        return self._http_client.get(url=url, params=params)
