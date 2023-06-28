from pathlib import Path

import pytest

from ps3iso.game import Game
from ps3iso.sfo import SfoFile

TEST_DATA = Path('tests/data')


@pytest.fixture
def sfo_data() -> dict:
    """
    These values must match the contents of data/PARAM.SFO
    """
    return {
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


@pytest.fixture
def sfo_file() -> Path:
    return TEST_DATA / 'PARAM.SFO'


@pytest.fixture
def game_object(sfo_file: Path) -> Game:
    game = Game('dummy.iso')
    game.sfo = SfoFile.parse_file(sfo_file)
    return game
