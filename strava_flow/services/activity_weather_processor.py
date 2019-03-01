from typing import Dict, Any

from strava_flow.darksky_api.api import DarkskyApi
from strava_flow.schemas.validator import SchemaValidator


class ActivityWeatherProcessor:
    def __init__(self, weather_api: DarkskyApi, schema_validator: SchemaValidator) -> None:
        self._weather_api = weather_api
        self._schema_validator = schema_validator

    def process(self, data: Dict[str, Any]) -> None:
        pass
