#!/usr/bin/env python

from databases import InMemoryDatabase
import logging
import sys
from ai_agents import ChatGPT

logger = logging.getLogger(__name__)


class CliAction:

    def __init__(self):
        self.db = InMemoryDatabase()

    def execute(self):
        raise "execute not Implemented"

    def print(self, text):
        print("({}) ".format(text))

    def _inputFreeStyle(self, text, allow_empty=True):
        if allow_empty:
            return input("({}) ".format(text))
        while True:
            userInput = input("({}) ".format(text))
            if userInput:
                return userInput
            print("(Input cannot be empty)")


    def _inputWithChoise(self, text, choices=None):
        while True:
            userInput = input("({}) ".format(text))
            if userInput in choices:
                return userInput


class ListWords(CliAction):

    def execute(self):
        data = self.db.getAll()
        if len(data) == 0:
            self.print("No data in dictoinary")
            return
        maxKeyLength = max([len(key) for key, _ in data])
        tableFormat = " {:<" + str(maxKeyLength) + "}   {}"
        print(tableFormat.format("Word", "Meaning"))
        print(tableFormat.format("-"*maxKeyLength, "-"*10))
        for key, value in sorted(data):
            print(tableFormat.format(key, value))


class AddWord(CliAction):

    def execute(self):
        override = "y"
        word = self._inputFreeStyle("Input word to add").lower()
        if self.db.exists(word):
            self.print("{} already exists in the dictionary.".format(word))
            self.print(" Current meaning: {}".format(self.db.get(word)))
            override = self._inputWithChoise(
                    "Replace it with new meaning? y/N",
                    ["y", "Y", "n", "N"])
        if override == "y" or override == "Y":
            meaning = self._inputFreeStyle("Input meaning", allow_empty=False)
            self.db.set(word, meaning)


class RemoveWord(CliAction):

    def execute(self):
        confirm = "N"
        word = self._inputFreeStyle("Input word to delete")
        confirm = self._inputWithChoise(
                "confirm: delete {}? y/N".format(word),
                ["y", "Y", "n", "N"])
        if confirm == "y" or confirm == "Y":
            self.db.remove(word)


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
        for key in self.db.getKeys():
            words.append((key, self.levenshtein_distance(word, key)))
        words = sorted(words, key=lambda x: x[1])
        logger.debug("{}".format(words))
        return [x[0] for x in words[:limit]]

    def execute(self):
        word = self._inputFreeStyle("Input word to search").lower()
        if self.db.exists(word):
            self.print("found with meaning: {}".format(self.db.data[word]))
            return
        else:
            self.print(f"{word} not found. Looking for similar ones.")

        words = self.findSimilarWords(word)
        if len(words) == 0:
            self.print("not found")
            return
        self.print("Find these possible results")
        for w in words:
            print(w, ":", self.db.get(w))


class QuitProgram(CliAction):

    def execute(self):
        self.print("Exiting...")
        sys.exit(0)


class AIMode(CliAction):

    def __init__(self):
        self.aiAgent = ChatGPT()

    def execute(self):
        question = self._inputFreeStyle("What would you like to ask from the AI?")
        answer = self.aiAgent.ask(question)
        self.aiAgent.parse(answer)
