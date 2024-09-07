# CLI Dictionary

A CLI tool for keeping a personal dictionary.

# Usage

```bash
$ ./cliDictionary.py -h
usage: cliDictionary.py [-h] [-d DB_FILE] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

A CLI based personal dictionary.

options:
  -h, --help            show this help message and exit
  -d DB_FILE, --db-file DB_FILE
                        Path to the dictionary DB. Default to
                        ${CLIDICTIONARY_DIR}/cli.db
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level
```

This will open an interactive shell.

## Add a word
```
>>> a
(Input word to add) Päivä
(Input meaning) day
```

## Search a word
```
>>> s
(Input word to search) Päivä
(found with meaning) day
```

## List words
```
>>> l
päivä : day
```

## Remove a word
```
>>> r
(Input word to delete) päivä
(confirm: delete päivä? y/N) y
```

## Quit the Shell
```
>>> q
```

# Dependencies

# License
[LICENSE](LICENSE)
