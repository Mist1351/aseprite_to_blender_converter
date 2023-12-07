import configparser
import re
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Config:
    blender: str
    aseprite: str
    size: Optional[str] = None
    scale: Optional[str] = None
    extrude: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    svg_only: Optional[bool] = None


_DEFAULT_CONFIG_FILENAME = 'config.ini'


def _validate_size_value(value: Optional[str]) -> Optional[str]:
    if value is None or re.match('^\\d+x\\d+$', value):
        return value
    return None


def _validate_unsigned_float(value: Optional[str]) -> Optional[str]:
    if value is None or re.match('^\\d+(.\\d+)?$', value):
        return value
    return None


def load_config(config_filename: str = None) -> Config:
    config = configparser.ConfigParser()
    config.read(config_filename or _DEFAULT_CONFIG_FILENAME)

    return Config(
        blender=config.get('App', 'blender', fallback='blender.exe'),
        aseprite=config.get('App', 'aseprite', fallback='Aseprite.exe'),
        size=_validate_size_value(config.get('User', 'size', fallback=None)),
        scale=_validate_unsigned_float(config.get('User', 'scale', fallback=None)),
        extrude=_validate_unsigned_float(config.get('User', 'extrude', fallback=None)),
        input=config.get('User', 'input', fallback=None),
        output=config.get('User', 'output', fallback=None),
        svg_only=config.getboolean('User', 'svg_only', fallback=False)
    )


def save_config(new_config: Config, config_filename: str = None):
    config = configparser.ConfigParser()
    config.read(config_filename or _DEFAULT_CONFIG_FILENAME)
    new_config_dict = asdict(new_config)

    if 'App' not in config:
        config['App'] = {}

    for item in ['blender', 'aseprite']:
        config.set('App', item, new_config_dict[item])

    if 'User' not in config:
        config['User'] = {}

    for item in ['size', 'scale', 'extrude', 'input', 'output', 'svg_only']:
        if new_config_dict[item] is None:
            config.remove_option('User', item)
        else:
            config.set('User', item, str(new_config_dict[item]))

    with open(config_filename or _DEFAULT_CONFIG_FILENAME, 'w') as configfile:
        config.write(configfile)
