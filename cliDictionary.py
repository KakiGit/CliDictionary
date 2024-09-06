#!/usr/bin/env python

import json
import sys
from pathlib import Path
import logging


imdb = {}

DB_FILE = Path("cli.db")


def load_db():
    if not DB_FILE.exists():
        return
    with open(DB_FILE) as f:
        imdb.update(json.loads(f.read()))


def store_db():
    with open(DB_FILE, "w+") as f:
        f.write(json.dumps(imdb))


def list_words():
    for key, value in sorted(imdb.items()):
        print(key, ":", value)


def add_word():
    override = "y"
    word = input("(Input word to add) ").lower()
    if word in imdb:
        override = input(
                "({} already exists in the dictionary.".format(word) +
                " Current meaning: {}\n".format(imdb[word]) +
                "Replace it with new meaning? y/N) ")
    if override == "y" or override == "Y":
        meaning = input("(Input meaning) ")
        imdb[word] = meaning


def search_word():
    word = input("(Input word to search) ").lower()
    if word in imdb:
        print("(found with meaning) {}".format(imdb[word]))
    else:
        print("(not found) ")


def remove_word():
    confirm = "N"
    word = input("(Input word to delete) ")
    confirm = input("(confirm: delete {}? y/N) ".format(word))
    if confirm == "y" or confirm == "Y":
        imdb.pop(word, None)


def quit_program():
    sys.exit(0)


ACTIONS = {
        "l": list_words,
        "a": add_word,
        "s": search_word,
        "r": remove_word,
        "q": quit_program,
}


if __name__ == "__main__":
    load_db()
    try:
        while True:
            s = input(">>> ")
            if s in ACTIONS:
                ACTIONS[s]()
            else:
                print("Error: only support l,a,s,r,q")
    except Exception:
        logging.exception("")
    finally:
        store_db()
