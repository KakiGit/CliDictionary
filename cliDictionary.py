#!/usr/bin/env python

from pathlib import Path
import atexit
import json
import logging
import sys


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class InMemoryDatabase(metaclass=Singleton):

    DB_FILE = Path("cli.db")

    def __init__(self):
        self.data = {}
        self._load_db()

    # def __del__(self):
        # self.store_db()
        # Interpreter shutdown will delete global variables
        # or functions like open()
        # Use atexit instead

    def _load_db(self):
        if not self.DB_FILE.exists():
            return
        with open(self.DB_FILE) as f:
            self.data.update(json.loads(f.read()))

    def store_db(self):
        logging.info("Saving Database")
        with open(self.DB_FILE, "w+") as f:
            f.write(json.dumps(self.data))


class CliAction:

    def __init__(self):
        self.db = InMemoryDatabase()

    def execute(self):
        raise "execute not Implemented"

    def print(self, text):
        print("({}) ".format(text))

    def _inputFreeStyle(self, text):
        return input("({}) ".format(text))

    def _inputWithChoise(self, text, choices=None):
        try:
            while True:
                userInput = input("({}) ".format(text))
                if userInput in choices:
                    return userInput
        except Exception:
            print("Navigating to main menu...")


class ListWords(CliAction):

    def execute(self):
        for key, value in sorted(self.db.data.items()):
            print(key, ":", value)


class AddWord(CliAction):

    def execute(self):
        override = "y"
        word = self._inputFreeStyle("Input word to add").lower()
        if word in self.db.data:
            self.print("{} already exists in the dictionary.".format(word))
            self.print(" Current meaning: {}".format(self.db.data[word]))
            override = self._inputWithChoise(
                    "Replace it with new meaning? y/N",
                    ["y", "Y", "n", "N"])
        if override == "y" or override == "Y":
            meaning = self._inputFreeStyle("Input meaning")
            self.db.data[word] = meaning


class RemoveWord(CliAction):

    def execute(self):
        confirm = "N"
        word = self._inputFreeStyle("Input word to delete")
        confirm = self._inputWithChoise(
                "confirm: delete {}? y/N".format(word),
                ["y", "Y", "n", "N"])
        if confirm == "y" or confirm == "Y":
            self.db.data.pop(word, None)


class SearchWord(CliAction):

    def execute(self):
        word = self._inputFreeStyle("Input word to search").lower()
        if word in self.db.data:
            self.print("found with meaning: {}".format(self.db.data[word]))
        else:
            self.print("not found")


class QuitProgram(CliAction):

    def execute(self):
        self.print("Exiting...")
        sys.exit(0)


ACTIONS = {
        "l": ListWords(),
        "a": AddWord(),
        "s": SearchWord(),
        "r": RemoveWord(),
        "q": QuitProgram(),
}


atexit.register(InMemoryDatabase().store_db)


if __name__ == "__main__":
    try:
        while True:
            s = input(">>> ")
            if s in ACTIONS:
                ACTIONS[s].execute()
            else:
                print("Error: only support l,a,s,r,q")
    except Exception:
        logging.exception("")
