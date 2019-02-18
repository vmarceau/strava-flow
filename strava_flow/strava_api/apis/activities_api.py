from typing import Any, Optional

from strava_flow.strava_api.apis.abc import StravaBaseApi
from strava_flow.strava_api.http_client import StravaHttpClient


class StravaActivitiesApi(StravaBaseApi):
    def __init__(self, http_client: StravaHttpClient) -> None:
        super().__init__(http_client=http_client)

    def get_activity(self, activity_id: int, include_all_efforts: bool = False) -> Any:
        url = f'/v3/activities/{activity_id}'
        params = {'include_all_efforts': include_all_efforts}
        return self._http_client.get(url=url, params=params)

    def get_all_activities(
        self,
        before: Optional[int] = None,
        after: Optional[int] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
    ) -> Any:
        url = '/v3/activities'
        params = {'before': before, 'after': after, 'per_page': per_page, 'page': page}
        if per_page is None and page is None:
            # @todo: imlement http client method to iterate on all pages
            raise NotImplementedError
        else:
            return self._http_client.get(url=url, params=params)
