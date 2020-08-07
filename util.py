#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import DbException
import configparser
import sqlite3
import json
import sys
import os


def get_configs(fields: list, config_path: str) -> dict:
    """parse a config.ini file for specific keys

    :param fields:
    :param config_path:
    :return res: a dict of values parsed from key-value pairs stored in the .ini file
    """
    if not config_path or config_path is None or not os.path.exists(config_path):
        raise FileNotFoundError("Invalid config file")

    config = configparser.ConfigParser()

    try:
        config.read(config_path)
    except configparser.Error as cpe:
        print(cpe, "Failed to parse config file")
        sys.exit(1)

    res = {}

    for field_name in fields:

        for membername in config.sections():
            for k, v in config.items(membername):

                if k == field_name and membername not in res.keys():
                    res[membername] = {}

                if k == field_name and k not in res[membername].keys():
                    res[membername][k] = v

    return res


def is_db_init(db_path: str) -> bool:
    """Get the count of all records in commits table.
    If count is 0, return false. If .db file does not exist, return false. Else, return true.

    :param db_path: path to the sqlite (.db) file
    :return: True if db is initialized, otherwise False
    """
    if not db_path or db_path is None:
        raise DbException("Database path required for this operation")

    if not os.path.exists(db_path):
        return False

    sql = "SELECT COUNT(*) FROM commits"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.close()
    except sqlite3.Error as sqle:
        print(sqle, "Database operation failed")
        sys.exit(-1)

    return True if result[0] > 0 else False


def git_db_setup(db_path: str) -> None:
    """Set up git database the old way."""
    if not db_path or db_path is None:
        raise DbException("Database path required for this operation")

    # Make sure we aren't running inside task_scripts
    if 'task_scripts' in os.path.join(__file__):
        print(__file__, "must not be in task_scripts/")
        sys.exit(-1)

    dbpath = os.path.join('data', 'git_treasures.db')

    # Let's start making databases!
    connection = sqlite3.connect(dbpath)
    cursor = connection.cursor()

    create_tables = "CREATE TABLE IF NOT EXISTS commits (commitID int, hash text, committerDate text, mainBranch text, otherBranches text, author_name text, author_email text, commitMessage text )"
    create_index = "CREATE UNIQUE INDEX IF NOT EXISTS commit_hash ON commits (hash)"
    get_tables = "SELECT name FROM sqlite_master WHERE type='table'"

    try:
        cursor.execute(create_tables)
        cursor.execute(create_index)
        cursor.execute(get_tables)
        connection.commit()
        # Should see "commits" table
        tables = cursor.fetchall()
        print(tables)
    except sqlite3.Error as sqle:
        print(sqle, "Database initialization failed")
        sys.exit(-1)


def gitlab_db_setup(db_path: str) -> None:
    """Set up git database the new way (with GitLabLog)."""
    if not db_path or db_path is None:
        raise DbException("Database path required for this operation")

    # create the database
    connection      = sqlite3.connect(db_path)
    cursor          = connection.cursor()

    create_tables   = "CREATE TABLE IF NOT EXISTS commits (commitID int, hash text, committerDate text, mainBranch text, author_name text, author_email text, commitMessage text )"
    create_index    = "CREATE UNIQUE INDEX IF NOT EXISTS commit_hash ON commits (hash)"
    get_tables      = "SELECT name FROM sqlite_master WHERE type='table'"

    try:
        cursor.execute(create_tables)
        cursor.execute(create_index)
        cursor.execute(get_tables)
        connection.commit()
        # Should see "commits" table
        tables = cursor.fetchall()
        print(tables)
        connection.close()
    except sqlite3.Error as sqle:
        print(sqle, "Database initialization failed")
        sys.exit(-1)


def main():
    tc = get_configs(["trello_id"], "users.ini")
    for t in tc.items():
        print(t)


    jc = get_configs(["jira_displayname"], "users.ini")
    for j in jc.items():
        print(j)

    trc = get_configs(["jira_displayname", "trello_id"], "users.ini")
    for tr in trc.items():
        print(tr)

    print('.')


if __name__ == "__main__":
    main()
