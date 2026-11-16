import unittest
from types import SimpleNamespace
from unittest.mock import patch

from clicol import clicol, command


class RuntimeTests(unittest.TestCase):
    def test_output_filter_preserves_utf8_and_returns_bytes(self):
        plugins = SimpleNamespace(preprocess=lambda text, effects: text,
                                  postprocess=lambda text, effects: text)
        with patch.multiple(clicol, plugins=plugins, cmap=[], effects=set(),
                            charbuffer='', lastline='', pause=0, pastepause=False,
                            interactive=False, debug=0, WORKING=True, timeout=0):
            text = 'caf\u00e9\r\n'
            self.assertEqual(clicol.ofilter(text.encode('utf-8')), text.encode('utf-8'))
            self.assertEqual(clicol.ofilter(b'bad\xffbyte\n'), b'badbyte\n')

    def test_input_filter_preserves_bytes_and_detects_break(self):
        with patch.multiple(clicol, is_break=False, timeout=0, prevents=0,
                            interactive=False, effects=set(), pastepause_needed=False,
                            pastepause=False, pasteguard=False, debug=0):
            text = 'caf\u00e9'.encode('utf-8')
            self.assertEqual(clicol.ifilter(text), text)
            self.assertFalse(clicol.is_break)
            self.assertEqual(clicol.ifilter(b'\x1c'), b'\x1c')
            self.assertTrue(clicol.is_break)

    def test_highlight_accepts_unicode_input(self):
        with patch('builtins.input', return_value='caf\u00e9'):
            regex = command.getregex()
        self.assertIsNotNone(regex.search('un caf\u00e9'))


if __name__ == '__main__':
    unittest.main()
