import requests
from typing import Any, Dict

from strava_flow.strava_api.credentials import StravaCredentialsService


class StravaHttpClient:
    _URL = 'https://www.strava.com/api/v3'
    _GET = 'get'
    _POST = 'post'
    _PUT = 'put'

    def __init__(self, credentials_service: StravaCredentialsService) -> None:
        self._credentials_service = credentials_service
        self._session = requests.Session()

    def __del__(self) -> None:
        self._session.close()

    def get(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._GET, url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._POST, url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._PUT, url, **kwargs)

    def _request(self, method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        params = self._prepare_params(kwargs)
        request_method = getattr(self._session, method)
        response: requests.Response = request_method(self._URL + url, params=params)
        response.raise_for_status()
        return self._format_response(response)

    def _prepare_params(self, kwargs: Any) -> Any:
        params = {'access_token': self._credentials_service.get_access_token()}
        if 'params' in kwargs and kwargs['params'] is not None:
            params.update(kwargs['params'])
        kwargs['params'] = params
        return kwargs

    @staticmethod
    def _format_response(response: requests.Response) -> Dict[str, Any]:
        if response.status_code == requests.codes.no_content:
            return {}
        else:
            response_json: Dict[str, Any] = response.json()
            return response_json
