import os
import io
import unittest


class TestSfo(unittest.TestCase):

    SFO_FILE = f'tests/data/PARAM.SFO'
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
    OUTFILE = 'out.sfo'
    VARIABLE_KEY_DATA = ('TITLE_01', 'RegionalTitle')

    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        try:
            os.unlink(self.OUTFILE)
        except OSError:
            pass


    def test_read_file(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        self.assertDictEqual(self.SFO_DATA, sfo.parameters._asdict())


    def test_read_stream(self):
        from ps3iso.sfo import SfoFile
        bio = io.BytesIO()
        with open(self.SFO_FILE, 'rb') as f:
            bio.write(f.read())
        bio.seek(0)
        sfo = SfoFile.parse(bio)
        self.assertDictEqual(self.SFO_DATA, sfo.parameters._asdict())


    def test_write_file(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        sfo.write_file(self.OUTFILE)
        with open(self.SFO_FILE, 'rb') as _in:
            with open(self.OUTFILE, 'rb') as _out:
                self.assertEqual(_in.read(), _out.read())

    def test_write_stream(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        bio = io.BytesIO()
        sfo.write(bio)
        bio.seek(0)
        with open(self.SFO_FILE, 'rb') as f:
            expected = f.read()
        self.assertEqual(bio.read(), expected)


    def test_read_brokenfiles(self):
        from ps3iso.sfo import SfoFile
        from ps3iso.sfo.errors import SfoParseError

        with self.assertRaises(SfoParseError):
            SfoFile.parse_file(self.SFO_FILE + '.broken-magic')

        with self.assertRaises(SfoParseError):
            SfoFile.parse_file(self.SFO_FILE + '.truncated')


    def test_verify_parameters(self):
        from ps3iso.sfo.file import SfoFile
        from ps3iso.sfo.parameters import SfoCategory
        from ps3iso.sfo.errors import SfoMissingParameterError
        sfo = SfoFile.parse_file(self.SFO_FILE + '.invalid_ps3')
        with self.assertRaises(SfoMissingParameterError):
            sfo.verify_parameters(SfoCategory.PS3)

    def test_variable_key_param(self):
        from ps3iso.sfo.file import SfoFile
        print(self.SFO_FILE + '.variable-key')
        sfo = SfoFile.parse_file(self.SFO_FILE + '.variable-key')
        key, value = self.VARIABLE_KEY_DATA
        print(sfo.parameters)
        print(key, value)
        self.assertTrue(hasattr(sfo.parameters, key))
        self.assertEqual(getattr(sfo.parameters, key), value)


    def test_format(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        # Make sure attribute replacement works as expected
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
        # Missing Attributes return an empty string
        sfo.remove_parameter('TITLE')
        self.assertEqual(sfo.format('%T'), '')


    def test_parameters_property(self):
        from ps3iso.sfo import SfoFile
        params = SfoFile.parse_file(self.SFO_FILE).parameters
        # Make sure attributes are accessible through property syntax
        self.assertEqual(params.APP_VER, self.SFO_DATA['APP_VER'])
        self.assertEqual(params.ATTRIBUTE, self.SFO_DATA['ATTRIBUTE'])
        self.assertEqual(params.BOOTABLE, self.SFO_DATA['BOOTABLE'])
        self.assertEqual(params.CATEGORY, self.SFO_DATA['CATEGORY'])
        self.assertEqual(params.LICENSE, self.SFO_DATA['LICENSE'])
        self.assertEqual(params.PARENTAL_LEVEL, self.SFO_DATA['PARENTAL_LEVEL'])
        self.assertEqual(params.PS3_SYSTEM_VER, self.SFO_DATA['PS3_SYSTEM_VER'])
        self.assertEqual(params.RESOLUTION, self.SFO_DATA['RESOLUTION'])
        self.assertEqual(params.SOUND_FORMAT, self.SFO_DATA['SOUND_FORMAT'])
        self.assertEqual(params.TITLE, self.SFO_DATA['TITLE'])
        self.assertEqual(params.TITLE_ID, self.SFO_DATA['TITLE_ID'])
        self.assertEqual(params.APP_VER, self.SFO_DATA['APP_VER'])


    def test_get_parameter(self):
        from ps3iso.sfo import SfoFile
        from ps3iso.sfo.errors import SfoParameterNotFoundError
        from ps3iso.sfo.parameters import SfoParameter
        sfo = SfoFile.parse_file(self.SFO_FILE)
        # Make sure the attribute is right
        p = sfo.get_parameter('TITLE')
        self.assertEqual(p, SfoParameter.new('TITLE', p.value))
        # Make sure it references the underlying sfo attribute
        p = sfo.get_parameter('TITLE')
        p.value = 'NewTitle'
        self.assertTrue(hasattr(sfo.parameters, 'TITLE'))
        self.assertEqual(getattr(sfo.parameters, 'TITLE'), 'NewTitle')
        # Make sure it fails on invalid parameter
        with self.assertRaises(SfoParameterNotFoundError):
            sfo.get_parameter('WHOOPS')


    def test_add_parameter(self):
        # Construct an SfoFile object from the sfo file params
        from ps3iso.sfo import SfoFile
        sfo_file = SfoFile.parse_file(self.SFO_FILE)
        params = sfo_file.parameters._asdict()
        sfo_make = SfoFile()
        for k, v in params.items():
            sfo_make.add_parameter(k, v)
        # Make sure all of the internal data is correct
        self.assertEqual(sfo_file.parameters, sfo_make.parameters)
        self.assertEqual(sfo_file.header, sfo_make.header)
        self.assertEqual(sfo_file.index_table, sfo_make.index_table)
        # Make sure that the .write() output is correct
        sfo_make.write_file(self.OUTFILE)
        with open(self.OUTFILE, 'rb') as f:
            written_bytes = f.read()
        with open(self.SFO_FILE, 'rb') as f:
            expected_bytes = f.read()
        self.assertEqual(written_bytes, expected_bytes)


    def test_set_parameter(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        expected_bytes = bytes(sfo)
        # Test predicate
        self.assertEqual(getattr(sfo.parameters, 'TITLE'), self.SFO_DATA['TITLE'])
        # Setting existing parameter changes the value and bytes
        sfo.set_parameter('TITLE', 'NewTitle')
        self.assertEqual(getattr(sfo.parameters, 'TITLE'), 'NewTitle')
        self.assertNotEqual(bytes(sfo), expected_bytes)
        # Changing it back to the old value does not alter the original byte representation
        sfo.set_parameter('TITLE', self.SFO_DATA['TITLE'])
        self.assertEqual(getattr(sfo.parameters, 'TITLE'), self.SFO_DATA['TITLE'])
        self.assertEqual(bytes(sfo), expected_bytes)
        # Setting a missing parameter will create it
        sfo.set_parameter('PARAMS', 'Test Parameters')
        self.assertTrue(hasattr(sfo.parameters, 'PARAMS'))
        self.assertEqual(getattr(sfo.parameters, 'PARAMS'), 'Test Parameters')
        self.assertNotEqual(bytes(sfo), expected_bytes)


    def test_remove_parameter(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        # Remove an attribute
        sfo.remove_parameter('LICENSE')
        with self.assertRaises(AttributeError):
            getattr(sfo.parameters, 'LICENSE')
        # output SFO file is still readable
        sfo.write_file(self.OUTFILE)
        outfile = SfoFile.parse_file(self.OUTFILE)
        with self.assertRaises(AttributeError):
            getattr(sfo.parameters, 'LICENSE')
        self.assertEqual(getattr(outfile.parameters, 'TITLE'), self.SFO_DATA['TITLE'])

    def test_repr(self):
        from ps3iso.sfo import SfoFile
        from ps3iso.sfo._file import SfoIndexTableEntry, SfoHeader, SfoIndexTable, SfoParameterFormat
        sfo = SfoFile.parse_file(self.SFO_FILE)
        self.assertEqual(sfo.index_table, eval(repr(sfo.index_table)))
        self.assertEqual(sfo.header, eval(repr(sfo.header)))
        p = getattr(sfo.parameters, 'TITLE')
        self.assertEqual(p, eval(repr(p)))

    def test_iter(self):
        from ps3iso.sfo import SfoFile
        sfo = SfoFile.parse_file(self.SFO_FILE)
        for key, value in sfo:
            self.assertEqual(getattr(sfo.parameters, key), value)
