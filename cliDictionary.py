#!/usr/bin/env python

import argparse
import atexit
import logging
import os
import sys
import readline
from databases import InMemoryDatabase, logger as db_logger
from actions import (
        ListWords, AddWord, RemoveWord,
        SearchWord, QuitProgram, logger as action_loger
        )

logger = logging.getLogger(__name__)


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


def main_menu():
    s = input(">>> ")
    if s in ACTIONS:
        ACTIONS[s].execute()
    elif s == "":
        pass
    else:
        print_usage()


def setup_logging(log_level):
    logging.basicConfig(stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        )
    logger.setLevel(level=getattr(logging, log_level))
    action_loger.setLevel(level=getattr(logging, log_level))
    db_logger.setLevel(level=getattr(logging, log_level))


if __name__ == "__main__":
    args = parse_args()
    logger.debug("starting with args {}".format(args))
    setup_logging(args.log_level)
    InMemoryDatabase(args.db_file)
    atexit.register(InMemoryDatabase().shutdown)
    ACTIONS = {
            "l": ListWords(),
            "a": AddWord(),
            "s": SearchWord(),
            "r": RemoveWord(),
            "q": QuitProgram(),
    }

    while True:
        try:
            main_menu()
        except KeyboardInterrupt:
            print("")
        except EOFError:
            print("")
            sys.exit(0)
        except Exception:
            logger.exception("")
