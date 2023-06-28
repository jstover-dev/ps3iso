from pytest import main
from pathlib import Path

from .test_sfo_file import TestSfo


tmp_files = (
    Path(TestSfo.OUTFILE),
    Path('NewTitle.SFO'),
)

pytest_args = [
    '--color=yes',
    '--doctest-modules',
    '--doctest-glob=README.*',
]


def cleanup():
    for path in tmp_files:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    returncode = main(pytest_args)
    cleanup()
    exit(returncode)
