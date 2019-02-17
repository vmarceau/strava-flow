import webbrowser
from urllib.parse import urljoin
from typing import List, Dict, Any, Tuple
from requests_oauthlib import OAuth2Session  # type: ignore
from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus  # type: ignore


class OAuth2RedirectServer(HTTPServer):
    def __init__(self, server_address: Tuple[str, int], request_handler: type) -> None:
        super().__init__(server_address, request_handler)
        self.response_path = ''


class OAuth2RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._status_ok()
        self.server.response_path = self.path  # type: ignore
        self._write_authentication_status()

    def log_message(self, format: str, *args: List[Any]) -> None:
        pass

    def _status_ok(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _write_authentication_status(self) -> None:
        self.wfile.write(b'<html><head><title>Authentication Status</title></head>')
        self.wfile.write(b'<body><p>Authentication has completed successfully.</p>')
        self.wfile.write(b'</body></html>')


class OAuth2AuthenticationClient:
    _REDIRECT_SERVER_PORT = 8000

    def __init__(
        self,
        client_id: int,
        client_secret: str,
        scope: List[str],
        user_agent: str,
        auth_uri: str,
        token_uri: str,
        revoke_uri: str,
    ) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._user_agent = user_agent
        self._auth_uri = auth_uri
        self._token_uri = token_uri
        self._revoke_uri = revoke_uri
        self._redirect_uri = f'http://localhost:{self._REDIRECT_SERVER_PORT}'

    def authenticate(self) -> Dict[str, Any]:
        httpd = OAuth2RedirectServer(('', self._REDIRECT_SERVER_PORT), OAuth2RedirectHandler)
        authorization_url, state = self._get_authorization_url()

        webbrowser.open(authorization_url, new=1, autoraise=True)
        httpd.handle_request()
        response = urljoin(self._redirect_uri, httpd.response_path)

        token = self._fetch_token(response, state)
        return token

    def refresh(self, refresh_token: str) -> Dict[str, Any]:
        strava = OAuth2Session(self._client_id, scope=self._scope, redirect_uri=self._redirect_uri)
        new_token: Dict[str, Any] = strava.refresh_token(
            self._token_uri, client_id=self._client_id, client_secret=self._client_secret, refresh_token=refresh_token
        )
        return {
            'access_token': new_token['access_token'],
            'refresh_token': new_token['refresh_token'],
            'token_expiry': new_token['expires_at'],
        }

    def _get_authorization_url(self) -> Tuple[str, str]:
        strava = OAuth2Session(self._client_id, scope=self._scope, redirect_uri=self._redirect_uri)
        authorization_url, state = strava.authorization_url(self._auth_uri)
        return authorization_url, state

    def _fetch_token(self, response: str, state: str) -> Dict[str, Any]:
        strava = OAuth2Session(self._client_id, scope=self._scope, redirect_uri=self._redirect_uri, state=state)
        token: Dict[str, Any] = strava.fetch_token(
            self._token_uri, client_secret=self._client_secret, authorization_response=response, include_client_id=True
        )
        return {
            'access_token': token['access_token'],
            'refresh_token': token['refresh_token'],
            'token_expiry': token['expires_at'],
        }
