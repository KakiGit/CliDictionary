# CLI Dictionary

An AI capable CLI tool for keeping a personal dictionary.

# Install Dependencies

```bash
pip install -r requirements.txt
```

# Usage

```bash
usage: cliDictionary.py [-h] [-d DB_FILE] [--ai-mode] [-a AI_IDS_FILE] [-k AI_KEY_FILE]
                        [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

A CLI based personal dictionary.

options:
  -h, --help            show this help message and exit
  -d DB_FILE, --db-file DB_FILE
                        Path to the DB file. Default to ${CLIDICTIONARY_DIR}/cli.db
  --ai-mode             Enable AI assitant.
  -a AI_IDS_FILE, --ai-ids-file AI_IDS_FILE
                        Path to the AI API IDs. Default to ${CLIDICTIONARY_DIR}/openai.json
  -k AI_KEY_FILE, --ai-key-file AI_KEY_FILE
                        Path to the AI API key. Default to ${CLIDICTIONARY_DIR}/api_key
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
 Word              Meaning
 ---------------   ----------
 päivä             day
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

## AI Mode

AI Mode is based on OpenAI

```
>>> ai
(What would you like to ask from the AI?)
```

AI Mode is only available when specifying "--ai-mode" when running the cliDictionary.py

By default, AI Mode reads config from openai.json and api\_key

### Example content of openai.json

```json
{"projectId":"$project_id", "organizationId": "$organizationId"}
```

### Example content of api\_key

```
$api_key
```


# Dependencies

* openai

# License
[LICENSE](LICENSE)
