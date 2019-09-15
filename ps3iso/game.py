import io
import re
import subprocess
from pathlib import Path

from .sfo import SfoFile


class Game(object):
    def __init__(self, iso_path):
        self.iso = Path(iso_path).resolve()
        self.files = set(self.iso.parent.glob(self.iso.stem + '.*'))
        self.sfo = self.extract_sfo(self.iso)

    def format(self, f, fmt, fill=''):
        name = str(fmt
                    .replace('%C', self.sfo.CATEGORY.strip())
                    .replace('%P', str(self.sfo.PARENTAL_LEVEL).strip())
                    .replace('%p', self.sfo.PS3_SYSTEM_VER.strip())
                    .replace('%R', str(self.sfo.RESOLUTION).strip())
                    .replace('%S', str(self.sfo.SOUND_FORMAT).strip())
                    .replace('%T', self.sfo.TITLE.strip())
                    .replace('%I', self.sfo.TITLE_ID.strip())
                    .replace('%V', self.sfo.VERSION.strip()))

        name = re.sub(r'[\\/*?:<>"|%]', fill, name)
        return (f.parent / name).with_suffix(f.suffix.lower())

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
