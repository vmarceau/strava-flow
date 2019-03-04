import os
import json
from typing import Dict, Any
from jsonschema import Draft4Validator  # type: ignore


class InvalidSchemaException(Exception):
    pass


class SchemaValidator:
    _SUPPORTED_SCHEMAS = ['ActivityWeatherProcessorTaskV1.json']

    def __init__(self) -> None:
        self._schemas = self._load_schemas()
        self._validators = self._create_validators()

    def validate(self, schema: str, data: Dict[str, Any]) -> None:
        validator = self._get_validator(schema)
        validator.validate(data)

    def _load_schemas(self) -> Dict[str, Any]:
        current_file = os.path.realpath(__file__)
        current_directory = os.path.dirname(current_file)
        schema_directory = os.path.join(current_directory, 'definitions')
        return {
            name: self._load_schema_from_json(os.path.join(schema_directory, name)) for name in self._SUPPORTED_SCHEMAS
        }

    def _create_validators(self) -> Dict[str, Draft4Validator]:
        return {name: Draft4Validator(schema) for name, schema in self._schemas.items()}

    def _get_validator(self, schema: str) -> Draft4Validator:
        if schema in self._validators:
            return self._validators[schema]
        else:
            raise InvalidSchemaException(f'Unsupported schema {schema}')

    @staticmethod
    def _load_schema_from_json(filepath: str) -> Any:
        with open(filepath, 'r') as f:
            content = json.load(f)
        return content
