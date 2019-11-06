from __future__ import annotations
import io
import struct
from collections import namedtuple
from typing import BinaryIO, NamedTuple, List

from .parameters import (
    SfoCategory,
    SfoParameter,
    SfoParameterFormat,
    VALID_SFO_PARAMETERS,
    SfoUnknownParameterError)

from ._file import SfoHeader, SfoIndexTable
from .errors import (
    SfoParameterNotFoundError,
    SfoMissingParameterError,
    SfoDuplicateParameterError,
    SfoHeaderParseError,
    SfoParseError,
    SfoIndexTableParseError,
    SfoIndexTableEntryParseError
)


# noinspection PyProtectedMember
class SfoFile(object):
    """
    The main object representing an SFO file.

    Use the :meth:`.parse_file` method to create an object from an existing file,
    or use :meth:`.parse` directly on a seekable object such as :class:`io.BytesIO`

    >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
    >>> sfo
    <SfoFile parameters=12 size=1041>

    >>> sfo.parameters
    SfoParameters(APP_VER='01.00', ATTRIBUTE=32, BOOTABLE=1, CATEGORY='DG', LICENSE='Some example license text, Supports UTF8 glyphs like ©and ®.', PARENTAL_LEVEL=5, PS3_SYSTEM_VER='02.5200', RESOLUTION=63, SOUND_FORMAT=1, TITLE='Example PS3ISO Game Title', TITLE_ID='BLES00000', VERSION='01.00')

    >>> for name, value in sfo:
    ...     print('%s=%s' % (name, value))
    APP_VER=01.00
    ATTRIBUTE=32
    BOOTABLE=1
    CATEGORY=DG
    LICENSE=Some example license text, Supports UTF8 glyphs like ©and ®.
    PARENTAL_LEVEL=5
    PS3_SYSTEM_VER=02.5200
    RESOLUTION=63
    SOUND_FORMAT=1
    TITLE=Example PS3ISO Game Title
    TITLE_ID=BLES00000
    VERSION=01.00

    .. seealso::
        :meth:`.parse_file`,
        :meth:`.format`,
        :meth:`.parameters`

    """
    def __init__(self):
        self.header = SfoHeader()
        self.index_table = SfoIndexTable()
        self._parameters = namedtuple('SfoParameters', [])()

    def _update_index(self):
        self.index_table = SfoIndexTable.build(self._parameters)
        self.header.table_entries = len(self.index_table)
        self.header.key_table_start = self.header.size + self.index_table.size
        self.header.data_table_start = self.header.size + self.index_table.size + len(self._key_table() + self._padding())

    def _key_table(self):
        return b''.join((x.encode('utf8') + b'\0' for x in self.keys))

    def _padding(self) -> bytes:
        header_len = len(bytes(self.header) + bytes(self.index_table) + self._key_table())
        return bytes((4 - (header_len % 4) % 4))


    @classmethod
    def parse(cls, fp: BinaryIO) -> SfoFile:
        """
        Read a seekable binary IO stream containing an SFO file's bytes

        :param fp: Stream or resource pointer
        :rtype: SfoFile

        :Example:

        >>> with open('test/data/PARAM.SFO', 'rb') as f:
        ...     sfo = SfoFile.parse(f)
        >>> print(sfo)
        <SfoFile parameters=12 size=1041>

        """
        try:
            sfo = SfoFile()
            sfo.header = SfoHeader.parse(fp.read(20))
            index_len = 16 * sfo.header.table_entries
            sfo.index_table = SfoIndexTable.parse(fp.read(index_len), sfo.header.table_entries)

            parameters = {}

            for record in sfo.index_table:

                # Key is always a null-terminated string
                fp.seek(sfo.header.key_table_start + record.key_offset)
                c = b''
                s = b''
                while c != b'\0':
                    s += c
                    c = fp.read(1)
                key = s.decode('utf8')

                # Value length (data_len)
                fp.seek(sfo.header.data_table_start + record.data_offset)
                value = fp.read(record.data_len)

                # Value type (data_fmt)
                if record.data_fmt == SfoParameterFormat.int32:
                    value = struct.unpack("<I", value)[0]
                else:
                    value = value.decode('utf8').rstrip('\x00')

                parameters[key] = SfoParameter.new(key, value)

            # Create a new named tuple for the internal parameters attribute
            param_nt = namedtuple('SfoParameters', sorted(parameters))
            sfo._parameters = param_nt(**parameters)

            return sfo

        except SfoUnknownParameterError as ex:
            raise SfoParseError('An invalid parameter was encountered (%s)' % str(ex)) from ex

        except SfoHeaderParseError as ex:
            raise SfoParseError('An invalid SFO header was encountered') from ex

        except SfoIndexTableParseError as ex:
            raise SfoParseError('An invalid SFO index table was encountered') from ex

        except SfoIndexTableEntryParseError as ex:
            raise SfoParseError('An invalid SFO index table entry was encountered') from ex


    @classmethod
    def parse_file(cls, path: str) -> SfoFile:
        """
        Create a new SfoFile object from an existing SFO file

        :param path: Path to the source file
        :rtype: SfoFile

        :Example:

        >>> SfoFile.parse_file('test/data/PARAM.SFO')
        <SfoFile parameters=12 size=1041>

        """
        try:
            with open(path, 'rb') as f:
                return cls.parse(f)
        except SfoParseError as ex:
            raise SfoParseError(str(ex), path) from ex.__cause__


    @property
    def keys(self) -> List[str]:
        r"""
        List of available parameter keys in the current :class:`.SfoFile`

        :rtype: List[str]

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.keys
        ['APP_VER', 'ATTRIBUTE', 'BOOTABLE', 'CATEGORY', 'LICENSE', 'PARENTAL_LEVEL', 'PS3_SYSTEM_VER', 'RESOLUTION', 'SOUND_FORMAT', 'TITLE', 'TITLE_ID', 'VERSION']

        """
        return sorted(self._parameters._asdict().keys())


    @property
    def parameters(self) -> NamedTuple:
        """
        NamedTuple of all SFO parameter values

        :rtype: NamedTuple

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.parameters
        SfoParameters(APP_VER='01.00', ATTRIBUTE=32, BOOTABLE=1, CATEGORY='DG', LICENSE='Some example license text, Supports UTF8 glyphs like ©and ®.', PARENTAL_LEVEL=5, PS3_SYSTEM_VER='02.5200', RESOLUTION=63, SOUND_FORMAT=1, TITLE='Example PS3ISO Game Title', TITLE_ID='BLES00000', VERSION='01.00')

        >>> sfo.parameters.TITLE
        'Example PS3ISO Game Title'

         .. seealso::
            :meth:`.get_parameter`,
            :meth:`.add_parameter`,
            :meth:`.set_parameter`,
            :meth:`.remove_parameter`
        """
        return self._parameters._make(x.value for x in self._parameters)


    def get_parameter(self, name: str) -> SfoParameter:
        r"""
        Retrieve an underlying :class:`.SfoParameter` object.
        If the parameter does not exist, an :class:`.SfoParameterNotFoundError` is raised.

        :param name: Parameter name. Must be a valid SFO parameter as found in :data:`.ps3iso.sfo.parameters.VALID_SFO_PARAMETERS`
        :rtype: SfoParameter

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.get_parameter('TITLE')
        SfoParameter('TITLE', fmt=SfoParameterFormat.utf8, length=None, maxlength=128, required=[SfoCategory.PS3, SfoCategory.PS1], optional=[], value='Example PS3ISO Game Title')

        .. seealso::
            :meth:`.add_parameter`,
            :meth:`.set_parameter`,
            :meth:`.remove_parameter`
        """
        try:
            return getattr(self._parameters, name)
        except AttributeError:
            raise SfoParameterNotFoundError('Parameter Not Found: ' + name)


    def add_parameter(self, name: str, value=None) -> None:
        """
        Add a new parameter to the :class:`.SfoFile`.
        Raises a :class:`.SfoDuplicateError` if the parameter already exists.

        :param name: Parameter name. Must be a valid SFO parameter as found in :data:`.ps3iso.sfo.parameters.VALID_SFO_PARAMETERS`
        :param value: Optionally set a value for the new parameter
        :rtype: None

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.parameters.REGION_DENY
        Traceback (most recent call last):
        AttributeError: 'SfoParameters' object has no attribute 'REGION_DENY'
        >>> sfo.add_parameter('REGION_DENY', 42)
        >>> sfo.parameters.REGION_DENY
        42

        .. seealso::
            :meth:`.get_parameter`,
            :meth:`.set_parameter`,
            :meth:`.remove_parameter`
        """
        if name in self.parameters._fields:
            raise SfoDuplicateParameterError('Unable to add a SFO parameter with a duplicate name')

        p = SfoParameter.new(name, value)
        names = (*self._parameters._fields, name)
        values = (*self._parameters, p)
        self._parameters = namedtuple('SfoParameters', names)(*values)
        self._update_index()


    def set_parameter(self, name: str, value: str) -> None:
        """
        Set the value of a parameter in the current :class:`.SfoFile`, creating it if it does not exist.

        :param name: Parameter name. Must be a valid SFO parameter as found in :data:`.ps3iso.sfo.parameters.VALID_SFO_PARAMETERS`
        :param value: New parameter value
        :rtype: None

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.parameters.TITLE_ID
        'BLES00000'
        >>> sfo.set_parameter('TITLE_ID', 'BLES11111')
        >>> sfo.parameters.TITLE_ID
        'BLES11111'

        .. seealso::
            :meth:`.get_parameter`,
            :meth:`.add_parameter`,
            :meth:`.remove_parameter`
        """
        p = getattr(self._parameters, name, None)
        if p is None:
            self.add_parameter(name, value)
        else:
            p.value = value
        self._update_index()


    def remove_parameter(self, name: str) -> None:
        """
        Remove a parameter from the current :class:`.SfoFile`

        :param name: Parameter name
        :rtype: None

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.parameters.TITLE_ID
        'BLES00000'
        >>> sfo.remove_parameter('TITLE_ID')
        >>> sfo.parameters.TITLE_ID
        Traceback (most recent call last):
        AttributeError: 'SfoParameters' object has no attribute 'TITLE_ID'

        .. seealso::
            :meth:`.get_parameter`,
            :meth:`.add_parameter`,
            :meth:`.set_parameter`
        """
        names, values = list(zip(*((k, v) for k, v in self._parameters._asdict().items() if k != name)))
        self._parameters = namedtuple('SfoParameters', names)(*values)
        self._update_index()


    def verify_parameters(self, category: SfoCategory) -> None:
        """
        Verify that all required parameters exist for the given :class:`.SfoCategory`,
        and raise a :class:`.SfoMissingParameterException` if any are missing.

        :param category: SFO file category to use for required parameters
        :rtype: None

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.verify_parameters(SfoCategory.PS3)
        >>> sfo.remove_parameter('TITLE')
        >>> sfo.verify_parameters(SfoCategory.PS3)
        Traceback (most recent call last):
        ps3iso.sfo.errors.SfoMissingParameterError: Not a valid SFO File for SfoCategory.PS3. Missing Required parameters: {'TITLE'}


        .. seealso ::
            :class:`.SfoCategory`

        """
        # Find all required parameters (string compare is only to work around IPython autoreload)
        all_params = VALID_SFO_PARAMETERS.values()
        required_params = [v.name for v in all_params if str(category) in map(str, v.required)]
        missing = set(required_params) - set(self._parameters._asdict())
        if bool(missing):
            raise SfoMissingParameterError(
                f'Not a valid SFO File for {str(category)}. Missing Required parameters: {missing}')


    def format(self, fmt: str) -> str:
        """
        Return a string representing the PARAM.SFO data contained in the current object.
        Variables in the formatting string are replaced with the corresponding SFO data.

        ========  =========
        Variable  Parameter
        ========  =========
        %a        APP_VER
        %a        ATTRIBUTE
        %C        CATEGORY
        %L        LICENSE
        %P        PARENTAL_LEVEL
        %R        RESOLUTION
        %S        SOUND_FORMAT
        %T        TITLE
        %I        TITLE_ID
        %V        VERSION
        %v        PS3_SYSTEM_VER
        ========  =========

        :param fmt: Formatting string
        :rtype: str

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.format('[%I]_(%T).iso')
        '[BLES00000]_(Example PS3ISO Game Title).iso'

        """
        def param(name):
            if not hasattr(self._parameters, name):
                return ''
            return str(getattr(self._parameters, name).value).strip()

        return (fmt
                .replace('%A', param('APP_VER'))
                .replace('%a', param('ATTRIBUTE'))
                .replace('%C', param('CATEGORY'))
                .replace('%L', param('LICENSE'))
                .replace('%P', param('PARENTAL_LEVEL'))
                .replace('%R', param('RESOLUTION'))
                .replace('%S', param('SOUND_FORMAT'))
                .replace('%T', param('TITLE'))
                .replace('%I', param('TITLE_ID'))
                .replace('%V', param('VERSION'))
                .replace('%v', param('PS3_SYSTEM_VER'))
                )

    def write(self, dst: BinaryIO) -> int:
        r"""
        Write the SFO object to a stream such as :class:`io.BytesIO`

        :param dst: Destination output stream
        :return: Number of bytes written
        :rtype: int

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.set_parameter('TITLE', 'NewTitle')
        >>> bio = io.BytesIO()
        >>> sfo.write(bio)
        1041

        """
        return dst.write(bytes(self))


    def write_file(self, path: str) -> int:
        """
        Write the SFO object to a file

        :param path: Destination file path
        :return: Number of bytes written
        :rtype: int

        :Example:

        >>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
        >>> sfo.set_parameter('TITLE', 'NewTitle')
        >>> sfo.write_file('NewTitle.SFO')
        1041

        """
        with open(path, 'wb') as f:
            return self.write(f)


    def __bytes__(self):
        params = self._parameters._asdict()
        data_table = b''.join((bytes(params[x]) for x in sorted(params.keys())))
        # Concat header
        b = bytes(self.header) + bytes(self.index_table) + self._key_table()
        # key_table padding
        b += self._padding()
        # Add data table and LF
        b += data_table + bytes([0x0a])
        return b


    def __iter__(self):
        # noinspection PyProtectedMember
        return ((k, v) for k, v in self.parameters._asdict().items())


    def __repr__(self):
        return '<%s parameters=%d size=%d>' % (
            type(self).__name__, len(self.parameters), len(bytes(self)))
