import configparser
import re
from dataclasses import dataclass, asdict
from typing import Optional

PIVOT_VALUES = ['center', 'bottom']


@dataclass
class Size:
    width: int
    height: int

    def __str__(self):
        return f'{self.width}x{self.height}'


@dataclass
class Config:
    blender: str
    aseprite: str
    size: Optional[Size] = None
    scale: Optional[str] = None
    extrude: Optional[str] = None
    input: Optional[str] = None
    output: Optional[str] = None
    svg_only: Optional[bool] = None
    pivot: Optional[str] = None


__DEFAULT_CONFIG_FILENAME = 'config.ini'


def __validate_size_value(value: Optional[str]) -> Optional[Size]:
    if value is not None and re.match('^\\d+x\\d+$', value):
        width_str, height_str = value.split('x')
        return Size(int(width_str), int(height_str))
    return None


def __validate_unsigned_float(value: Optional[str]) -> Optional[str]:
    if value is None or re.match('^\\d+(.\\d+)?$', value):
        return value
    return None


def __validate_pivot(value: Optional[str]) -> Optional[str]:
    if value in PIVOT_VALUES:
        return value
    return None


def load_config(config_filename: str = None) -> Config:
    config = configparser.ConfigParser()
    config.read(config_filename or __DEFAULT_CONFIG_FILENAME)

    return Config(
        blender=config.get('App', 'blender', fallback='blender.exe'),
        aseprite=config.get('App', 'aseprite', fallback='Aseprite.exe'),
        size=__validate_size_value(config.get('User', 'size', fallback=None)),
        scale=__validate_unsigned_float(config.get('User', 'scale', fallback=None)),
        extrude=__validate_unsigned_float(config.get('User', 'extrude', fallback=None)),
        input=config.get('User', 'input', fallback=None),
        output=config.get('User', 'output', fallback=None),
        svg_only=config.getboolean('User', 'svg_only', fallback=False),
        pivot=__validate_pivot(config.get('User', 'pivot', fallback=None))
    )


def save_config(new_config: Config, config_filename: str = None):
    config = configparser.ConfigParser()
    config.read(config_filename or __DEFAULT_CONFIG_FILENAME)
    new_config_dict = asdict(new_config)

    if 'App' not in config:
        config['App'] = {}

    for item in ['blender', 'aseprite']:
        config.set('App', item, new_config_dict[item])

    if 'User' not in config:
        config['User'] = {}

    for item in ['size', 'scale', 'extrude', 'input', 'output', 'svg_only', 'pivot']:
        if item == 'size':
            value = new_config.size
        else:
            value = new_config_dict[item]

        if value is None:
            config.remove_option('User', item)
        else:
            config.set('User', item, str(value))

    with open(config_filename or __DEFAULT_CONFIG_FILENAME, 'w') as configfile:
        config.write(configfile)
