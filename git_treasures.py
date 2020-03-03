#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.testrail_reconciler import TestRailReconciler
from src.trello_reconciler import TrelloReconciler
from src.trello_board import TrelloBoard
from src.testrail import TestRail
from src.jira_board import JiraBoard
from src.gitlab_log import GitLabLog
from util import is_db_init
from argparse import ArgumentParser
import configparser
import inspect
import time
import sys
import os

usage = """Use this tool to update a Trello board with QA order/priorities based on data retrieved from Jira and git.
    python git_treasures.py --url <repository url> | --path <repository path>
"""

# database path shouldn't change
db_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
    "git_treasures.db"
)

if not is_db_init(db_path):
    print("Database is not initialized. Run init.py in this directory to initialize the commit database, then re-run GitTreasures.")
    sys.exit(-1)

config = configparser.ConfigParser()

try:
    config.read(os.path.relpath("config.ini"))
except OSError as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)

_name = inspect.stack()[0][3]

try:
    # Trello config values
    trello_config = dict(
        key                 = config["trello"]["key"],
        token               = config["trello"]["token"],
        board_id            = config["trello"]["board_id"],
        test_board_id       = config["trello"]["test_board_id"],
        archive_board_id    = config["trello"]["archive_board_id"],
    )

    # Jira config values
    jira_config = dict(
        f_name              = _name,
        url                 = config["jira"]["url"],
        username            = config["jira"]["username"],
        token               = config["jira"]["token"],
        project_key         = config["jira"]["project_key"]
    )

    # git config values
    git_config = dict(
        repo_path           = config["git"]["repo_path"],
        staging_branch_name = config["git"]["staging_branch_name"],
        jira_pattern        = config["git"]["jira_pattern"],
        db_path             = db_path
    )

    # GitLab config values
    gitlab_config = dict(
        repo_path           = config["gitlab"]["repo_path"],
        token               = config["gitlab"]["token"],
        project_id          = config["gitlab"]["project_id"],
        staging_branch_name = config["git"]["staging_branch_name"],
        jira_pattern        = config["git"]["jira_pattern"],
        db_path             = db_path
    )

    # Trello reconciler config values
    tr_config = dict(
        filter_qa_status    = config["jira"]["filter_qa_status"],
        filter_qa_ready     = config["jira"]["filter_qa_ready"],
        project_key         = config["jira"]["project_key"],
        jira_pattern        = r"{}".format(config["git"]["jira_pattern"]),
        testcase_url        = config["testrail"]["testcase_url"]
    )

    # TestRail config values
    testrail_config = dict(
        url                 = config["testrail"]["url"],
        user                = config["testrail"]["user"],
        password            = config["testrail"]["password"],
    )

    # TestRail reconciler config values
    trr_config = dict(
        project_key         = config["jira"]["project_key"],
        filter_last_week    = config["jira"]["filter_last_week"],
        filter_this_release = config["jira"]["filter_this_release"],
    )

except (configparser.Error, KeyError) as error:
    raise error("[!] Failed to set config values from config file.")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-d", "--dev",
        action="store_true",
        required=False,
        help="Run the development version of the script")
    parser.add_argument(
        "-tr", "--testrail",
        action="store_true",
        required=False,
        help="If true, will reconcile TestRail after Trello is complete.")
    return parser.parse_args()


def main():
    """The main entry point into the application.

    The script called by Jenkins, the script called by the Flask front end.

    Other "versions" that were previously separate files can be called by specifying the command line argument for the thing that the old file used to do
    """
    print("[+] Starting GitTreasures")
    args = parse_args()

    start = time.time()

    # initialize all my interface and reconciler classes
    if args.dev:
        trello = TrelloBoard(trello_config, testMode=True)
    else:
        trello = TrelloBoard(trello_config)

    jira = JiraBoard(jira_config)
    git = GitLabLog(gitlab_config)

    # stage 2 init process (really big fan of these it seems)
    trello.populate()
    git.populate()

    # run the TestRail reconcile process if true
    if args.testrail:
        testrail = TestRail(testrail_config)
        testrail_reconciler = TestRailReconciler(testrail, jira, trr_config)
        testrail_reconciler.populate_release()

    # initialize the Trello reconciler
    trello_reconciler = TrelloReconciler(jira, git, trello, tr_config)
    trello_reconciler.reconcile()

    end = time.time()
    duration = int(end) - int(start)
    print("[+] duration: {}s".format(str(duration)))


if __name__ == "__main__":
    main()
