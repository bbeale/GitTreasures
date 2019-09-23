#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.gitlab_log import GitLabLog
from util import is_db_init, gitlab_db_setup

import configparser
import sqlite3
import sys
import os

usage = "Run this file in the root directory:" \
        "python init.py"

config = configparser.ConfigParser()
try:
    config.read(os.path.relpath("config.ini"))
except configparser.Error as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)

db_path = os.path.join(
    'data', 'git_treasures.db'
)

if is_db_init(db_path):
    print("Database is already initialized. If you want to reinitialize the commit database, then delete or rename the current database file (data/<filename>.db), then rerun init.py. Else, run git_treasures.py.")
    sys.exit(-1)


def main():
    # get GitLab config values
    try:
        gitlab_config = dict(
            repo_path           = config["gitlab"]["repo_path"],
            token               = config["gitlab"]["token"],
            project_id          = config["gitlab"]["project_id"],
            staging_branch_name = config["git"]["staging_branch_name"],
            jira_pattern        = config["git"]["jira_pattern"],
            db_path             = db_path
        )

    except configparser.Error:
        print("Failed to get GitLab settings from config file")
        sys.exit(-1)

    gitlab_db_setup(gitlab_config["db_path"])
    gl = GitLabLog(gitlab_config)

    try:
        gl.populate()
        print("Initialization complete")
    except sqlite3.Error as sqle:
        print(sqle, "Initialization failed")


if __name__ == '__main__':
    main()
