import io
import sys
import json
import unittest
import unittest.mock


class TestGame(unittest.TestCase):

    SFO_FILE = 'test/data/PARAM.SFO'
    SFO_DATA = {
        'APP_VER': '01.00',
        'ATTRIBUTE': 32,
        'BOOTABLE': 1,
        'CATEGORY': 'DG',
        'LICENSE': '''Some example license text, Supports UTF8 glyphs like ©and ®.''',
        'PARENTAL_LEVEL': 5,
        'PS3_SYSTEM_VER': '02.5200',
        'RESOLUTION': 63,
        'SOUND_FORMAT': 1,
        'TITLE': 'Example PS3ISO Game Title',
        'TITLE_ID': 'BLES00000',
        'VERSION': '01.00',
    }

    @property
    def dummy_game(self):
        from ps3iso.game import Game
        from ps3iso.sfo import SfoFile
        game = Game('dummy.iso')
        game.sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        return game


    def setUp(self):
        self.maxDiff = None


    def test_format_file(self):
        from ps3iso.game import Game
        from ps3iso.sfo import SfoFile
        game = Game('test.iso')
        self.assertFalse(game.exists)
        sfo = SfoFile.parse_file(self.SFO_FILE)
        game.sfo = sfo

        self.assertEqual(
            str(game.format_file('test.iso', '[%I]-(%T)')),
            '[%s]-(%s).iso' % (sfo.parameters.TITLE_ID, sfo.parameters.TITLE))


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_print_info_json(self, stdout):
        # Test print_info can construct basic JSON
        self.dummy_game.print_info('{"title":"%T", "id":"%I"}')
        out = json.loads(stdout.getvalue())
        self.assertEqual(out['title'], self.SFO_DATA['TITLE'])
        self.assertEqual(out['id'], self.SFO_DATA['TITLE_ID'])
