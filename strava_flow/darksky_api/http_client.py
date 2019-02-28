import requests
from typing import Any, Dict


class DarkskyHttpClient:
    _URL = 'https://api.darksky.net/forecast/'
    _GET = 'get'

    def __init__(self, token: str) -> None:
        self._token = token
        self._session = requests.Session()

    def __del__(self) -> None:
        self._session.close()

    def get(self, url: str, **kwargs: Any) -> Any:
        return self._request(self._GET, url, **kwargs)

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        request_url = self._prepare_url(url)
        request_method = getattr(self._session, method)
        response: requests.Response = request_method(request_url, params=kwargs['params'])
        response.raise_for_status()
        return self._format_response(response)

    def _prepare_url(self, url: str) -> str:
        return self._URL + self._token + url

    @staticmethod
    def _format_response(response: requests.Response) -> Any:
        if response.status_code == requests.codes.no_content:
            return {}
        else:
            response_json: Dict[str, Any] = response.json()
            return response_json
