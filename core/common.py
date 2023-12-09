import os
import re
import sys
import argparse
import subprocess
from argparse import Namespace, ArgumentParser
from typing import List, Tuple
from core.config import load_config, PIVOT_VALUES

INPUT_FILE_EXTENSIONS = ['.ase', '.aseprite']
VERSION = '0.2.1a'


class ScriptError(Exception):
    def __init__(self, message='Script execution error'):
        self.message = message
        super().__init__(self.message)


class ArgsError(Exception):
    def __init__(self, message='Args error'):
        self.message = message
        super().__init__(self.message)


def __resource_path(relative_path: str) -> str:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    real_path = os.path.join(base_path, relative_path)
    if not os.path.isfile(real_path):
        real_path = relative_path
    print(f'Script path: {real_path}')
    return real_path


def call_aseprite_script(script: str, **kwargs):
    actual_script = __resource_path(script)
    print(actual_script)
    config = load_config()
    command = [config.aseprite,
               '-b',
               *[x for key, value in kwargs.items() for x in ['--script-param', f'{key}={value}']],
               '--script', actual_script]
    ret = subprocess.run(command, capture_output=True, text=True)
    print(ret.args)
    print(ret.stdout)
    if ret.returncode:
        raise ScriptError(ret.stderr)


def call_blender_script(script: str, **kwargs):
    actual_script = __resource_path(script)
    config = load_config()
    command = [config.blender,
               '-b',
               '-P', actual_script,
               '--', *[x for key, value in kwargs.items() for x in [f'{key}', f'{value}']]]

    ret = subprocess.run(command, capture_output=True, text=True)
    print(ret.args)
    print(ret.stdout)
    if ret.returncode:
        raise ScriptError(ret.stderr)


def get_files(directory: str, pattern: str) -> List[str]:
    return [os.path.join(directory, each) for each in os.listdir(directory) if re.match(pattern, each)]


def __type_size(astring: str) -> str:
    if not re.match('^\\d+x\\d+$', astring):
        raise ValueError
    return astring


def __type_unsigned_float(astring: str) -> str:
    if not re.match('^\\d+(.\\d+)?$', astring):
        raise ValueError
    return astring


def __type_aseprite_file(astring: str) -> str:
    if not any(astring.endswith(ext) for ext in INPUT_FILE_EXTENSIONS):
        raise ValueError
    return astring


def parse_args() -> Tuple[Namespace, ArgumentParser]:
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}')
    parser.add_argument('-b', '--batch', help='run converter without gui',
                        default=False, action='store_true')
    parser.add_argument('-i', '--input', help='aseprite file', type=__type_aseprite_file)
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('--create_output_dir', help='create output dir if not exists',
                        default=False, action='store_true')
    parser.add_argument('-s', '--size', help='size of tile',
                        type=__type_size)
    parser.add_argument('--scale', help='fbx scale',
                        type=__type_unsigned_float)
    parser.add_argument('--extrude', help='fbx scale',
                        type=__type_unsigned_float)
    parser.add_argument('--svg_only', help='Generate svg file only',
                        default=False, action='store_true')
    parser.add_argument('--pivot', help='model pivot', choices=PIVOT_VALUES)
    return parser.parse_args(), parser
