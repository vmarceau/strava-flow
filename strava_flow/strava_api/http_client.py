import requests
from typing import Any, Dict, List

from strava_flow.strava_api.credentials import StravaCredentialsService


class StravaHttpClient:
    _URL = 'https://www.strava.com/api'
    _PER_PAGE_DEFAULT = 30
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

    def get_all(self, url: str, **kwargs: Any) -> List[Any]:
        if kwargs['params'].get('per_page') is None:
            kwargs['params']['per_page'] = self._PER_PAGE_DEFAULT

        fetch_more = True
        current_page = 1
        results: List[Any] = []
        while fetch_more:
            kwargs['params']['page'] = current_page
            page_results = self._request(self._GET, url, **kwargs)
            results += page_results
            current_page += 1
            if len(page_results) < kwargs['params']['per_page']:
                fetch_more = False
        return results

    def post(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._POST, url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._PUT, url, **kwargs)

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        kwargs = self._prepare_params(kwargs)
        request_method = getattr(self._session, method)
        response: requests.Response = request_method(self._URL + url, params=kwargs['params'])
        response.raise_for_status()
        return self._format_response(response)

    def _prepare_params(self, kwargs: Any) -> Any:
        params = {'access_token': self._credentials_service.get_access_token()}
        if 'params' in kwargs and kwargs['params'] is not None:
            params.update(kwargs['params'])
        kwargs['params'] = params
        return kwargs

    @staticmethod
    def _format_response(response: requests.Response) -> Any:
        if response.status_code == requests.codes.no_content:
            return {}
        else:
            response_json: Dict[str, Any] = response.json()
            return response_json
