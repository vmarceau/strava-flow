from typing import Any, Dict

from strava_flow.api.strava.credentials import StravaCredentialsService
from strava_flow.api.strava.http_client import StravaHttpClient
from strava_flow.api.strava.apis.activities_api import StravaActivitiesApi
from strava_flow.api.strava.apis.athletes_api import StravaAthletesApi


class StravaApi:
    def __init__(self, config: Dict[str, Any]) -> None:
        credentials_service = self._create_credentials_service(config)
        self._http_client = StravaHttpClient(credentials_service)
        self._activities_api = StravaActivitiesApi(self._http_client)
        self._athletes_api = StravaAthletesApi(self._http_client)

    @property
    def activities(self) -> StravaActivitiesApi:
        return self._activities_api

    @property
    def athletes(self) -> StravaAthletesApi:
        return self._athletes_api

    def _create_credentials_service(self, config: Dict[str, Any]) -> StravaCredentialsService:
        client_id = config['strava_client_id']
        client_secret = config['strava_client_secret']
        return StravaCredentialsService(cliend_id=client_id, client_secret=client_secret)


if __name__ == '__main__':
    import os
    import json
    from strava_flow.configuration.config import load_config

    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    config = load_config()
    api = StravaApi(config)

    # res = api.activities.get_activity(2150404083)
    # res = api.activities.get_all_activities(page=1)
    res = api.athletes.get_athlete()
    res_json = json.dumps(res, indent=2)
    print(res_json)
