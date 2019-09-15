import io
import re
import glob
import subprocess
from pathlib import Path
from collections import Counter

from .sfo import SfoFile


class Game(object):

    def __init__(self, iso_path):
        self.iso = Path(iso_path).resolve()
        self.files = set(self.iso.parent.glob(glob.escape(self.iso.stem) + '.*'))
        self.sfo = self.extract_sfo(self.iso)

    def format_file(self, f, fmt, fill=''):
        name = self.sfo.format(fmt)
        name = re.sub(r'[\\/*?:<>"|%]', fill, name)
        return (f.parent / name).with_suffix(f.suffix.lower())

    def print_info(self, fmt=None):
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
    def extract_sfo(cls, iso_path):
        cmd = ['isoinfo', '-i', str(iso_path), '-x', '/PS3_GAME/PARAM.SFO;1']
        proc = subprocess.run(cmd, capture_output=True)
        proc.check_returncode()
        with io.BytesIO(proc.stdout) as f:
            sfo = SfoFile.parse(f)
        return sfo

    @classmethod
    def search(cls, path):
        path = Path(path)
        if path.resolve().is_dir():
            for fpath in path.glob(r'*.[Ii][Ss][Oo]'):
                yield cls(fpath)
        else:
            yield cls(path)

    @staticmethod
    def rename_all(games, fmt):
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
            print('\nCowardly refusing to rename files which result in duplicates being overwritten:')
            width = maxwidth(duplicates)
            for src, dst in sorted(duplicates, key=lambda x: x[1]):
                print(f'\t{str(src).ljust(width)} -> {dst}')

