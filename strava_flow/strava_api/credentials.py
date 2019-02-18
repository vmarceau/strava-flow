import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

from strava_flow.utils.time import datetime_from_timestamp
from strava_flow.strava_api.oauth2 import OAuth2AuthenticationClient


class InvalidTokenFormatException(Exception):
    """Received token does not contain the valid format"""


class Credentials:
    CLIENT_ID = 'client_id'
    CLIENT_SECRET = 'client_secret'
    ACCESS_TOKEN = 'access_token'
    REFRESH_TOKEN = 'refresh_token'
    TOKEN_EXPIRY = 'token_expiry'
    SCOPE = 'scope'
    USER_AGENT = 'user_agent'
    INVALID = 'invalid'
    _EXPIRES_SOON_OFFSET = 3600.0

    def __init__(
        self,
        client_id: int,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_expiry: float,
        scope: List[str],
        user_agent: str,
        invalid: bool = False,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.user_agent = user_agent
        self.scope = scope
        self.invalid = invalid

    def invalidate(self) -> None:
        self.invalid = True

    def access_token_expired(self) -> bool:
        return self._is_expired()

    def access_token_soon_expired(self) -> bool:
        return self._is_expired(self._EXPIRES_SOON_OFFSET)

    def _is_expired(self, offset: float = 0.0) -> bool:
        now = datetime.now(timezone.utc)
        if not self.token_expiry:
            return False
        elif not self.invalid and now < datetime_from_timestamp(self.token_expiry - offset):
            return False
        else:
            return True

    @classmethod
    def from_json(cls, content: str) -> 'Credentials':
        data = json.loads(content)
        return cls(
            client_id=data[cls.CLIENT_ID],
            client_secret=data[cls.CLIENT_SECRET],
            access_token=data[cls.ACCESS_TOKEN],
            refresh_token=data[cls.REFRESH_TOKEN],
            token_expiry=data[cls.TOKEN_EXPIRY],
            scope=data[cls.SCOPE],
            user_agent=data[cls.USER_AGENT],
            invalid=data[cls.INVALID],
        )

    def to_json(self) -> str:
        data = {
            self.CLIENT_ID: self.client_id,
            self.CLIENT_SECRET: self.client_secret,
            self.ACCESS_TOKEN: self.access_token,
            self.REFRESH_TOKEN: self.refresh_token,
            self.TOKEN_EXPIRY: self.token_expiry,
            self.SCOPE: self.scope,
            self.USER_AGENT: self.user_agent,
            self.INVALID: self.invalid,
        }
        return json.dumps(data, indent=2)


class CredentialsStorage:
    def __init__(self, filepath: str) -> None:
        self._filepath = filepath

    def get(self) -> Optional[Credentials]:
        credentials = None
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, 'r') as f:
                    content = f.read()
                credentials = Credentials.from_json(content)
            except IOError:
                pass

        return credentials

    def put(self, credentials: Optional[Credentials]) -> None:
        if credentials is not None:
            Path(self._filepath).touch(exist_ok=True)
            with open(self._filepath, 'w') as f:
                f.write(credentials.to_json())

    def delete(self) -> None:
        if os.path.exists(self._filepath):
            os.remove(self._filepath)


class StravaCredentialsService:
    _SCOPE = ['activity:read_all']
    _AUTHORIZE_URI = 'https://www.strava.com/oauth/authorize'
    _REVOKE_URI = 'https://www.strava.com/oauth/deauthorize'
    _TOKEN_URI = 'https://www.strava.com/oauth/token'
    _USER_AGENT = 'strava-flow'
    _CREDENTIALS_FOLDER = '.credentials'
    _CREDENTIALS_FILENAME = 'strava.com.json'

    def __init__(self, cliend_id: int, client_secret: str) -> None:
        self._client_id = cliend_id
        self._client_secret = client_secret
        self._storage = self._initialize_storage()

        self._auth_client = OAuth2AuthenticationClient(
            client_id=self._client_id,
            client_secret=self._client_secret,
            scope=self._SCOPE,
            user_agent=self._USER_AGENT,
            auth_uri=self._AUTHORIZE_URI,
            token_uri=self._TOKEN_URI,
            revoke_uri=self._REVOKE_URI,
        )

    def get_access_token(self) -> str:
        credentials = self._get_credentials()
        return credentials.access_token

    def _get_credentials(self) -> Credentials:
        credentials = self._storage.get()
        if not credentials or credentials.invalid:
            credentials = self._get_new_credentials()
        elif credentials.access_token_soon_expired():
            credentials = self._refresh_existing_credentials(credentials)
        self._storage.put(credentials)
        return credentials

    def _initialize_storage(self) -> CredentialsStorage:
        home = str(Path.home())
        filename = f'{self._client_id}.{self._CREDENTIALS_FILENAME}'
        filepath = os.path.join(home, self._CREDENTIALS_FOLDER, filename)
        return CredentialsStorage(filepath)

    def _get_new_credentials(self) -> Credentials:
        token = self._auth_client.authenticate()
        return self._convert_token_to_credentials(token)

    def _refresh_existing_credentials(self, credentials: Credentials) -> Credentials:
        token = self._auth_client.refresh(credentials.refresh_token)
        return self._convert_token_to_credentials(token)

    def _convert_token_to_credentials(self, token_dict: Dict[str, Any]) -> Credentials:
        if self._is_token_valid(token_dict):
            return Credentials(
                client_id=self._client_id,
                client_secret=self._client_secret,
                access_token=token_dict[Credentials.ACCESS_TOKEN],
                refresh_token=token_dict[Credentials.REFRESH_TOKEN],
                token_expiry=token_dict[Credentials.TOKEN_EXPIRY],
                scope=self._SCOPE,
                user_agent=self._USER_AGENT,
            )
        else:
            raise InvalidTokenFormatException

    @staticmethod
    def _is_token_valid(token_dict: Dict[str, Any]) -> bool:
        return all(
            key in token_dict for key in [Credentials.ACCESS_TOKEN, Credentials.REFRESH_TOKEN, Credentials.TOKEN_EXPIRY]
        )
