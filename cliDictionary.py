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
        SearchWord, QuitProgram, AIMode, logger as action_loger
        )
from ai_agents import ChatGPT, logger as ai_logger

logger = logging.getLogger(__name__)


DEFAULT_DB_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "cli.db",
        )

DEFAULT_AIIDS_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "openai.json",
        )

DEFAULT_AIKEY_PATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "api_key",
        )


def parse_args():
    parser = argparse.ArgumentParser(
            prog=os.path.basename(__file__),
            description="A CLI based personal dictionary.")
    parser.add_argument("-d", "--db-file",
                        default=DEFAULT_DB_PATH,
                        help=f"Path to the DB file. Default to {DEFAULT_DB_PATH}")
    parser.add_argument('--ai-mode', action='store_true',
                        help="Enable AI assitant.")
    parser.add_argument("-a", "--ai-ids-file",
                        default=DEFAULT_AIIDS_PATH,
                        help=f"Path to the AI API IDs. Default to {DEFAULT_AIIDS_PATH}")
    parser.add_argument("-k", "--ai-key-file",
                        default=DEFAULT_AIKEY_PATH,
                        help=f"Path to the AI API key. Default to {DEFAULT_AIKEY_PATH}")
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
        ACTIONS[s]().execute()
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
    ai_logger.setLevel(level=getattr(logging, log_level))


ACTIONS = {
        "l": ListWords,
        "a": AddWord,
        "s": SearchWord,
        "r": RemoveWord,
        "q": QuitProgram,
}

if __name__ == "__main__":
    args = parse_args()
    logger.debug("starting with args {}".format(args))
    setup_logging(args.log_level)
    InMemoryDatabase(args.db_file)
    if args.ai_mode:
        ChatGPT(args.ai_ids_file, args.ai_key_file)
        ACTIONS["ai"] = AIMode
    atexit.register(InMemoryDatabase().shutdown)

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
