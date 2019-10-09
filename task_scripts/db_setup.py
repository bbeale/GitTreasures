#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.git_log import GitLog
from util import git_db_setup, is_db_init

import configparser
import sqlite3
import sys
import os

usage = "Move this file to root directory and run using:" \
        "python db_setup.py"

config = configparser.ConfigParser()
try:
    config.read(os.path.relpath("config.ini"))
except configparser.Error as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)

db_path = os.path.join(
    "data", "git_treasures.db"
)

if is_db_init(db_path):
    print("Database is already initialized. If you want to reinitialize the commit database, then delete or rename the current database file (data/<filename>.db), then rerun init.py. Else, run git_treasures.py.")
    sys.exit(-1)


def main():
    # get GitLab config values
    try:
        git_config = dict(
            repo_path           = config["git"]["repo_path"],
            staging_branch_name = config["git"]["staging_branch_name"],
            jira_pattern        = config["git"]["jira_pattern"],
            db_path             = db_path
        )

    except configparser.Error:
        print("Failed to get GitLab settings from config file")
        sys.exit(-1)

    git_db_setup(git_config["db_path"])
    gl = GitLog(git_config)

    try:
        gl.populate()
        print("Initialization complete")
    except sqlite3.Error as sqle:
        print(sqle, "Initialization failed")


if __name__ == "__main__":
    main()
