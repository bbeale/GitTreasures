#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Trello board custom exceptions
class TrelloBoardException(Exception):
    pass


# Database
class DbException(Exception):
    pass


# TestRail
class TestRailException(Exception):
    pass


# Reconcile Excptions
class TrelloReconcilerException(Exception):
    pass


class TestRailReconcilerException(Exception):
    pass


# Jira
class JiraBoardException(Exception):
    pass


# GitLab
class GitLabLogException(Exception):
    pass


