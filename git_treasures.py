#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.testrail_reconciler import TestRailReconciler
from src.trello_reconciler import TrelloReconciler
from src.trello_board import TrelloBoard
from src.testrail import TestRail
from src.jira_board import JiraBoard
from src.gitlab_log import GitLabLog
from src.git_log import GitLog
from util import is_db_init

from argparse import ArgumentParser, ArgumentError
import configparser
import inspect
import time
import sys
import os

usage = """Use this tool to update a Trello board with QA order/priorities based on data retrieved from Jira and git.
    python git_treasures.py --url <repository url> | --path <repository path>
"""

parser = ArgumentParser()

# use a different entrypoint based on CLI args
parser.add_argument("--dev", help="Run the development version of the script")
parser.add_argument("--testrail", help="Run the TestRail integration")
parser.add_argument("--testrail-dev", help="Run the test version of the TestRail integration")
parser.add_argument("--gitlab", help="Run the GitLab version of the script")
parser.add_argument("--gitlab-dev", help="Run the GitLab development version of the script")
parser.add_argument("--github", help="Run the GitHub version of the script")

# database path shouldn't change
db_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data',
    'git_treasures.db'
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
        project_key         = config["jira"]["project_key"],
        jira_pattern        = r'{}'.format(config["git"]["jira_pattern"]),
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
    print(".")

except KeyError as KE:
    print(KE, "Key does not exist")
    sys.exit(-1)

except configparser.Error as E:
    print(E, "Failed to get settings from config file")
    sys.exit(-1)



def main():
    """The main entry point into the application.

    The script called by Jenkins, the script called by the Flask front end.

    Other "versions" that were previously separate files can be called by specifying the command line argument for the thing that the old file used to do
    """
    print('Starting GitTreasures')

    start               = time.time()

    # initialize interfaces with Trello, Jira and Git
    trello              = TrelloBoard(trello_config)
    jira                = JiraBoard(jira_config)
    git                 = GitLog(git_config)

    # populate the GitLog object with relevant commits
    git.populate()

    TrelloReconciler(jira, git, trello, tr_config).reconcile()

    end                 = time.time()
    duration            = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


def dev():
    """The development/test entry point."""
    print('Starting GitTreasures in TEST MODE')

    start               = time.time()

    # initialize interfaces with Trello, Jira and Git
    trello              = TrelloBoard(trello_config, testMode=True)
    jira                = JiraBoard(jira_config)
    git                 = GitLog(git_config)

    # populate the GitLog object with relevant commits
    git.populate()

    TrelloReconciler(jira, git, trello, tr_config).reconcile()

    end                 = time.time()
    duration            = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


def testrail_main():
    """Main TestRail entry point."""
    print('Starting TestRail sync')

    start                   = time.time()
    testrail                = TestRail(testrail_config)
    jira                    = JiraBoard(jira_config)
    trello                  = TrelloBoard(trello_config)

    TestRailReconciler(testrail, jira, trello, trr_config).reconcile()

    end                     = time.time()
    duration                = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


def testrail_dev():
    """TestRail development/test entry point."""
    print('Starting TestRail sync in TEST MODE')

    start                   = time.time()
    testrail                = TestRail(testrail_config)
    jira                    = JiraBoard(jira_config)
    trello                  = TrelloBoard(trello_config, testMode=True)

    TestRailReconciler(testrail, jira, trello, trr_config).reconcile()

    end                     = time.time()
    duration                = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


def gitlab_main():
    """The development version of the GitLab entry point.
    This will replace the main version after the migration to GitLab.

    """
    print('Starting GitTreasures with GitLab')

    start               = time.time()

    # initialize interfaces with Trello, Jira and GitLab
    trello              = TrelloBoard(trello_config)
    jira                = JiraBoard(jira_config)
    git                 = GitLabLog(gitlab_config)

    # populate the GitLabLog object with relevant commits
    git.populate()

    TrelloReconciler(jira, git, trello, tr_config).reconcile()

    end                 = time.time()
    duration            = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


def gitlab_dev():
    """The development version of the GitLab entry point.
    This will replace the main version after the migration to GitLab.

    """
    print('Starting GitTreasures with GitLab in TEST MODE')

    start               = time.time()

    # initialize interfaces with Trello, Jira and GitLab
    trello              = TrelloBoard(trello_config, testMode=True)
    jira                = JiraBoard(jira_config)
    git                 = GitLabLog(gitlab_config)

    # populate the GitLabLog object with relevant commits
    git.populate()

    TrelloReconciler(jira, git, trello, tr_config).reconcile()

    end                 = time.time()
    duration            = int(end) - int(start)

    print('duration: {}s'.format(str(duration)))


if __name__ == '__main__':

    if len(sys.argv[1:]) == 0:
        main()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--dev":
        dev()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--testrail":
        testrail_main()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--testrail-dev":
        testrail_dev()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--gitlab":
        gitlab_main()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--gitlab-dev":
        gitlab_dev()

    elif len(sys.argv[1:]) == 1 and sys.argv[1] == "--github":
        raise NotImplementedError       # TODO

    else:
        raise ArgumentError("Not a valid argument")
