import os
import yaml
from typing import Any, Dict


def load_config() -> Dict[str, Any]:
    current_file = os.path.realpath(__file__)
    script_directory = os.path.dirname(current_file)
    config_file = os.path.join(script_directory, 'config.yaml')
    with open(config_file, 'r') as f:
        content = f.read()
    content = os.path.expandvars(content)
    config = yaml.safe_load(content)  # type: Dict[str,Any]
    return config