#!/usr/bin/env python

from pathlib import Path
import json
import logging

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

    def _store_db(self):
        logger.debug("Saving data to {}".format(self.DB_FILE))
        with open(self.DB_FILE, "w+") as f:
            f.write(json.dumps(self.data))

    def shutdown(self):
        logger.debug("Shutting down database")
        self._store_db()

    def get(self, key):
        return self.data.get(key)

    def getKeys(self):
        return self.data.keys()

    def getAll(self):
        return self.data.items()

    def set(self, key, value):
        self.data[key] = value

    def exists(self, key):
        return key in self.data

    def remove(self, key):
        return self.data.pop(key, None)
