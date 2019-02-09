import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from strava_flow.utils.time import datetime_from_timestamp


class Credentials:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_expiry: float,
        scopes: List[str],
        user_agent: str,
        invalid: bool = False,
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expiry = token_expiry
        self.user_agent = user_agent
        self.scopes = scopes
        self.invalid = invalid

    def invalidate(self) -> None:
        self.invalid = True

    def access_token_expired(self) -> bool:
        now = datetime.now(timezone.utc)
        if not self.token_expiry:
            return False
        elif not self.invalid and now < datetime_from_timestamp(self.token_expiry):
            return False
        else:
            return True

    @classmethod
    def from_json(cls, content: str) -> 'Credentials':
        data = json.loads(content)
        return cls(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_expiry=data['token_expiry'],
            scopes=data['scopes'],
            user_agent=data['user_agent'],
            invalid=data['invalid'],
        )

    def to_json(self) -> str:
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expiry': self.token_expiry,
            'scope': self.scopes,
            'user_agent': self.user_agent,
            'invalid': self.invalid,
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
            except Exception:
                pass

        return credentials

    def put(self, credentials: Credentials) -> None:
        Path(self._filepath).touch(exist_ok=True)
        with open(self._filepath, 'w') as f:
            f.write(credentials.to_json())

    def delete(self) -> None:
        os.remove(self._filepath)


class StravaCredentialsService:
    _SCOPES = ['activities:read']
    _AUTHORIZE_URI = 'https://www.strava.com/oauth/authorize'
    _DEAUTHORIZE_URI = 'https://www.strava.com/oauth/deauthorize'
    _TOKEN_URI = 'https://www.strava.com/oauth/token'
    _USER_AGENT = 'strava-flow'
    _CREDENTIALS_FOLDER = '.credentials'
    _CREDENTIALS_FILENAME = 'strava.com.json'

    def __init__(self, cliend_id: str, client_secret: str) -> None:
        self._client_id = cliend_id
        self._client_secret = client_secret
        self._storage = self._initialize_storage()

    def get_credentials(self) -> Optional[Credentials]:
        credentials = self._storage.get()
        if not credentials or credentials.invalid or credentials.access_token_expired():
            self._get_new_credentials()
        return credentials

    def revoke_credentials(self) -> None:
        pass

    def _initialize_storage(self) -> CredentialsStorage:
        home = str(Path.home())
        filename = f'{self._client_id}.{self._CREDENTIALS_FILENAME}'
        filepath = os.path.join(home, self._CREDENTIALS_FOLDER, filename)
        return CredentialsStorage(filepath)

    def _get_new_credentials(self) -> None:
        return None
