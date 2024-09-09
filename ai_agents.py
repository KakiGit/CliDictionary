#!/usr/bin/env python

from utils import Singleton
from openai import OpenAI
import json
from databases import InMemoryDatabase
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SYSTEM_MSG = """
# Objective
You can only do 3 kinds of operations to the dictionary: add, remove and search. For add and remove operations, you'll be able to do a list of operations. For search, you can do both exact search and fuzzy search.
# Style
In json format.
# Audience
An application that only receives json input.
# Response
[{"operation": "", "word": "WORD1", meaning: "MEANING1"}, {"operation": "", "word": "WORD2", meaning: "MEANING2 "}, ]
# Context
You are maintaining a dictionary for the user. You know the meaning of all the words in all human languages. You know the translation between any two languages.
current dictionary contents:
"""


class ChatGPT(metaclass=Singleton):

    def __init__(self, idFile=None, apiKeyFile=None):
        self.orgId = None
        self.projId = None
        self.apiKey = None
        if idFile:
            if not Path(idFile).exists():
                logger.error("{} not found.".format(idFile))
                logger.error('It shoud contain content {"projectId":"$project_id", "organizationId": "$organizationId"}')
                raise
            with open(idFile, "r") as f:
                data = json.loads(f.read())
                self.orgId = data["organizationId"]
                self.projId = data["projectId"]
                logger.debug("orgId {}. projId {}.".format(self.orgId, self.projId))
        if apiKeyFile:
            if not Path(apiKeyFile).exists():
                logger.error("{} not found.".format(idFile))
                logger.error('It shoud contain the api_key as plain text in a single line')
                raise
            with open(apiKeyFile, "r") as f:
                self.apiKey = f.read().strip()
                logger.debug("apiKey {}...{}.".format(self.apiKey[:10], self.apiKey[len(self.apiKey)-10:]))

        self.client = OpenAI(
                  organization=self.orgId,
                  project=self.projId,
                  api_key=self.apiKey,
                )
        self.db = InMemoryDatabase()

    def ask(self, msg):
        response = self.client.chat.completions.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_MSG + "{}".format(self.db.getAll()),
                },
                {
                    "role": "user",
                    "content": msg,
                }
                ],
            model="gpt-4o-mini",
        )
        logger.debug(response.headers.get('x-request-id'))

        # get the object that `chat.completions.create()` would have returned
        completion = response.parse()
        logger.debug("{}".format(completion))
        return json.loads(completion.choices[0].message.content)

    def add(self, word, meaning):
        self.db.set(word.lower(), meaning)

    def remove(self, word, meaning):
        self.db.remove(word)

    def search(self, word, meaning):
        res = self.db.get(word)
        print(word, ":", res)

    def parse(self, operations):
        OPS = {
                "add": self.add,
                "remove": self.remove,
                "search": self.search,
                }
        for operation in operations:
            word = operation.get("word")
            meaning = operation.get("meaning", None)
            OPS[operation["operation"]](word, meaning)
