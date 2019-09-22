# PS3ISO

Command line tool and Python library for managing existing Playstation 3 image files

[![builds.sr.ht status](https://builds.sr.ht/~jmstover/ps3iso.svg)](https://builds.sr.ht/~jmstover/ps3iso?)

[[PyPi](https://pypi.org/project/ps3iso/)]
[[sourcehut](https://git.sr.ht/~jmstover/ps3iso)]


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
                        Path to the PS3 ISO file or directory containing PS3
                        ISO files
  -f FORMAT, --format FORMAT
                        Format string to use for output or --rename target
  --rename              Rename .iso and supporting files to a format string
                        based on PS3 metadata
```

## Quick Library Examples

```python
from ps3iso.game import Game

games = Game.search('/path/to/iso/files')
Game.rename_all(list(games), '%I-[%T]')
```

```python
from ps3iso.game import Game

for game in Game.search('.'):
	game.print_info('{"file":"%F", "title":"%T", "ID":"%I"}')
```

```python
from ps3iso.game import Game

games = Game.search('/path/to/iso/files')
for game in games:
	for f in game.files:
		print("Old name = %s" % f)
		print("New name = %s" % game.format_file(f, '%T [%I]'))
```


```python
from ps3iso.sfo import SfoFile

with open('/path/to/PARAM.SFO', 'rb') as f:
	sfo = SfoFile.parse(f)

for key, value in sfo:
	print("key=%s, value=%r" % (key, value))
```

```python
from ps3iso.sfo import SfoFile

sfo = SfoFile.parse_file('/path/to/PARAM.SFO')
print("Game ID = %s" % sfo.TITLE_ID)
print(sfo.format("Game Title = %T\n"))
```

