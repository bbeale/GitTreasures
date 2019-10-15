#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import (
    JiraBoardIssueException,
    JiraBoardIssueFieldException,
    JiraBoardFilterException,
    JiraBoardProjectException
)

from util import get_configs

from requests.exceptions import HTTPError
from urllib.parse import urljoin
from jira import JIRA
import dateutil.parser
import json
import os
import re


class JiraBoard:

    def __init__(self, config, testMode=False):
        """Initialize JiraBoard with all relevant QA Jira stories.

        :param config: Jira configuration settings
        :param testMode: if True, load test data from a JSON file instead of making requests to the API
        """
        print("Initializing JiraBoard")

        # Tester credentials import
        upath = (os.path.relpath(os.path.join("src", "users.ini")))
        self.testers = [t["jira_displayname"] for t in get_configs(["jira_displayname"], upath).values()]

        self.caller         = config["f_name"]
        self.host           = config["url"]
        self.username       = config["username"]
        self.password       = config["token"]
        self.project_key    = config["project_key"]
        self.testMode       = testMode
        self.options        = {"server": self.host}
        self.jira           = JIRA(self.options, auth=(self.username, self.password))
        self.board          = self.get_board(self.project_key)
        self.current_sprint = self.get_current_sprint(self.board.id)
        self.raw_issues     = []
        self.stories        = []

    def add_new_filter(self, filter_name, new_query):
        """Add a new JQL filter to the Jira project.

        :param filter_name: name for the filter
        :param new_query: filter criteria in the form of a JQL string.
        :return:
        """
        if not filter_name or filter_name is None:
            raise JiraBoardFilterException("Invalid issue_key")
        if not new_query or new_query is None:
            raise JiraBoardFilterException("Invalid or empty query")

        result = None
        try:
            result = self.jira.create_filter(filter_name, jql=new_query)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira stories.\nRetrying in a few seconds.")
            try:
                result = self.jira.create_filter(filter_name, jql=new_query)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira stories.")
        finally:
            return result

    def update_filter(self, filter_id, new_query):
        """Update an existing JQL filter associated with the Jira project.

        :param filter_id: id for the filter
        :param new_query: filter criteria in the form of a JQL string.
        :return:
        """
        if not filter_id or filter_id is None:
            raise JiraBoardIssueException("Invalid filter_id")
        if not new_query or new_query is None:
            raise JiraBoardFilterException("Invalid or empty query")

        result = None
        try:
            result = self.jira.update_filter(filter_id, jql=new_query)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to update Jira filter.\nRetrying in a few seconds.")
            try:
                result = self.jira.update_filter(filter_id, jql=new_query)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to update Jira filter.")
        finally:
            return result

    def get_project(self):
        """Get active Jira project.

        :return: JSON object representing entire Jira project, otherwise None
        """
        projects = None
        try:
            projects = self.jira.projects()
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira projects.\nRetrying in a few seconds.")
            try:
                projects = self.jira.projects()
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira projects.")
        finally:
            # projects = None # test!!!
            return next(filter(lambda proj: proj.key.upper() == self.project_key, projects), None)

    def get_board(self, project_key):
        """Get active Jira board given a project_key.

        :param project_key: Jira project key
        :return: JSON object representing entire Jira board, otherwise None
        """
        if not project_key or project_key is None:
            raise JiraBoardProjectException("Invalid project_key")

        boards = None
        try:
            boards = self.jira.boards(project_key)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira projects.\nRetrying in a few seconds.")
            try:
                boards = self.jira.boards(project_key)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira projects.")
        finally:
            # boards = None # test!!!
            return next(filter(lambda board: board.name.lower() == "medhub development", boards), None)

    def get_current_sprint(self, board_id):
        """Given a board_id, get the current sprint the project is in. Also try and filter out that Moodle shit.

        :param board_id: ID for the current Jira board
        :return:
        """
        if not board_id or board_id is None:
            raise JiraBoardIssueException("Invalid board_id")
        sprints = None
        try:
            sprints = self.jira.sprints(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira sprints.\nRetrying in a few seconds.")
            try:
                sprints = self.jira.sprints(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira sprints.")
        finally:
            # boards = None # test!!!
            return next(filter(lambda story: story.state.lower() == "active" and "moodle" not in story.name.lower() and "release sprint" in story.name.lower(), sprints), None)

    def get_jql_filter(self, filter_id):
        if not filter_id or filter_id is None:
            raise JiraBoardIssueException("Invalid filter_id")

        j_filter = None
        try:
            j_filter = self.jira.filter(filter_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira filter.\nRetrying in a few seconds.")
            try:
                j_filter = self.jira.filter(filter_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira filter.")
        finally:
            return j_filter

    def get_issues_from_filter(self, filter_id):
        """Get Jira issues returned by a given JQL filter_id.

        :param filter_id: id for the filter
        :return:
        """
        if not filter_id or filter_id is None:
            raise JiraBoardIssueException("Invalid filter_id")

        jql = self.get_jql_filter(filter_id).jql
        issues = None
        try:
            issues = self.jira.search_issues(jql, maxResults=100)
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get issues from Jira filter.\nRetrying in a few seconds.")
            try:
                issues = self.jira.search_issues(jql, maxResults=100)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get issues from Jira filter.")
        finally:
            return issues

    def get_issues(self, filter_id):
        """Seems weirdly like a dupe of get_issues_from_filter(), but if things are working I don't wanna break it right now..

        :param filter_id: id for the filter
        :return:
        """
        if not filter_id or filter_id is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issues = None
        if self.testMode:
            jsonData = open(os.path.join("testJiraData.json"), "r", encoding="utf-8")
            issues = json.loads(jsonData.read())
        else:
            try:
                issues = self.get_issues_from_filter(filter_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get issues from Jira filter.\nRetrying in a few seconds.")
                try:
                    issues = self.get_issues_from_filter(filter_id)
                except HTTPError as httpe:
                    print(httpe.response.status_code, "- Failed to get issues from Jira filter.")
        return issues

    def get_current_status(self, issue_key):
        """Get the current status for a given Jira story.

        :param issue_key: a Jira story key
        :return:
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is not None:
                return issue.fields.status.name
            else:
                return None

    def get_current_status_category(self, issue_key):
        """Get the status category for a given Jira story.

        :param issue_key: a Jira story key
        :return:
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is not None:
                return issue.fields.status.statusCategory.name
            else:
                return None

    def get_most_recent_status_change(self, issue_key):
        """Get the most recent status change for a Jira story, given it's issue_key.

        :param issue_key: a Jira story key
        :return: object representing the most recent status change
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is not None:
                return next(filter(lambda s: s["toString"], issue.fields.status.name), None)
            else:
                return None

    def is_hotfix(self, issue_key):
        """Given am issue_key, check if the story is a hotfix.

        :param issue_key: a Jira story key
        :return boolean: True if story is a hotfix, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="labels", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="labels", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is not None:
                return next(filter(lambda l: l.lower() == "hotfix", issue.fields.labels), None) is not None
            else:
                return False

    def isAtomic(self, issue_key):
        """Given am issue_key, check if the story is from Atomic Object.

        :param issue_key: a Jira story key
        :return boolean: True if story is from Atomic Object, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")
        return "MMDH-" in self.jira.issue(issue_key).key

    def is_in_staging(self, issue_key, stories):
        """Given am issue_key, check if the story is in the staging branch.

        :param issue_key: a Jira story key
        :param stories: a list of Jira stories
        :return boolean: True if story is in staging, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")
        if stories is None:
            raise JiraBoardIssueException("List of stories cannot be None")
        in_staging = False
        issue = next(filter(lambda story: story["jira_key"] == issue_key, stories), None)
        if issue is not None:
            in_staging = issue["in_staging"]
        return in_staging

    def is_fresh_qa_ready(self, issue_key):
        """Given am issue_key, check if the story is ready for QA for the very first time.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of "Ready for QA Release" and no fail statuses in the past, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        current_status = self.get_current_status(issue_key)
        qa_fail = self.has_failed_qa(issue_key)
        if current_status is None:
            raise JiraBoardIssueException("No current status found")
        return current_status == "Ready for QA Release" and not qa_fail

    def is_stale_qa_ready(self, issue_key):
        """Given am issue_key, check if the story is ready for QA after previously failing testing.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of "Ready for QA Release" and at least one prior fail status, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        current_status = self.get_current_status(issue_key)
        qa_fail = self.has_failed_qa(issue_key)
        if current_status is None:
            raise JiraBoardIssueException("No current status found")
        return current_status == "Ready for QA Release" and qa_fail

    def is_in_qa_testing(self, issue_key):
        """Given am issue_key, check if the story is currently in "QA Testing".

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of "QA Testing", otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        current_status = self.get_current_status(issue_key)
        if current_status is None:
            raise JiraBoardIssueException("No current status found")
        return current_status == "QA Testing"

    def has_complete_status(self, issue_key):
        """Given am issue_key, check if the story has a "Complete" status category.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status category of "Done", otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        current_status_category = self.get_current_status_category(issue_key)
        if current_status_category is None:
            raise JiraBoardIssueException("No current status  category found")
        return current_status_category == "Done"

    def passed_qa(self, issue_key):
        """Given an issue_key, check if the story has passed QA.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a passing status with a valid QA tester, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is None:
                raise JiraBoardIssueException("NoneType issue is not valid.")
            else:
                # Let's try this another way
                statuses = self.get_statuses(issue.changelog.histories)
                tester = next(filter(lambda s: s["authorName"] in self.testers, statuses), None)
                return self.has_complete_status(issue.key) and tester is not None

    def has_failed_qa(self, issue_key):
        """Given an issue_key, check if the story has failed QA in the past.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a fail status in the past, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is None:
                raise JiraBoardIssueException("NoneType issue is not valid.")
            else:
                # Let's try this another way
                statuses = self.get_statuses(issue.changelog.histories)
                failStatus      = next(filter(
                    lambda status: (status["authorName"] in self.testers)
                    and status["fromString"] == "QA Testing"
                    and status["toString"] == "In Progress", statuses
                ), None)
                return True if failStatus is not None else False

    def is_currently_failed(self, issue_key):
        """Given an issue_key, check if a Jira story currently has a failure status.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current fail status, otherwise False
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        current_status = self.get_current_status(issue_key)
        if current_status is None:
            raise JiraBoardIssueException("No current status found")
        return current_status in ["In Progress", "Backlog"]

    def get_statuses(self, change_log):
        """Get all status changes from a change_log associated with a Jira story.

        :param change_log: expanded list of fields returned from Jira API for a single issue
        :return list: a list of dicts representing the status change and it's author
        """
        if not change_log or change_log is None:
            raise JiraBoardIssueFieldException("change_log cannot be None")
        return [dict(
            authorName  = ch.author.displayName,
            created     = ch.created,
            fromString  = ch.items[0].fromString,
            toString    = ch.items[0].toString
        ) for ch in change_log if ch.items[0].field.lower() == "status"]

    # TODO: Test this. NEW METHOD!
    def get_subtasks(self, issue_key):
        """Get subtasks of a Jira story.

        :param issue_key: a Jira story key
        :return list: a list of subtask names
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="status", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="status", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is None:
                raise JiraBoardIssueException("NoneType issue is not valid.")
            else:
                return [task.lower() for task in issue.fields.subtasks]

    def get_attachments(self, issue_key):
        """Get attachments from a Jira story.

        :param issue_key: a Jira story key
        :return list: a list of URLs pointing to story attachments
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="attachment", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="attachment", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is None:
                raise JiraBoardIssueException("NoneType issue is not valid.")
            else:
                return ["{}secure/attachment/{}/{}".format(self.host, a.id, a.filename) for a in issue.fields.attachment]

    def get_labels(self, issue_key):
        """Get a list of labels attached to a story by issue_key.

        :param issue_key: a Jira story key
        :return list: a list Jira story labels
        """
        if not issue_key or issue_key is None:
            raise JiraBoardIssueException("Invalid issue_key")

        issue = None
        try:
            issue = self.jira.issue(issue_key, fields="labels", expand="changelog")
        except HTTPError as httpe:
            print(httpe.response.status_code, "- Failed to get Jira issue.\nRetrying in a few seconds.")
            try:
                issue = self.jira.issue(issue_key, fields="labels", expand="changelog")
            except HTTPError as httpe:
                print(httpe.response.status_code, "- Failed to get Jira issue.")
        finally:
            if issue is None:
                raise JiraBoardIssueException("NoneType issue is not valid.")
            else:
                return [label.lower() for label in issue.fields.labels]

    def get_parsed_stories(self, raw_issues):
        """Given a collection of raw Jira stories, parses them down to JSON objects containing needed fields only.

        :param raw_issues: JSON collection of stories returned from the Jira API
        :return parsed_stories: a list of parsed stories ready for one of the reconcile methods
        """
        if raw_issues is None:
            raise JiraBoardIssueException("List of raw Jira stories cannot be None")

        parsed_stories = []

        for issue in raw_issues:
            _story = self.jira.issue(
                issue.key, fields="summary,description,comment,labels,created,updated,status", expand="changelog"
            )

            _testedBy           = "unassigned"
            _hasFailed          = False
            _currentStatus      = self.get_current_status(_story.key)
            _changelog          = sorted(_story.changelog.histories, key=lambda ch: ch.created, reverse=True)
            _statuses           = self.get_statuses(_changelog)
            _validTester        = next(filter(lambda status: status["authorName"] in self.testers, _statuses), None)
            _testedBy           = _validTester["authorName"] if _validTester is not None else "unassigned"
            _url                = urljoin(self.host, "browse/{}".format(_story.key))
            _labels             = self.get_labels(_story.key)
            _summary            = "".join(re.findall(r'[^*`#\t\'"]', _story.fields.summary))
            _desc               = "".join(re.findall(r'[^*`#\t\'"]', _story.fields.description))

            if "testrail" in self.caller.lower():
                record = dict(
                    jira_key                = _story.key,
                    jira_url                = _url,
                    jira_summary            = _summary,
                    jira_desc               = _desc,
                    labels                  = _labels,
                    jira_created            = _story.fields.created,
                    jira_updated            = _story.fields.updated,
                    tested_by               = _testedBy,
                )

            else:
                _qaStatuses     = list(filter(lambda status: status["fromString"] == "QA Testing" or status["toString"] == "QA Testing", _statuses))
                _validTester    = next(filter(lambda status: status["authorName"] in self.testers, _statuses), None)

                _qaDateStatus   = next(filter(
                    lambda status: status["fromString"] == "In Progress"
                    and status["toString"] == "Ready for QA Release"
                    and _story.key not in parsed_stories, _statuses
                ), None)

                if _qaDateStatus is None:
                    raise Exception("No QA date found")

                _movedToQaDate  = dateutil.parser.parse(_qaDateStatus["created"])

                _hasFailed      = True if len(_qaStatuses) > 0 else False

                _testedBy       = _validTester["authorName"] if _validTester is not None else "unassigned"

                _comments       = "\n".join([
                    "\n_**{}** at {}_:\n\n{}\n\n".format(
                        comment.author,
                        dateutil.parser.parse(comment.updated).strftime("%Y-%m-%d %H:%M"),
                        "".join(re.findall(r'[^*`#\t\'"]', comment.body))
                    ) for comment in sorted(_story.fields.comment.comments, key=lambda s: s.updated, reverse=True)
                ])

                _statuses       = "\n".join([
                    "_**{}**_:\n\nFrom {} to {} at {}\n\n".format(
                        s["authorName"],
                        s["fromString"],
                        s["toString"],
                        dateutil.parser.parse(s["created"]).strftime("%Y-%m-%d %H:%M")
                    ) for s in _statuses
                ])

                if _movedToQaDate is not None:
                    _qaDate     = _movedToQaDate.strftime("%Y-%m-%d %H:%M:%S%z")
                else:
                    raise Exception("No QA date status found")

                _api_url        = urljoin(self.host, "rest/api/2/issue/{}".format(_story.key))
                _hotfix         = self.is_hotfix(_story.key)
                _inStaging      = False
                _attachments    = self.get_attachments(_story.key)

                record = dict(
                    jira_id                 = issue.id,
                    jira_key                = _story.key,
                    jira_url                = _url,
                    jira_api_url            = _api_url,
                    jira_summary            = _summary,
                    jira_desc               = _desc,
                    jira_created            = _story.fields.created,
                    jira_updated            = _story.fields.updated,
                    jira_qa_date            = _qaDate,
                    tested_by               = _testedBy,
                    current_status          = _currentStatus,
                    has_failed              = _hasFailed,
                    in_staging              = _inStaging,
                    is_hotfix               = _hotfix,
                    comments                = _comments,
                    statuses                = _statuses,
                    labels                  = _labels,
                    attachments             = _attachments,
                    last_known_commit_date  = None,
                    git_commit_message      = None,
                )

            parsed_stories.append(record)
        return sorted(parsed_stories, key=lambda story: story["jira_qa_date"])
