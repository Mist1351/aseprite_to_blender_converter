import unittest
import tempfile
import os
from dataclasses import asdict

from core.config import load_config, save_config, Config, Size


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_config_file = tempfile.mktemp()

    def tearDown(self):
        if os.path.exists(self.temp_config_file):
            os.remove(self.temp_config_file)

    def test_save_and_load_config(self):
        aseprite_value = 'path/to/aseprite.exe'
        blender_value = 'path/to/blender.exe'
        config = Config(aseprite=aseprite_value, blender=blender_value)
        save_config(config, self.temp_config_file)
        loaded_config = load_config(self.temp_config_file)
        self.assertEqual(loaded_config.aseprite, aseprite_value)
        self.assertEqual(loaded_config.blender, blender_value)

    def test_load_empty_config(self):
        loaded_config = load_config(self.temp_config_file)
        self.assertEqual(loaded_config.aseprite, 'Aseprite.exe')
        self.assertEqual(loaded_config.blender, 'blender.exe')
        self.assertEqual(loaded_config.size, None)
        self.assertEqual(loaded_config.scale, None)
        self.assertEqual(loaded_config.extrude, None)
        self.assertEqual(loaded_config.input, None)
        self.assertEqual(loaded_config.output, None)
        self.assertEqual(loaded_config.svg_only, False)

    def test_save_valid_optional_values_to_config(self):
        pairs = {'size': [None, '16x16', '0x0', None],
                 'scale': [None, '1', '01.000', '1.5', None],
                 'extrude': [None, '1', '01.000', '1.5', None],
                 'input': [None, '', 'file.ext', None],
                 'output': [None, '', 'dir/', None],
                 'svg_only': [True, False]}
        for key, values in pairs.items():
            for value in values:
                config = Config(aseprite='1', blender='2')
                setattr(config, key, value)
                save_config(config, self.temp_config_file)
                loaded_config_dict = asdict(load_config(self.temp_config_file))
                self.assertEqual(loaded_config_dict['aseprite'], '1')
                self.assertEqual(loaded_config_dict['blender'], '2')
                if key == 'size' and value is not None:
                    width, height = [int(x) for x in value.split('x')]
                    self.assertEqual(loaded_config_dict[key], asdict(Size(width, height)))
                else:
                    self.assertEqual(loaded_config_dict[key], value)

    def test_save_invalid_optional_values_to_config(self):
        pairs = {'size': ['', '16x', 'x16', '-16x16', '16x-16', '-16x-16', '16.0x16', '16x16.0'],
                 'scale': ['', '-1', '-1.0'],
                 'extrude': ['', '-1', '-1.0'],
                 'svg_only': [None]}
        for key, values in pairs.items():
            for value in values:
                config = Config(aseprite='1', blender='2')
                setattr(config, key, value)
                save_config(config, self.temp_config_file)
                loaded_config_dict = asdict(load_config(self.temp_config_file))
                self.assertEqual(loaded_config_dict['aseprite'], '1')
                self.assertEqual(loaded_config_dict['blender'], '2')
                if key == 'svg_only':
                    self.assertEqual(loaded_config_dict[key], False)
                else:
                    self.assertEqual(loaded_config_dict[key], None)


if __name__ == '__main__':
    unittest.main()
