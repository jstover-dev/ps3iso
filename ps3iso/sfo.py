from __future__ import annotations
import struct
from typing import BinaryIO
from collections import namedtuple

_SfoIndexEntry = namedtuple('SfoIndexEntry', ['key_offset', 'fmt', 'len', 'maxlen', 'data_offset'])

SFO_HEADER_MAGIC = [0x00, 0x50, 0x53, 0x46]

SFO_PARAMETER_FORMAT = {
    'utf8s': [0x04, 0x00],
    'utf8': [0x04, 0x02],
    'int32': [0x04, 0x04],
}

VALID_SFO_PARAMETERS = {
    'ACCOUNT_ID':           'utf8s',
    'ACCOUNTID':            'utf8',
    'ANALOG_MODE':          'int32',
    'APP_VER':              'utf8',
    'ATTRIBUTE':            'int32',
    'BOOTABLE':             'int32',
    'CATEGORY':             'utf8',
    'CONTENT_ID':           'utf8',
    'DETAIL':               'utf8',
    'GAMEDATA_ID':          'utf8',
    'ITEM_PRIORITY':        'int32',
    'LANG':                 'int32',
    'LICENSE':              'utf8',
    'NP_COMMUNICATION_ID':  'utf8',
    'NPCOMMID':             'utf8',
    'PADDING':              'utf8s',
    'PARAMS':               'utf8s',
    'PARAMS2':              'utf8s',
    'PARENTAL_LEVEL_x':     'int32',
    'PARENTAL_LEVEL':       'int32',
    'PARENTALLEVEL':        'int32',
    'PATCH_FILE':           'utf8',
    'PS3_SYSTEM_VER':       'utf8',
    'REGION_DENY':          'int32',
    'RESOLUTION':           'int32',
    'SAVEDATA_DETAIL':      'utf8',
    'SAVEDATA_DIRECTORY':   'utf8',
    'SAVEDATA_FILE_LIST':   'utf8s',
    'SAVEDATA_LIST_PARAM':  'utf8s',
    'SAVEDATA_PARAMS':      'utf8',
    'SAVEDATA_TITLE':       'utf8',
    'SOUND_FORMAT':         'int32',
    'SOURCE':               'int32',
    'SUB_TITLE':            'utf8',
    'TARGET_APP_VER':       'utf8',
    'TITLE':                'utf8',
    'TITLE_ID':             'utf8',
    'TITLE_xx':             'utf8',
    'TITLEID0xx':           'utf8',
    'VERSION':              'utf8',
    'XMB_APPS':             'int32',
}

REQUIRED_PS3_SFO_PARAMETERS = [
    'BOOTABLE',
    'CATEGORY',
    'LICENSE',
    'PARENTAL_LEVEL',
    'PATCH_FILE',
    'PS3_SYSTEM_VER',
    'RESOLUTION',
    'SOUND_FORMAT',
    'TITLE',
    'TITLE_ID',
    'VERSION',
]

OPTIONAL_PS3_SFO_PARAMETERS = [
    'APP_VER',
    'ATTRIBUTE',
    'CONTENT_ID',
    'GAMEDATA_ID',
    'NP_COMMUNICATION_ID',
    'PARENTAL_LEVEL_x',
    'PATCH_FILE',
    'REGION_DENY',
    'TITLE_xx',
    'XMB_APPS',
]

assert all(x in VALID_SFO_PARAMETERS for x in REQUIRED_PS3_SFO_PARAMETERS)
assert all(x in VALID_SFO_PARAMETERS for x in OPTIONAL_PS3_SFO_PARAMETERS)
assert all(x in SFO_PARAMETER_FORMAT for x in VALID_SFO_PARAMETERS.values())


class SfoParseError(Exception):
    pass


class SfoFile(object):
    """
        SfoFile is a class capable of parsing the PARAM.SFO file found on Playstation 3 game discs
    """

    def __repr__(self):
        return '\n'.join(f'{k}: {v}' for k, v in self.__dict__.items())

    def __getattr__(self, item):
        if item not in VALID_SFO_PARAMETERS:
            raise AttributeError(f'`{item}` is not a valid SFO parameter)')
        elif item in OPTIONAL_PS3_SFO_PARAMETERS:
            raise AttributeError(f'Optional PS3 SFO parameter `{item}` not found')
        elif item in REQUIRED_PS3_SFO_PARAMETERS:
            raise AttributeError(f'Required PS3 SFO parameter `{item}` not found. This is not a valid PS3 SFO')

    def __iter__(self):
        return ((k, v) for k, v in self.__dict__.items() if k in VALID_SFO_PARAMETERS)

    def format(self, fmt: str) -> str:
        """
        Return a string representing the PARAM.SFO data contained in the current object.
        Wildcards in the formatting string are replaced with the corresponding SFO data.

        ========  =========
        Variable  Parameter
        ========  =========
        %a        APP_VER
        %a        ATTRIBUTE
        %C        CATEGORY
        %L        LICENSE
        %P        PARENTAL_LEVEL
        %p        PS3_SYSTEM_VER
        %R        RESOLUTION
        %S        SOUND_FORMAT
        %T        TITLE
        %I        TITLE_ID
        %V        VERSION
        ========  =========

        :param fmt: Formatting string
        """
        def param(name):
            return str(getattr(self, name, '')).strip()
        return (fmt
                .replace('%A', param('APP_VER'))
                .replace('%a', param('ATTRIBUTE'))
                .replace('%C', param('CATEGORY'))
                .replace('%L', param('LICENSE'))
                .replace('%P', param('PARENTAL_LEVEL'))
                .replace('%p', param('PS3_SYSTEM_VER'))
                .replace('%R', param('RESOLUTION'))
                .replace('%S', param('SOUND_FORMAT'))
                .replace('%T', param('TITLE'))
                .replace('%I', param('TITLE_ID'))
                .replace('%V', param('VERSION'))
                )

    @classmethod
    def parse(cls, fp: BinaryIO) -> SfoFile:
        """
        Parse the file or stream and create a new SfoFile object

        :param fp: Opened file or seekable stream to parse
        """
        fp.seek(0)

        if list(cls._readbytes(fp, 4)) != SFO_HEADER_MAGIC:
            raise SfoParseError(f'Magic bytes ({SFO_HEADER_MAGIC}) not found')

        sfo_data = {
            'sfo_version': '.'.join((str(int(b)) for b in cls._readbytes(fp, 4).rstrip(b'\x00')))
        }

        _key_table_start = cls._readint(fp)
        _data_table_start = cls._readint(fp)
        _table_entries = cls._readint(fp)
        _index = cls._read_index(fp, _table_entries)
        sfo_data.update(
            cls._read_data(fp, _index, _key_table_start, _data_table_start)
        )

        missing = [x for x in REQUIRED_PS3_SFO_PARAMETERS if x not in sfo_data]
        if len(missing) > 1:
            raise SfoParseError(f'Not a valid PS3 image. Required SFO parameters were missing: {missing}')

        psf = cls()
        psf.__dict__ = sfo_data
        return psf

    @classmethod
    def parse_file(cls, path: str) -> SfoFile:
        """
        Parse the file at the given path with :meth:`.parse()`
        """
        with open(path, 'rb') as f:
            return cls.parse(f)

    @staticmethod
    def _readbytes(src, length):
        data = bytearray(src.read(length))
        if len(data) != length:
            raise SfoParseError(f'Encountered EOF while reading {length} bytes')
        return data

    @classmethod
    def _readint(cls, src):
        return struct.unpack("<I", cls._readbytes(src, 4))[0]

    @classmethod
    def _readshort(cls, src):
        return struct.unpack("<H", cls._readbytes(src, 2))[0]

    @classmethod
    def _readstring(cls, src, offset, encoding='utf-8'):
        src.seek(offset)
        c = b''
        s = b''
        while c != b'\x00':
            s += c
            c = src.read(1)
        return s.decode(encoding)

    @classmethod
    def _read_index(cls, src, nkeys):
        indexes = []
        for _ in range(nkeys):
            _key_offset = cls._readshort(src)
            _fmt_bytes = list(bytearray(struct.pack("<H", cls._readshort(src))))
            _fmt = 'unknown'
            _len = cls._readint(src)
            _maxlen = cls._readint(src)
            _data_offset = cls._readint(src)
            for name, val in SFO_PARAMETER_FORMAT.items():
                if val == _fmt_bytes:
                    _fmt = name
                    break
            indexes += [_SfoIndexEntry(_key_offset, _fmt, _len, _maxlen, _data_offset)]
        return indexes

    @classmethod
    def _read_data(cls, src, index, key_table_offset, data_table_offset):
        data_table = {}
        for record in index:
            keyname = cls._readstring(src, key_table_offset + record.key_offset)
            src.seek(data_table_offset + record.data_offset)
            keydata = cls._readbytes(src, record.len)
            if record.fmt in ['utf8', 'utf8s']:
                keydata = keydata.decode('utf8').rstrip('\x00')
            elif record.fmt == 'int32':
                keydata = struct.unpack("<I", keydata)[0]
            data_table[keyname] = keydata
        return data_table
