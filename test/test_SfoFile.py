import unittest
import ps3iso.sfo
from ps3iso.sfo import SfoFile, SfoParseError


class TestSfoFile(unittest.TestCase):

    SFO_FILE = 'test/data/PARAM.SFO'

    SFO_DATA = {
            'APP_VER': '01.00',
            'ATTRIBUTE': 32,
            'BOOTABLE': 1,
            'CATEGORY': 'DG',
            'LICENSE': '''Library programs ©Sony Computer Entertainment Inc. Licensed for play on the PLAYSTATION®3 Computer Entertainment System or authorized PLAYSTATION®3 format systems. For full terms and conditions see the user's manual. This product is authorized and produced under license from Sony Computer Entertainment Inc. Use is subject to the copyright laws and the terms and conditions of the user's license.''', # noqa: E501
            'PARENTAL_LEVEL': 5,
            'PS3_SYSTEM_VER': '02.5200',
            'RESOLUTION': 63,
            'SOUND_FORMAT': 1,
            'TITLE': '---- Example PS3ISO Game Title ----',
            'TITLE_ID': 'BLES00000',
            'VERSION': '01.00',
            'sfo_version': '1.1'
    }

    def test_repr(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)
        sfo_repr = repr(sfo)
        for k, v in sfo.__dict__.items():
            self.assertIn(k, sfo_repr)

    def test_broken_header_magic(self):
        with self.assertRaises(SfoParseError):
            SfoFile.parse_file(self.SFO_FILE + '.broken-magic')

    def test_truncated(self):
        with self.assertRaises(SfoParseError):
            SfoFile.parse_file(self.SFO_FILE + '.truncated')

    def test_invalid_ps3(self):
        with self.assertRaises(SfoParseError):
            SfoFile.parse_file(self.SFO_FILE + '.invalid_ps3')

    def test_parse_file(self):
        SfoFile.parse_file(self.SFO_FILE)

    def test_parse_fp(self):
        with open(self.SFO_FILE, 'rb') as f:
            SfoFile.parse(f)

    def test_parse_stream(self):
        import io
        with open(self.SFO_FILE, 'rb') as f:
            bio = io.BytesIO(f.read())
        SfoFile.parse(bio)

    def test_attributes_exact(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)
        self.maxDiff = None
        self.assertDictEqual(sfo.__dict__, self.SFO_DATA)

    def test_attributes_valid_sfo(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)

        # Invalid SFO param
        with self.assertRaises(AttributeError) as e:
            x = sfo.INVALID_ATTR

        # Valid but missing optional PS3 param
        with self.assertRaises(AttributeError) as e:
            x = sfo.PATCH_FILE

        # Required but somehow missing PS3 param
        del sfo.TITLE
        with self.assertRaises(AttributeError) as e:
            x = sfo.TITLE

    def test_iterator(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)
        keys = [k for k, v in sfo]
        self.assertTrue(all(a in keys for a in ps3iso.sfo.REQUIRED_PS3_SFO_PARAMETERS))

        expected = {k: v for k, v in self.SFO_DATA.items() if k in ps3iso.sfo.VALID_SFO_PARAMETERS}
        self.maxDiff = None
        self.assertEqual(dict((k, v) for k, v in sfo), expected)
        self.assertEqual(dict(sfo), expected)

    def test_format(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)
        self.assertEqual(sfo.format('%A'), str(self.SFO_DATA['APP_VER']))
        self.assertEqual(sfo.format('%a'), str(self.SFO_DATA['ATTRIBUTE']))
        self.assertEqual(sfo.format('%C'), str(self.SFO_DATA['CATEGORY']))
        self.assertEqual(sfo.format('%L'), str(self.SFO_DATA['LICENSE']))
        self.assertEqual(sfo.format('%P'), str(self.SFO_DATA['PARENTAL_LEVEL']))
        self.assertEqual(sfo.format('%R'), str(self.SFO_DATA['RESOLUTION']))
        self.assertEqual(sfo.format('%S'), str(self.SFO_DATA['SOUND_FORMAT']))
        self.assertEqual(sfo.format('%T'), str(self.SFO_DATA['TITLE']))
        self.assertEqual(sfo.format('%I'), str(self.SFO_DATA['TITLE_ID']))
        self.assertEqual(sfo.format('%V'), str(self.SFO_DATA['VERSION']))
        self.assertEqual(sfo.format('%v'), str(self.SFO_DATA['PS3_SYSTEM_VER']))
