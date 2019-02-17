from typing import Any, Dict

from strava_flow.strava_api.credentials import StravaCredentialsService
from strava_flow.strava_api.http_client import StravaHttpClient
from strava_flow.strava_api.apis.activities_api import StravaActivitiesApi


class StravaApi:
    def __init__(self, config: Dict[str, Any]) -> None:
        credentials_service = self._create_credentials_service(config)
        self._http_client = StravaHttpClient(credentials_service)
        self._activities_api = StravaActivitiesApi(self._http_client)

    @property
    def http_client(self) -> StravaHttpClient:
        return self._http_client

    @property
    def activities(self) -> StravaActivitiesApi:
        return self._activities_api

    def _create_credentials_service(self, config: Dict[str, Any]) -> StravaCredentialsService:
        client_id = config['strava_client_id']
        client_secret = config['strava_client_secret']
        return StravaCredentialsService(cliend_id=client_id, client_secret=client_secret)
