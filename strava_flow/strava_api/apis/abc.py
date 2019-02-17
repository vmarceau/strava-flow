import abc

from strava_flow.strava_api.http_client import StravaHttpClient


class StravaBaseApi(metaclass=abc.ABCMeta):  # noqa: B903
    @abc.abstractmethod
    def __init__(self, *, http_client: StravaHttpClient) -> None:
        self._http_client = http_client
