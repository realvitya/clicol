import os
import tempfile
import unittest

import configparser

from clicol import _compat


class ResourceTests(unittest.TestCase):
    def test_bundled_colors_and_interpolated_colortable(self):
        colors = configparser.ConfigParser()
        _compat.read_config_resource(colors, 'ini/colors_securecrt.ini')
        table = configparser.ConfigParser(dict(colors.items('colors')))
        _compat.read_config_resource(table, 'ini/ct_dbg_net.ini')
        self.assertEqual(table.get('colortable', 'default'), r'\033[0m')

    def test_user_file_overrides_bundled_defaults(self):
        colors = configparser.ConfigParser()
        _compat.read_config_resource(colors, 'ini/colors_securecrt.ini')
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write('[colors]\nc_default = custom\n')
            colors.read([path])
            self.assertEqual(colors.get('colors', 'c_default'), 'custom')
            self.assertTrue(colors.has_option('colors', 'c_bold'))
        finally:
            os.unlink(path)

    def test_all_bundled_colormaps_load(self):
        config = configparser.ConfigParser()
        for name in ('common', 'cisco', 'juniper'):
            _compat.read_config_resource(config, 'ini/cm_' + name + '.ini')
        sections = config.sections()
        for prefix in ('common_', 'cisco_', 'juniper_'):
            self.assertTrue(any(section.startswith(prefix) for section in sections))

    def test_missing_resource_is_ignored(self):
        config = configparser.ConfigParser()
        _compat.read_config_resource(config, 'ini/missing.ini')
        self.assertEqual(config.sections(), [])


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        self.original_entry_points = _compat.metadata.entry_points

    def tearDown(self):
        _compat.metadata.entry_points = self.original_entry_points

    def test_legacy_mapping_api(self):
        _compat.metadata.entry_points = lambda: {'clicol.plugins': ['plugin']}
        self.assertEqual(list(_compat.iter_entry_points('clicol.plugins')), ['plugin'])
        self.assertEqual(list(_compat.iter_entry_points('missing')), [])

    def test_selectable_api(self):
        class Points:
            def select(self, group):
                return ['plugin'] if group == 'clicol.plugins' else []

        _compat.metadata.entry_points = Points
        self.assertEqual(list(_compat.iter_entry_points('clicol.plugins')), ['plugin'])
        self.assertEqual(list(_compat.iter_entry_points('missing')), [])

    def test_installed_builtin_plugin_loads(self):
        points = list(_compat.iter_entry_points('clicol.plugins'))
        plugin = next(point for point in points if point.name == 'HumanNumbers').load()
        self.assertEqual(plugin.__name__, 'HumanNumbers')
        instance = plugin(({}, {}))
        self.assertIn('853,297,735', instance.plugin_postprocess('853297735 packets', ['test']))


if __name__ == '__main__':
    unittest.main()
