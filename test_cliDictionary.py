#!/usr/bin/env python

import unittest
import cliDictionary
from unittest.mock import patch
from io import StringIO
import sys
import json
from pathlib import Path
import atexit
import os
from databases import InMemoryDatabase


TEST_DB_PATH = "test.db"

db = InMemoryDatabase(TEST_DB_PATH)


class TestCliDictionary(unittest.TestCase):

    def test_0101_add_word(self):
        stdin = sys.stdin
        sys.stdin = open('simulatedInput_add_word.txt', 'r')
        # cliDictionary.input = lambda _: 'testword'
        cliDictionary.AddWord().execute()
        self.assertEqual(db.get("testword"), 'testmeaning')
        sys.stdin.close()
        sys.stdin = stdin

    def test_0201_list_words(self):
        with patch('sys.stdout', new_callable=StringIO) as fake_out:
            cliDictionary.ListWords().execute()
            self.assertEqual(fake_out.getvalue().strip(), "testword : testmeaning")
            fake_out.truncate(0)
            fake_out.seek(0)

    def test_0301_add_existing(self):
        stdin = sys.stdin
        sys.stdin = open('simulatedInput_add_existing_word.txt', 'r')
        cliDictionary.AddWord().execute()
        self.assertEqual(db.get("testword"), 'testmeaning1')
        sys.stdin.close()
        sys.stdin = stdin

    def test_0302_dont_add_existing(self):
        stdin = sys.stdin
        sys.stdin = open('simulatedInput_dont_add_existing_word.txt', 'r')
        cliDictionary.AddWord().execute()
        self.assertEqual(db.get("testword"), 'testmeaning1')
        sys.stdin.close()
        sys.stdin = stdin

    def test_0401_remove_word(self):
        stdin = sys.stdin
        sys.stdin = open('simulatedInput_remove_word.txt', 'r')
        # cliDictionary.input = lambda _: 'testword'
        cliDictionary.RemoveWord().execute()
        exists = db.exists("testword")
        self.assertEqual(exists, False)
        sys.stdin.close()
        sys.stdin = stdin

    def test_0501_store_db(self):
        self.test_0101_add_word()
        db._store_db()

        def cleanup_db_file():
            os.remove(TEST_DB_PATH)
        atexit.register(cleanup_db_file)
        self.assertEqual(Path(TEST_DB_PATH).exists(), True)

    def test_0601_load_db(self):
        data = None
        if Path(TEST_DB_PATH).exists():
            with open(TEST_DB_PATH, "r") as f:
                data = json.loads(f.read())
        self.assertEqual(data, {"testword": "testmeaning"})


if __name__ == '__main__':
    unittest.main()
