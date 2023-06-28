from __future__ import annotations
import struct
from collections import UserList

from .parameters import SfoParameterFormat
from .errors import SfoHeaderParseError, SfoIndexTableEntryParseError, SfoIndexTableParseError, SfoParseError


class SfoHeader(object):

    SFO_HEADER_MAGIC = 0x46535000

    size = 20

    def __init__(self, magic=SFO_HEADER_MAGIC, version=(1, 1), key_table_start=20, data_table_start=0, table_entries=0):
        self.magic = magic
        self.version = version
        self.key_table_start = key_table_start
        self.data_table_start = data_table_start
        self.table_entries = table_entries

    @classmethod
    def parse(cls, header_bytes, magic_check=True) -> SfoHeader:
        if len(header_bytes) != 20:
            raise SfoHeaderParseError('Header data must be 20 bytes long')

        data = struct.unpack("<5I", header_bytes)
        hdr = cls(magic=data[0],
                  version=tuple(map(int, struct.pack("<H", data[1]))),
                  key_table_start=data[2],
                  data_table_start=data[3],
                  table_entries=data[4])

        if magic_check and hdr.magic != cls.SFO_HEADER_MAGIC:
            raise SfoParseError(f'Magic bytes ({hex(cls.SFO_HEADER_MAGIC)}) not found')
        return hdr

    def __bytes__(self):
        return struct.pack("<5I",
                           self.magic,
                           struct.unpack("<H", bytearray(self.version))[0],
                           self.key_table_start,
                           self.data_table_start,
                           self.table_entries)

    def __repr__(self):
        classname = self.__class__.__name__
        return '%s(magic=%r, version=%r, key_table_start=%d, data_table_start=%d, table_entries=%d)' % (
            classname, self.magic, self.version, self.key_table_start, self.data_table_start, self.table_entries)

    def __eq__(self, other):
        if not isinstance(other, SfoHeader):
            return False
        return self.__dict__ == other.__dict__


class SfoIndexTableEntry(object):

    size = 16

    def __init__(self, key_offset=0, data_fmt=SfoParameterFormat.utf8, data_len=0, data_max_len=0, data_offset=0):
        self.key_offset = key_offset
        self.data_fmt = data_fmt
        self.data_len = data_len
        self.data_max_len = data_max_len
        self.data_offset = data_offset

    @classmethod
    def parse(cls, entry_bytes) -> SfoIndexTableEntry:
        if len(entry_bytes) != 16:
            raise SfoIndexTableEntryParseError('Index Table data must be 16 bytes long')

        data = struct.unpack("<2H3I", entry_bytes)
        return cls(key_offset=data[0],
                   data_fmt=SfoParameterFormat.from_bytes(bytes(struct.pack("<H", data[1]))),
                   data_len=data[2],
                   data_max_len=data[3],
                   data_offset=data[4])

    def __bytes__(self):
        return struct.pack("<2H3I",
                           self.key_offset,
                           struct.unpack("<H", bytes(self.data_fmt))[0],
                           self.data_len,
                           self.data_max_len,
                           self.data_offset)

    def __repr__(self):
        return '%s(key_offset=%s, data_fmt=%s, data_len=%d, data_max_len=%d, data_offset=%d)' % (
            self.__class__.__name__, self.key_offset, self.data_fmt, self.data_len, self.data_max_len, self.data_offset)

    def __eq__(self, other):
        if not isinstance(other, SfoIndexTableEntry):
            return False
        return self.__dict__ == other.__dict__


# noinspection PyProtectedMember
class SfoIndexTable(UserList):
    @property
    def size(self):
        return len(self) * SfoIndexTableEntry.size

    @classmethod
    def parse(cls, table_bytes, table_entries):
        entry_size = SfoIndexTableEntry.size
        if len(table_bytes) != table_entries * entry_size:
            raise SfoIndexTableParseError('Index Table data must be (table_entries * 16) bytes long)')
        tbl = cls()
        for n in range(table_entries):
            entry = SfoIndexTableEntry.parse(table_bytes[(n * entry_size):(n + 1) * entry_size])
            tbl.append(entry)
        return tbl

    @classmethod
    def build(cls, parameters) -> SfoIndexTable:
        table = cls()
        data_offset = 0
        key_offset = 0
        for key in sorted(getattr(parameters, '_fields', [])):
            value = getattr(parameters, key)  # type: SfoParameter
            table.append(SfoIndexTableEntry(
                key_offset=key_offset,
                data_offset=data_offset,
                data_fmt=value.fmt,
                data_len=value.size,
                data_max_len=value.maxlength
            ))
            data_offset += value.maxlength
            key_offset += len(bytes(key, 'utf8')) + 1
        return table

    def __bytes__(self):
        return b''.join(map(bytes, self))

    def __repr__(self):
        return '%s([\n    %s\n])' % (self.__class__.__name__, ',\n    '.join(map(str, self)))
