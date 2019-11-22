#!/usr/bin/env python
# -*- coding: utf-8 -*-
from subprocess import SubprocessError


# Trello board custom exceptions
class TrelloBoardException(Exception):
    pass


class BoardIdException(TrelloBoardException):
    pass


class ListIdException(TrelloBoardException):
    pass


class ListNameException(TrelloBoardException):
    pass


class CardException(TrelloBoardException):
    pass


class CardIdException(TrelloBoardException):
    pass


class CardNameException(TrelloBoardException):
    pass


class CardAttachmentException(TrelloBoardException):
    pass


class LabelException(TrelloBoardException):
    pass


class LabelIdException(TrelloBoardException):
    pass


class BoardException(TrelloBoardException):
    pass


class ListException(TrelloBoardException):
    pass


class MemberIdException(TrelloBoardException):
    pass


class ListIdNotSetException(TrelloBoardException):
    pass


class ChecklistIdException(TrelloBoardException):
    pass


class ChecklistItemException(TrelloBoardException):
    pass


class UpdateTrelloException(TrelloBoardException):
    pass


# GitLog
class GitLogException(Exception):
    pass


class InvalidBranchException(SubprocessError):
    pass


# Database
class DbException(Exception):
    pass


class DbPathException(DbException):
    pass


class DbQueryResultException(DbException):
    pass


class DbQueryAddValueException(DbException):
    pass


# TestRail
class TestRailException(Exception):
    pass


class TestRailUserException(TestRailException):
    pass


class TestRailProjectException(TestRailException):
    pass


class TestRailSectionException(TestRailException):
    pass


class TestRailTestSuiteException(TestRailException):
    pass


class TestRailTestCaseException(TestRailException):
    pass


class TestRailTestRunException(TestRailException):
    pass


class TestRailTestPlanException(TestRailException):
    pass


class TestRailNewEntityException(TestRailException):
    pass


class TestRailSuiteModeException(TestRailException):
    pass


# Reconcile Excptions
class ReconcileException(Exception):
    pass


# TrelloReconciler custom exceptions
class ReconcileTrelloException(ReconcileException):
    pass


class ReconcileJiraBoardException(ReconcileException):
    pass


class ReconcileJiraStoryException(ReconcileException):
    pass


class ReconcileGitLogException(ReconcileException):
    pass


class ReconcileGitCommitException(ReconcileException):
    pass


class ReconcileTrelloBoardException(ReconcileException):
    pass


class ReconcileTrelloCardException(ReconcileException):
    pass


class ReconcileTrelloListException(ReconcileException):
    pass


# TestRailReconciler custom exceptions
class ReconcileTestRailException(ReconcileException):
    pass


class ReconcileTestRailProjectException(ReconcileException):
    pass


# Jira
class JiraBoardException(Exception):
    pass


class JiraBoardProjectException(JiraBoardException):
    pass


class JiraBoardSprintException(JiraBoardException):
    pass


class JiraBoardIssueException(JiraBoardException):
    pass


class JiraBoardIssueFieldException(JiraBoardException):
    pass


class JiraBoardFilterException(JiraBoardException):
    pass


# GitLab
class GitLabLogException(Exception):
    pass


class GitLabLogRepoPathException(GitLabLogException):
    pass


class GitLabLogTokenException(GitLabLogException):
    pass


class GitLabLogProjectException(GitLabLogException):
    pass


class GitLabLogQueryException(GitLabLogException):
    pass


