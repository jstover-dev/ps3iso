from __future__ import annotations
import io
import re
import glob
import subprocess
from pathlib import Path
from collections import Counter
from typing import Iterator, Union, List

from .sfo import SfoFile


class Game(object):

    def __init__(self, iso_path):
        """
        Class representing a set of files making up a Playstation 3 game
        An existing .iso file must be passed, files with any extension matching the base name
        will be found and included in all operations

        :param Path or str iso_path: Path to an existing .iso file
        """
        self.iso = Path(iso_path).resolve()
        self.files = set(self.iso.parent.glob(glob.escape(self.iso.stem) + '.*'))
        self.sfo = self.extract_sfo(self.iso)

    @classmethod
    def extract_sfo(cls, iso_path: Union[str, Path]) -> SfoFile:
        """
        Read the PARAM.SFO data from an .iso file

        .. seealso:: :meth:`.SfoFile.parse`

        :param iso_path: Path to the .iso file to read
        """
        iso_path = Path(iso_path)
        cmd = ['isoinfo', '-i', str(iso_path), '-x', '/PS3_GAME/PARAM.SFO;1']
        proc = subprocess.run(cmd, capture_output=True)
        proc.check_returncode()
        with io.BytesIO(proc.stdout) as f:
            sfo = SfoFile.parse(f)
        return sfo

    def format_file(self, f: Union[str, Path], fmt: str, fill='') -> Path:
        """
        Return a new path for an input file, formatted according to the SFO data and formatting string.
        The existing file extension will be preserved.

        .. seealso:: :meth:`.SfoFile.format`

        :param f: Path to an existing file
        :param fmt: Formatting string to use for new file name
        :param fill: String to use for replacing invalid characters
        """
        f = Path(f)
        name = self.sfo.format(fmt)
        name = re.sub(r'[\\/*?:<>"|%]', fill, name)
        return (f.parent / name).with_suffix(f.suffix.lower())

    def print_info(self, fmt=None) -> None:
        """
        Print information about the current game set.
        Accepts a custom output formatting string with SFO parameter wildcard support

        .. seealso:: :meth:`.SfoFile.format`

        :param str fmt: Formatting string to use for output
        """
        if fmt is not None:
            for f in self.files:
                print(self.sfo.format(fmt)
                      .replace('\\n', '\n')
                      .replace('\\t', '\t')
                      .replace('%F', str(f)))
        else:
            width = max(len(str(k)) for k, v in self.sfo)
            print(f'\n{self.iso}')
            print('\n'.join(f'\t{k.ljust(width)}: {v}' for k, v in self.sfo))

    def __repr__(self):
        return f'<{self.iso}|+{len(self.files) - 1}>'

    @classmethod
    def search(cls, path: Union[str, Path]) -> Iterator[SfoFile]:
        """
        Search for .iso files in the given path. Non-recursive and case-insensitive

        :param: Path to search
        """
        path = Path(path)
        if path.resolve().is_dir():
            for fpath in path.glob(r'*.[Ii][Ss][Oo]'):
                yield cls(fpath)
        else:
            yield cls(path)

    @staticmethod
    def rename_all(games: List[Game], fmt: str) -> int:
        """
        Rename all files for the given games according to the formatting string

        .. seealso:: :meth:`.SfoFile.format`

        :param games: List of games to rename
        :param fmt: Formatting string to use as file name template
        """
        # Create a list of (src, dst) tuples
        targets = set((f, game.format_file(f, fmt)) for game in games for f in game.files)
        # Remove duplicates
        counter = Counter(t[1] for t in targets)
        duplicates = set(t for t in targets if counter[t[1]] != 1)
        targets -= duplicates

        def maxwidth(_targets):
            return max(len(str(t[0])) for t in _targets)

        width = maxwidth(targets)
        for src, dst in sorted(targets, key=lambda x: x[0]):
            print(f'{str(src).ljust(width)} -> {dst}')
            src.rename(dst)

        if duplicates:
            print('\nCowardly refusing to rename files where duplicates would be overwritten:')
            width = maxwidth(duplicates)
            for src, dst in sorted(duplicates, key=lambda x: x[1]):
                print(f'\t{str(src).ljust(width)} -> {dst}')

        return len(targets)
