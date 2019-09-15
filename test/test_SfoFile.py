import unittest
from ps3iso.sfo import SfoFile, SfoParseError


class TestSfoFile(unittest.TestCase):

    SFO_FILE = 'test/data/PARAM.SFO'

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

    def test_sfo_attributes(self):
        sfo = SfoFile.parse_file(self.SFO_FILE)
        self.maxDiff = None
        self.assertDictEqual(sfo.__dict__, {
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
        })
