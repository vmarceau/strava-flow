import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from strava_flow.utils.time import datetime_from_timestamp


class StravaCredentials:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        access_token: str,
        refresh_token: str,
        token_expiry: float,
        scope: str,
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
        now = datetime.now(timezone.utc)
        if not self.token_expiry:
            return False
        elif not self.invalid and now < datetime_from_timestamp(self.token_expiry):
            return False
        else:
            return True

    @classmethod
    def from_json(cls, content: str) -> 'StravaCredentials':
        data = json.loads(content)
        return cls(
            client_id=data['client_id'],
            client_secret=data['client_secret'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_expiry=data['token_expiry'],
            scope=data['scope'],
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
            'scope': self.scope,
            'user_agent': self.user_agent,
            'invalid': self.invalid,
        }
        return json.dumps(data, indent=2)


class CredentialsStorage:
    def __init__(self, filename: str) -> None:
        self._filename = filename

    def get(self) -> Optional[StravaCredentials]:
        credentials = None
        try:
            with open(self._filename, 'r') as f:
                content = f.read()
            credentials = StravaCredentials.from_json(content)
        except IOError:
            pass

        return credentials

    def put(self, credentials: StravaCredentials) -> None:
        Path(self._filename).touch(exist_ok=True)
        with open(self._filename, 'w') as f:
            f.write(credentials.to_json())

    def delete(self) -> None:
        os.remove(self._filename)
