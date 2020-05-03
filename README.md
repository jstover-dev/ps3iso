# PS3ISO

Command line tool and Python library for managing existing Playstation 3 and
Playstation Portable image files

[![PyPI version](https://badge.fury.io/py/ps3iso.svg)](https://pypi.org/project/ps3iso)
[![builds.sr.ht status](https://builds.sr.ht/~jmstover/ps3iso.svg)](https://builds.sr.ht/~jmstover/ps3iso?)
[![Documentation Status](https://readthedocs.org/projects/ps3iso/badge/?version=latest)](https://ps3iso.readthedocs.io/en/latest/?badge=latest)
[![Coverage](https://artifact.jstover.dev/ps3iso/badges/coverage.svg)](https://artifact.jstover.dev/ps3iso/htmlcov/)
[![PyPI - License](https://img.shields.io/pypi/l/ps3iso)](https://git.sr.ht/~jmstover/ps3iso/blob/master/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ps3iso)]()


## Installing

```
pip install ps3iso
```


## Dependencies


### isoinfo

`isoinfo` needs to be in the system PATH in order to extract SFO data directly from .iso images

 Windows: `https://smithii.com/files/cdrtools-latest.zip`
 
 macOS: `brew install cdrtools`
 
 Linux: `brew install genisoimage`



## Quick Program Help
```
usage: [-h] -i INPUT [-f FORMAT] [--rename]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
						Path to the ISO file or directory containing ISO files
  -f FORMAT, --format FORMAT
                        Format string to use for output or --rename target
  --rename              Rename .iso and supporting files to a format string
                        based on SFO metadata
```

To rename all ISO files, plus all files with a matching name to a nice format:

```sh
$ ps3iso -i /path/to/isos -f '%I-[%T]' --rename
```
This will rename `.iso` files by reading the game's metadata. It will also find any files with the same name, but different extension. The file name will be based on the format string given by `-f` and the following variables are expanded:

| Variable | Parameter       |
|:--------:|-----------------|
| __%a__   | APP_VER         |
| __%a__   | ATTRIBUTE       |
| __%C__   | CATEGORY        |
| __%L__   | LICENSE         |
| __%P__   | PARENTAL_LEVEL  |
| __%R__   | RESOLUTION      |
| __%S__   | SOUND_FORMAT    |
| __%T__   | TITLE           |
| __%I__   | TITLE_ID        |
| __%V__   | VERSION         |
| __%v__   | PS3_SYSTEM_VER  |

Therefore, the above command will look in `/path/to/isos` for all ISO files (_e.g._ `UnknownGame.iso`) and rename it according to `%I-[%T]` (e.g. `BLES0000-[Game Title].iso`)

Additionally, all matching extra files (_e.g._ `UnknownGame.png`) will be renamed (_e.g._ `BLES0000-[Game Title].png`)

When __not__ renaming files, the `--format` argument will also expand additional variables:

| Variable | Parameter         |
|:--------:|-------------------|
| __%f__   | File name         |
| __%p__   | File full path    |
| __\n__   | Newline character |
| __\t__   | Tab character     |

The following will output a JSON object for each file found:

```sh 
ps3iso -i /path/to/isos -f '{\n\t"file": "%F",\n\t"title": "%T",\n\t"ID": "%I"\n}'
```

```json
{
        "file": "/path/to/isos/UnknownGame.iso",
        "title": "Game Title",
        "ID": "BLES00000"
}
```


## Quick Library Examples

Renaming all ISO's in `/path/to/iso/files` to `BLES0000-[Game Title].iso` format:

```python
from ps3iso.game import Game

games = Game.search('/path/to/iso/files')
Game.rename_all(list(games), '%I-[%T]')
```


Print a JSON object per game containing file path, game title, and game id:

```python
from ps3iso.game import Game

for game in Game.search('.'):
	game.print_info('{"file":"%p", "title":"%T", "ID":"%I"}')
```


Loop over all ISO files and matching associated files, and generate a new filename in `Game Title [BLES0000].ext` format

```python
from ps3iso.game import Game

games = Game.search('/path/to/iso/files')
for game in games:
	for f in game.files:
		print("Old name = %s" % f)
		print("New name = %s" % game.format_file(f, '%T [%I]'))
```


Open an existing PARAM.SFO file and print all valid SFO attributes

```pycon
>>> from ps3iso.sfo import SfoFile
>>> with open('test/data/PARAM.SFO', 'rb') as f:
...	   sfo = SfoFile.parse(f)
>>> for key, value in sfo:
...     print("%s=%r" % (key, value))
APP_VER='01.00'
ATTRIBUTE=32
BOOTABLE=1
CATEGORY='DG'
LICENSE='Some example license text, Supports UTF8 glyphs like ©and ®.'
PARENTAL_LEVEL=5
PS3_SYSTEM_VER='02.5200'
RESOLUTION=63
SOUND_FORMAT=1
TITLE='Example PS3ISO Game Title'
TITLE_ID='BLES00000'
VERSION='01.00'

```

Read a specific attribute (`TITLE_ID`) from an existing PARAM.SFO

```pycon
>>> from ps3iso.sfo import SfoFile
>>> sfo = SfoFile.parse_file('test/data/PARAM.SFO')
>>> print("Game ID = %s" % sfo.parameters.TITLE_ID)
Game ID = BLES00000
>>> print(sfo.format("Game Title = %T"))
Game Title = Example PS3ISO Game Title

```


## Development - New release

1. Make sure the tests pass and docs build: `make coverage; make doc`
1. Update the version number in setup.py
1. Create a tag for the version e.g.: `git tag v1.2.3`
1. Build and upload to PyPi: `make upload`

