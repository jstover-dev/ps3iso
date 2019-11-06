from __future__ import annotations
import struct
import enum
import re

from .errors import SfoUnknownParameterError


class _SfoParameterFormatMeta(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._map = {
            'utf8s': bytes([0x04, 0x00]),
            'utf8': bytes([0x04, 0x02]),
            'int32': bytes([0x04, 0x04])
        }
        for name in cls._map:
            setattr(cls, name, cls(name))

    def _from_bytes(cls, b: bytes) -> SfoParameterFormat:
        for k, v in cls._map.items():
            if b == v:
                return getattr(cls, k)
        raise ValueError(f'Unknown parameter format bytes: ' + str(b))

    def _to_bytes(cls, name: str) -> bytes:
        try:
            return cls._map[name]
        except KeyError:
            raise ValueError('Unknown SFO parameter name: ' + name)

    def __repr__(self):
        return "GG"


# noinspection PyProtectedMember
class SfoParameterFormat(metaclass=_SfoParameterFormatMeta):
    """
    This class represents the valid SFO parameter types

    +--------------------------+--------------------------------+
    | Member                   | Description                    |
    +==========================+================================+
    | SfoParameterFormat.int32 | 32-bit Integer                 |
    +--------------------------+--------------------------------+
    | SfoParameterFormat.utf8  | UTF-8 String (NULL terminated) |
    +--------------------------+--------------------------------+
    | SfoParameterFormat.utf8s | UTF-8 String                   |
    +--------------------------+--------------------------------+
    """
    int32 = None
    utf8 = None
    utf8s = None

    def __init__(self, name):
        self.name = name

    @classmethod
    def from_bytes(cls, b: bytes) -> SfoParameterFormat:
        """
        Parse bytes and return the corresponding SfoParameterFormat.
        Raises ValueError if none is found

        :param b: Bytes to parse
        """
        return cls._from_bytes(b)

    def __bytes__(self):
        return type(self)._to_bytes(self.name)

    def __repr__(self):
        return '%s.%s' % (type(self).__name__, self.name)


class SfoCategory(enum.IntFlag):
    """
    Enum representing valid SFO file categories

    +------------------------+--------------------------+
    | Member                 | Description              |
    +========================+==========================+
    | SfoCategory.PSP        | PSP Bootable Image       |
    +------------------------+--------------------------+
    | SfoCategory.PS1        | PS1 Bootable Image       |
    +------------------------+--------------------------+
    | SfoCategory.PS2        | PS2 Bootable Image       |
    +------------------------+--------------------------+
    | SfoCategory.PS3        | PS3 Bootable Image       |
    +------------------------+--------------------------+
    | SfoCategory.PSPData    | PSP Data Image           |
    +------------------------+--------------------------+
    | SfoCategory.PS1Data    | PS1 Data Image           |
    +------------------------+--------------------------+
    | SfoCategory.PS2Data    | PS2 Data Image           |
    +------------------------+--------------------------+
    | SfoCategory.PS3Data    | PS3 Data Image           |
    +------------------------+--------------------------+

    .. seealso::
        :meth:`.SfoFile.verify_parameters`

    """
    PSP = 0x01
    PS1 = 0x02
    PS2 = 0x04
    PS3 = 0x08
    PSPData = 0x10
    PS1Data = 0x20
    PS2Data = 0x40
    PS3Data = 0x80

    def __repr__(self):
        return '%s.%s' % (self.__class__.__name__, self.name)


class SfoParameter(object):
    """
    Class representing an SFO parameter.

    All valid parameters are defined in :data:`.VALID_SFO_PARAMETERS`

    :paran str name: Parameter name
    :param SfoParameterFormat fmt: Parameter type, see :class:`.SfoParameterFormat`
    :param int length: Initial length of the parameter value
    :param int maxlength: Maximum length of the parameter value
    :param list required: Categories for which this parameter is required
    :param list optional: Categories for which this parameter is optional
    :param value: Set the initial parameter value

    """

    def __init__(self, name,
                 fmt=SfoParameterFormat.int32,
                 length=None,
                 maxlength=None,
                 required=None,
                 optional=None,
                 variable_key_range=None,
                 value=None):

        if maxlength is None:
            if fmt == SfoParameterFormat.int32:
                maxlength = 4
            elif length is not None:
                maxlength = length
            else:
                raise ValueError('string types require a maxlength property')

        if value is None:
            value = 0 if fmt == SfoParameterFormat.int32 else ''

        self._name = name
        self._value = value
        self.fmt = fmt
        self.length = length
        self.maxlength = maxlength
        self.required = required or []
        self.optional = optional or []
        self.variable_key_range = variable_key_range


    def __repr__(self):
        classname = self.__class__.__name__
        return '%s(%r, fmt=%s, length=%r, maxlength=%r, required=%r, optional=%r, value=%r)' % (
            classname, self.name, self.fmt, self.length, self.maxlength, self.required, self.optional, self.value)


    def __eq__(self, other):
        if not isinstance(other, SfoParameter):
            return False
        for key in self.__dict__:
            if key != 'methods':
                if self.__dict__[key] != other.__dict__[key]:
                    return False
        return True

    def __bytes__(self):
        if self.fmt == SfoParameterFormat.int32:
            return struct.pack("<I", self.value)
        elif self.fmt == SfoParameterFormat.utf8s:
            b = bytes(self.value, 'utf8') + b'\0'
        else:
            b = bytes(self.value, 'utf8')
        return b + bytes(self.maxlength - len(b))

    @property
    def name(self):
        """
        Parameter name
        """
        return self._name

    @property
    def size(self):
        """
        Number of bytes the parameter value will occupy when writtern
        """
        if self.fmt == SfoParameterFormat.int32:
            return 4
        else:
            strlen = len(bytes(self._value, 'utf8'))
            if self.fmt == SfoParameterFormat.utf8:
                strlen += 1
            return min(strlen, self.maxlength)

    @property
    def value(self):
        """
        Current parameter value
        """
        return self._value

    @value.setter
    def value(self, val):
        # clamp values to 32-bit range
        if self.fmt == SfoParameterFormat.int32:
            self._value = max(min(int(val), 0xFFFFFFFF), -0xFFFFFFFF)
        # truncate the string to the attribute's maxlength
        elif self.fmt == SfoParameterFormat.utf8:
            self._value = str(val)[:self.maxlength - 1]
        elif self.fmt == SfoParameterFormat.utf8s:
            self._value = str(val)[:self.maxlength]
        else:
            raise Exception('Unknown Attribute Format')

    def copy(self, value=None):
        """
        Create a copy of the SfoParameter, optionally setting it's initial value.

        :Example:

        >>> p = SfoParameter('TITLE', fmt=SfoParameterFormat.utf8, maxlength=1024)
        >>> p.copy('NewValue')
        SfoParameter('TITLE', fmt=SfoParameterFormat.utf8, length=None, maxlength=1024, required=[], optional=[], value='NewValue')

        """
        obj = SfoParameter(self.name,
                           fmt=self.fmt,
                           length=self.length,
                           maxlength=self.maxlength,
                           required=self.required.copy(),
                           optional=self.optional.copy(),
                           value=value)
        return obj

    @classmethod
    def new(cls, name: str, value=None) -> SfoParameter:
        """
        Create a new SFO Parameter. 'name' must be a valid parameter name.
        Optionally set the initial value

        >>> SfoParameter.new('TITLE', 'NewValue')
        SfoParameter('TITLE', fmt=SfoParameterFormat.utf8, length=None, maxlength=128, required=[SfoCategory.PS3, SfoCategory.PS1], optional=[], value='NewValue')

        """
        try:
            return VALID_SFO_PARAMETERS[name].copy(value)
        except KeyError:
            key_regex = re.compile('xx?')
            for pname, param in VALID_SFO_PARAMETERS.items():
                if param.variable_key_range is not None:
                    for x in param.variable_key_range:
                        key = key_regex.sub(x, pname)
                        if key == name:
                            param._name = key
                            return param.copy(value)
            raise SfoUnknownParameterError(name)


# TODO: Only Bootable PS3 and PS1 SFOs have been added for now, but it should be easy to add others.
VALID_SFO_PARAMETERS = {p.name: p for p in ((
    SfoParameter('ACCOUNT_ID',
                 fmt=SfoParameterFormat.utf8s, length=16),

    SfoParameter('ACCOUNTID',
                 fmt=SfoParameterFormat.utf8, length=16),

    SfoParameter('ANALOG_MODE',
                 required=[SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('APP_VER',
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.utf8, length=6, maxlength=8),

    SfoParameter('ATTRIBUTE',
                 optional=[SfoCategory.PS3],
                 required=[SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('BOOTABLE',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('CATEGORY',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.utf8, length=3, maxlength=4),

    SfoParameter('CONTENT_ID',
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.utf8, length=37, maxlength=48),

    SfoParameter('DETAIL',
                 fmt=SfoParameterFormat.utf8, maxlength=1024),

    SfoParameter('GAMEDATA_ID',
                 fmt=SfoParameterFormat.utf8, maxlength=32),

    SfoParameter('ITEM_PRIORITY',
                 fmt=SfoParameterFormat.int32),

    SfoParameter('LANG',
                 fmt=SfoParameterFormat.int32),

    SfoParameter('LICENSE',
                 required=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.utf8, maxlength=512),

    SfoParameter('NP_COMMUNICATION_ID',
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.utf8, length=13, maxlength=16),

    SfoParameter('NPCOMMID',
                 fmt=SfoParameterFormat.utf8, length=12, maxlength=16),

    SfoParameter('PADDING',
                 fmt=SfoParameterFormat.utf8s, length=0, maxlength=8),

    SfoParameter('PARAMS',
                 fmt=SfoParameterFormat.utf8s, length=1024),

    SfoParameter('PARAMS2',
                 fmt=SfoParameterFormat.utf8s, length=12),

    SfoParameter('PARENTAL_LEVEL_x',
                 variable_key_range=['A', 'C', 'E', 'H', 'J', 'K'],
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('PARENTAL_LEVEL',
                 required=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('PARENTALLEVEL',
                 required=[SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('PATCH_FILE',
                 fmt=SfoParameterFormat.utf8, maxlength=32),

    SfoParameter('PS3_SYSTEM_VER',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.utf8, length=8),

    SfoParameter('REGION_DENY',
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('RESOLUTION',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('SAVEDATA_DETAIL',
                 fmt=SfoParameterFormat.utf8, maxlength=1024),

    SfoParameter('SAVEDATA_DIRECTORY',
                 fmt=SfoParameterFormat.utf8, maxlength=64),

    SfoParameter('SAVEDATA_FILE_LIST',
                 fmt=SfoParameterFormat.utf8s, length=3168),

    SfoParameter('SAVEDATA_LIST_PARAM',
                 fmt=SfoParameterFormat.utf8, maxlength=8),

    SfoParameter('SAVEDATA_PARAMS',
                 fmt=SfoParameterFormat.utf8s, length=128),

    SfoParameter('SAVEDATA_TITLE',
                 fmt=SfoParameterFormat.utf8, maxlength=128),

    SfoParameter('SOUND_FORMAT',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.int32),

    SfoParameter('SOURCE',
                 fmt=SfoParameterFormat.int32),

    SfoParameter('SUB_TITLE',
                 fmt=SfoParameterFormat.utf8, maxlength=128),

    SfoParameter('TARGET_APP_VER',
                 fmt=SfoParameterFormat.utf8, length=6, maxlength=8),

    SfoParameter('TITLE',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.utf8, maxlength=128),

    SfoParameter('TITLE_ID',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.utf8, length=10, maxlength=16),

    SfoParameter('TITLE_xx',
                 variable_key_range=['%02d' % x for x in range(30)],
                 fmt=SfoParameterFormat.utf8, maxlength=128),

    SfoParameter('TITLEID0xx',
                 variable_key_range=['%02d' % x for x in range(30)],
                 optional=[SfoCategory.PS3],
                 fmt=SfoParameterFormat.utf8, length=9, maxlength=16),

    SfoParameter('VERSION',
                 required=[SfoCategory.PS3, SfoCategory.PS1],
                 fmt=SfoParameterFormat.utf8, length=6, maxlength=8),

    SfoParameter('XMB_APPS',
                 fmt=SfoParameterFormat.int32),
))}
""" 
    :type: Dict[str, SfoParameter]

    :annotation:

    This data is taken from the parameter table at https://psdevwiki.com/ps3/PARAM.SFO
    Each entry describes a valid SFO parameter, it's type, and length constraints.
    Each parameter can be made 'optional' or 'required' for any SfoCategory's.
    
    .. exec::
        from tabulate import tabulate
        from ps3iso.sfo import VALID_SFO_PARAMETERS
        print(tabulate(
            ((name, param.fmt, param.length, param.maxlength, sorted(param.required) or '', sorted(param.optional) or '') for name, param in VALID_SFO_PARAMETERS.items()),
            ('name', 'fmt', 'length', 'maxlength', 'required', 'optional'),
            tablefmt='rst'))

"""
