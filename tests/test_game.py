import json
from pathlib import Path

import pytest

from ps3iso.game import Game
from ps3iso.sfo import SfoFile


def test_format_file(sfo_file: Path):
    # Check game.format_file works as expected
    game = Game('test.iso')
    assert not game.exists
    game.sfo = SfoFile.parse_file(sfo_file)
    assert hasattr(game.sfo.parameters, 'TITLE')
    assert hasattr(game.sfo.parameters, 'TITLE_ID')
    title = getattr(game.sfo.parameters, 'TITLE')
    title_id = getattr(game.sfo.parameters, 'TITLE_ID')
    assert game.format_file('test.iso', '[%I]-(%T)') == Path(f'[{title_id}]-({title}).iso')


def test_print_info_json(game_object: Game, sfo_data: dict, capfd: pytest.CaptureFixture):
    # Test print_info can construct basic JSON
    game_object.print_info('{"title":"%T", "id":"%I"}')
    out, err = capfd.readouterr()
    out = json.loads(out)
    assert out['title'] == sfo_data['TITLE']
    assert out['id'] == sfo_data['TITLE_ID']
