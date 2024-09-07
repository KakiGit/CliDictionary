#!/usr/bin/env python

from pathlib import Path
import argparse
import atexit
import json
import logging
import os
import sys
import readline

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class InMemoryDatabase(metaclass=Singleton):

    def __init__(self, db_path=None):
        if db_path:
            self.DB_FILE = Path(db_path)
        logger.debug("DB_FILE {}".format(self.DB_FILE))
        self.data = {}
        self._load_db()

    # def __del__(self):
        # self.store_db()
        # Interpreter shutdown will delete global variables
        # or functions like open()
        # Use atexit instead

    def _load_db(self):
        logger.debug("loading data from {}".format(self.DB_FILE))
        if not self.DB_FILE.exists():
            return
        with open(self.DB_FILE) as f:
            self.data.update(json.loads(f.read()))

    def store_db(self):
        logger.debug("Saving data to {}".format(self.DB_FILE))
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

    def __init__(self):
        super().__init__()
        self.THRESHOLD = 3

    @staticmethod
    def levenshtein_distance(s1, s2):
        # Create a matrix to store distances
        distances = [[0 for _ in range(len(s2) + 1)] for _ in range(len(s1) + 1)]

        # Initialize distances for the base cases
        for i in range(len(s1) + 1):
            distances[i][0] = i
        for j in range(len(s2) + 1):
            distances[0][j] = j

        # Calculate distances
        for i in range(1, len(s1) + 1):
            for j in range(1, len(s2) + 1):
                if s1[i - 1] == s2[j - 1]:
                    cost = 0
                else:
                    cost = 1
                distances[i][j] = min(distances[i - 1][j] + 1,     # Deletion
                                      distances[i][j - 1] + 1,     # Insertion
                                      distances[i - 1][j - 1] + cost)  # Substitution

        # The final distance is in the bottom-right corner of the matrix
        return distances[-1][-1]

    def findSimilarWords(self, word, limit=3):
        words = []
        for key in self.db.data.keys():
            words.append((key, self.levenshtein_distance(word, key)))
        words = sorted(words, key=lambda x: x[1])
        logger.debug("{}".format(words))
        return [x[0] for x in words[:limit]]

    def execute(self):
        word = self._inputFreeStyle("Input word to search").lower()
        if word in self.db.data:
            self.print("found with meaning: {}".format(self.db.data[word]))
        else:
            self.print(f"{word} not found. Looking for similar ones.")
            words = self.findSimilarWords(word)
            if len(words) == 0:
                self.print("not found")
                return
            self.print("Find these possible results")
            for w in words:
                print(w, ":", self.db.data[w])


class QuitProgram(CliAction):

    def execute(self):
        self.print("Exiting...")
        sys.exit(0)


DEFAULT_DB_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "cli.db",
        )


def parse_args():
    parser = argparse.ArgumentParser(
            prog=os.path.basename(__file__),
            description="A CLI based personal dictionary.")
    parser.add_argument("-d", "--db-file",
                        default=DEFAULT_DB_PATH,
                        help=f"Path to the dictionary DB. Default to {DEFAULT_DB_PATH}")
    parser.add_argument("-l", "--log-level",
                        default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    return parser.parse_args()


def print_usage():
    print("These are the supported commands:")
    print("l   list words in the dictionary")
    print("a   add a word to the dictionary")
    print("s   search a word in the dictionary")
    print("r   remove a word from the dictionary")
    print("q   quit")


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        )
    logger.setLevel(level=getattr(logging, args.log_level))
    logger.debug("starting with args {}".format(args))
    InMemoryDatabase(args.db_file)
    atexit.register(InMemoryDatabase().store_db)
    ACTIONS = {
            "l": ListWords(),
            "a": AddWord(),
            "s": SearchWord(),
            "r": RemoveWord(),
            "q": QuitProgram(),
    }

    while True:
        try:
            s = input(">>> ")
            if s in ACTIONS:
                ACTIONS[s].execute()
            elif s == "":
                pass
            else:
                print_usage()
        except KeyboardInterrupt:
            print("")
        except EOFError:
            print("")
            sys.exit(0)
        except Exception:
            logger.exception("")
