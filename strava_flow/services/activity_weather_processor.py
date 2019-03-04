import uuid
import logging
from typing import Dict, Any

from strava_flow.api.darksky.api import DarkskyApi
from strava_flow.schemas.validator import SchemaValidator


class ActivityWeatherProcessor:
    _LATITUDE_TOL = 0.001
    _LONGITUDE_TOL = 0.001
    _TIMESTAMP_TOL = 3600

    def __init__(self, weather_api: DarkskyApi, schema_validator: SchemaValidator, logger: logging.Logger) -> None:
        self._weather_api = weather_api
        self._schema_validator = schema_validator
        self._logger = logger

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        weather_data = self._retrieve_activity_weather_data(data)
        output = self._format_output_data(data, weather_data)
        return self._create_response(output)

    def _retrieve_activity_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        latitude = data['activity_latitude']
        longitude = data['activity_longitude']
        timestamp = data['activity_timestamp']
        elapsed_time = data['activity_elapsed_time']
        if latitude and longitude:
            retrieval_time = timestamp
            if elapsed_time:
                retrieval_time += elapsed_time // 2
            return self._fetch_weather(latitude, longitude, retrieval_time)
        else:
            return {}

    def _fetch_weather(self, latitude: float, longitude: float, time: int) -> Dict[str, Any]:
        weather_data: Dict[str, Any] = self._weather_api.historical(latitude, longitude, time)
        if self._is_weather_data_valid(latitude, longitude, time, weather_data):
            return weather_data
        else:
            return {}

    def _is_weather_data_valid(
        self, latitude: float, longitude: float, time: int, weather_data: Dict[str, Any]
    ) -> bool:
        is_valid = True
        is_valid = is_valid and abs(weather_data['latitude'] - latitude) < self._LATITUDE_TOL
        is_valid = is_valid and abs(weather_data['longitude'] - longitude) < self._LONGITUDE_TOL
        is_valid = is_valid and 'currently' in weather_data
        is_valid = is_valid and abs(weather_data['currently']['time'] - time) < self._TIMESTAMP_TOL
        return is_valid

    def _format_output_data(self, data: Dict[str, Any], weather_data: Dict[str, Any]) -> Dict[str, Any]:
        output = {'id': uuid.uuid1(), 'activity_id': data['activity_id']}
        if weather_data:
            output['latitude'] = weather_data['latitude']
            output['longitude'] = weather_data['longitude']
            output['retrieval_time'] = weather_data['currently']['time']
            output['weather_summary'] = weather_data['currently']['summary']
            output['temperature'] = weather_data['currently']['temperature']
            output['temperature_apparent'] = weather_data['currently']['apparentTemperature']
            output['precipitations_intensity'] = weather_data['currently']['precipIntensity']
            output['precipitations_probability'] = weather_data['currently']['precipProbability']
            output['precipitations_type'] = weather_data['currently']['precipType']
            output['humidity'] = weather_data['currently']['humidity']
            output['wind_speed'] = weather_data['currently']['windSpeed']
        return output

    def _create_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        response: Dict[str, Any] = {'schema': 'ActivityWeatherProcessorTaskV1.json', 'data': data}
        self._schema_validator.validate(response['schema'], response['data'])
        return response
