#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.testrail_reconciler import TestRailReconciler
from src.trello_reconciler import TrelloReconciler
from src.trello_board import TrelloBoard
from src.testrail import TestRail
from src.jira_board import JiraBoard
from src.gitlab_log import GitLabLog
from src.exceptions import DbException
from util import is_db_init, get_cli_args
from configparser import ConfigParser, ParsingError
import time
import os


def main(args):
    config = ConfigParser()
    try:
        config.read(os.path.join('config', 'config.ini'))
    except ParsingError as e:
        raise e

    # database path shouldn't change
    db_path = os.path.relpath(os.path.join(config.get('common', 'db_path')))
    if not is_db_init(db_path):
        raise DbException('[!] Database is not initialized. Run init.py in this directory to initialize the commit database, then re-run GitTreasures.')

    print('[+] Initializing GitTreasures')
    start = time.time()
    # initialize all my interface and reconciler classes
    if args.dev:
        trello = TrelloBoard(config, test_mode=True)
    else:
        trello = TrelloBoard(config)
    jira = JiraBoard(config)
    git = GitLabLog(config)
    trello.populate()
    git.populate()

    print('[+] Starting reconcile process')
    # run the TestRail reconcile process if true
    if args.testrail:
        testrail = TestRail(config)
        testrail_reconciler = TestRailReconciler(testrail, jira, config)
        testrail_reconciler.populate_release()

    # initialize the Trello reconciler
    trello_reconciler = TrelloReconciler(jira, git, trello, config)
    trello_reconciler.reconcile()
    end = time.time()
    duration = int(end) - int(start)
    print(f'[+] Done in {str(duration)}s')


if __name__ == '__main__':
    main(get_cli_args().parse_args())
