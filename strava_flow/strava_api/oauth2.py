from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus  # type: ignore


class OAuth2RedirectServer(HTTPServer):
    def __init__(self, server_address: Tuple[str, int], request_handler: type) -> None:
        super().__init__(server_address, request_handler)
        self.query_params: Dict[str, Any] = {}


class OAuth2RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._status_ok()
        query = self._parse_query_params()
        self.server.query_params = query  # type: ignore
        self._write_authentication_status()

    def log_message(self, format: str, *args: List[Any]) -> None:
        pass

    def _status_ok(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _parse_query_params(self) -> Dict[str, Any]:
        parts = urlparse(self.path)
        urlencoded_params = parse_qs(parts.query)
        params = {key: value[0] for key, value in urlencoded_params.items()}
        return params

    def _write_authentication_status(self) -> None:
        self.wfile.write(b'<html><head><title>Authentication Status</title></head>')
        self.wfile.write(b'<body><p>Authentication has completed successfully.</p>')
        self.wfile.write(b'</body></html>')
