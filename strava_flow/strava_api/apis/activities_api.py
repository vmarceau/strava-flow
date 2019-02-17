from strava_flow.strava_api.apis.abc import StravaBaseApi
from strava_flow.strava_api.http_client import StravaHttpClient


class StravaActivitiesApi(StravaBaseApi):
    def __init__(self, http_client: StravaHttpClient) -> None:
        super().__init__(http_client=http_client)
