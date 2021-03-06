#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import get_configs
from src.exceptions import JiraBoardException
from urllib.parse import urljoin
from jira import JIRA, JIRAError
from jira.resources import Filter, Project, Board, Sprint, Issue
import dateutil.parser
import json
import os
import re


class JiraBoard(object):

    def __init__(self, config: dict, userpath: str = None, testMode: bool = False):
        """Initialize JiraBoard with all relevant QA Jira stories.

        :param config: Jira configuration settings
        :param testMode: if True, load test data from a JSON file instead of making requests to the API
        """
        print('[+] Initializing JiraBoard')

        # Tester credentials import
        if userpath is not None:
            upath = (os.path.relpath(os.path.join('config', userpath)))
        else:
            upath = (os.path.relpath(os.path.join('config', 'users.ini')))
        self.testers = [t['jira_displayname'] for t in get_configs(['jira_displayname'], upath).values()]

        self.host = config.get('url')
        self.username = config.get('username')
        self.password = config.get('token')
        self.project_key = config.get('project_key')
        self.testMode = testMode
        self.options = {'server': self.host}
        self.jira = JIRA(self.options, auth=(self.username, self.password))
        self.board = self.get_board(self.project_key)
        self.current_sprint = self.get_current_sprint(self.board.id)
        self.raw_issues = []
        self.stories = []

    def add_new_filter(self, filter_name: str, new_query: str) -> Filter:
        """Add a new JQL filter to the Jira project.

        :param filter_name: name for the filter
        :param new_query: filter criteria in the form of a JQL string.
        :return:
        """
        result = None
        try:
            result = self.jira.create_filter(filter_name, jql=new_query)
        except JIRAError:
            print('[!] Failed to get Jira stories.\nRetrying in a few seconds.')
            try:
                result = self.jira.create_filter(filter_name, jql=new_query)
            except JIRAError:
                print('[!] Failed to get Jira stories.')
        finally:
            return result

    def update_filter(self, filter_id: int, new_query: str) -> Filter:
        """Update an existing JQL filter associated with the Jira project.

        :param filter_id: id for the filter
        :param new_query: filter criteria in the form of a JQL string.
        :return:
        """
        result = None
        try:
            result = self.jira.update_filter(filter_id, jql=new_query)
        except JIRAError:
            print('[!] Failed to update Jira filter.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                result = self.jira.update_filter(filter_id, jql=new_query)
            except JIRAError:
                print('[!] Failed to update Jira filter.'.format(str(JIRAError)))
        finally:
            return result

    def get_project(self) -> Project:
        """Get active Jira project.

        :return: JSON object representing entire Jira project, otherwise None
        """
        projects = None
        try:
            projects = self.jira.projects()
        except JIRAError:
            print('[!] Failed to get Jira projects.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                projects = self.jira.projects()
            except JIRAError:
                print('[!] Failed to get Jira projects.'.format(str(JIRAError)))
        finally:
            return next(filter(lambda proj: proj.key.upper() == self.project_key, projects), None)

    def get_board(self, project_key: str) -> Board:
        """Get active Jira board given a project_key.

        :param project_key: Jira project key
        :return: JSON object representing entire Jira board, otherwise None
        """
        boards = None
        try:
            boards = self.jira.boards(project_key)
        except JIRAError:
            print('[!] Failed to get Jira projects.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                boards = self.jira.boards(project_key)
            except JIRAError:
                print('[!] Failed to get Jira projects.'.format(str(JIRAError)))
        finally:
            return next(filter(lambda board: board.name.lower() == 'medhub development', boards), None)

    def get_current_sprint(self, board_id: int) -> Sprint:
        """Given a board_id, get the current sprint the project is in. Also try and filter out that Moodle shit.

        :param board_id: ID for the current Jira board
        :return:
        """
        sprints = None
        try:
            sprints = self.jira.sprints(board_id)
        except JIRAError:
            print('[!] Failed to get Jira sprints.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                sprints = self.jira.sprints(board_id)
            except JIRAError:
                print('[!] Failed to get Jira sprints.'.format(str(JIRAError)))
        finally:
            res = next(filter(lambda story: story.state.lower() == 'active' and 'yaks' in story.name.lower(), sprints), None)
            if res is None:
                raise JiraBoardException('[!] No current sprint')
            return res

    def get_jql_filter(self, filter_id: int) -> Filter:
        j_filter = None
        try:
            j_filter = self.jira.filter(filter_id)
        except JIRAError:
            print('[!] Failed to get Jira filter.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                j_filter = self.jira.filter(filter_id)
            except JIRAError:
                print('[!] Failed to get Jira filter.'.format(str(JIRAError)))
        finally:
            return j_filter

    def get_issues_from_filter(self, filter_id: int) -> list:
        """Get Jira issues returned by a given JQL filter_id.

        :param filter_id: id for the filter
        :return:
        """
        jql = self.get_jql_filter(filter_id).jql
        issues = None
        try:
            issues = self.jira.search_issues(jql, maxResults=100)
        except JIRAError:
            print('[!] Failed to get issues from Jira filter.\nRetrying in a few seconds.'.format(str(JIRAError)))
            try:
                issues = self.jira.search_issues(jql, maxResults=100)
            except JIRAError:
                print('[!] Failed to get issues from Jira filter.'.format(str(JIRAError)))
        finally:
            return issues

    def get_issues(self, filter_id: int) -> list:
        """Seems weirdly like a dupe of get_issues_from_filter(), but if things are working I don't wanna break it right now..

        :param filter_id: id for the filter
        :return:
        """
        issues = None
        if self.testMode:
            jsonData = open(os.path.join('testJiraData.json'), 'r', encoding='utf-8')
            issues = json.loads(jsonData.read())
        else:
            try:
                issues = self.get_issues_from_filter(filter_id)
            except JIRAError:
                print('[!] Failed to get issues from Jira filter.\nRetrying in a few seconds.'.format(str(JIRAError)))
                try:
                    issues = self.get_issues_from_filter(filter_id)
                except JIRAError:
                    print('[!] Failed to get issues from Jira filter.'.format(str(JIRAError)))
        return issues

    def get_issue(self, issue_key: str, fields: str = 'status') -> Issue:
        """Get a Jira story given a key.

        :param issue_key: a Jira story key
        :param fields:
        :return:
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields=fields, expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields=fields, expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is None:
                raise JiraBoardException('[!] Unable to retrieve issue {}'.format(issue_key))
            return issue

    def get_current_status(self, issue_key: str) -> str or None:
        """Get the current status for a given Jira story.

        :param issue_key: a Jira story key
        :return:
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is not None:
                return issue.fields.status.name
            else:
                return None

    def get_current_status_category(self, issue_key: str) -> str or None:
        """Get the status category for a given Jira story.

        :param issue_key: a Jira story key
        :return:
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is not None:
                return issue.fields.status.statusCategory.name
            else:
                return None

    def get_most_recent_status_change(self, issue_key: str) -> str or None:
        """Get the most recent status change for a Jira story, given it's issue_key.

        :param issue_key: a Jira story key
        :return: object representing the most recent status change
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is not None:
                return next(filter(lambda s: s['toString'], issue.fields.status.name), None)
            else:
                return None

    def is_hotfix(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story is a hotfix.

        :param issue_key: a Jira story key
        :return boolean: True if story is a hotfix, otherwise False
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='labels', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='labels', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is not None:
                return next(filter(lambda l: l.lower() == 'hotfix', issue.fields.labels), None) is not None
            else:
                return False

    def is_atomic(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story is from Atomic Object.

        :param issue_key: a Jira story key
        :return boolean: True if story is from Atomic Object, otherwise False
        """
        return 'MMDH-' in self.jira.issue(issue_key).key

    def is_in_staging(self, issue_key: str, stories: list) -> bool:
        """Given am issue_key, check if the story is in the staging branch.

        :param issue_key: a Jira story key
        :param stories: a list of Jira stories
        :return boolean: True if story is in staging, otherwise False
        """
        in_staging = False
        issue = next(filter(lambda story: story['jira_key'] == issue_key, stories), None)
        if issue is not None:
            in_staging = issue['in_staging']
        return in_staging

    def is_fresh_qa_ready(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story is ready for QA for the very first time.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of "Ready for QA Release" and no fail statuses in the past, otherwise False
        """
        current_status = self.get_current_status(issue_key)
        qa_fail = self.has_failed_qa(issue_key)
        if current_status is None:
            raise JiraBoardException('[!] No current status found')
        return current_status == 'Ready for QA Release' and not qa_fail

    def is_stale_qa_ready(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story is ready for QA after previously failing testing.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of 'Ready for QA Release' and at least one prior fail status, otherwise False
        """
        current_status = self.get_current_status(issue_key)
        qa_fail = self.has_failed_qa(issue_key)
        if current_status is None:
            raise JiraBoardException('[!] No current status found')
        return current_status == 'Ready for QA Release' and qa_fail

    def is_in_qa_testing(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story is currently in 'QA Testing'.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status of 'QA Testing', otherwise False
        """
        current_status = self.get_current_status(issue_key)
        if current_status is None:
            raise JiraBoardException('[!] No current status found')
        return current_status == 'QA Testing'

    def has_complete_status(self, issue_key: str) -> bool:
        """Given am issue_key, check if the story has a 'Complete' status category.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current status category of 'Done', otherwise False
        """
        current_status_category = self.get_current_status_category(issue_key)
        if current_status_category is None:
            raise JiraBoardException('[!] No current status category found')
        return current_status_category == 'Done'

    def for_qa_team(self, issue_key: str) -> bool:
        """Similar to passed_qa but checks if a QA tester moved this at any point to make sure it actually got tested.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a status change with a valid QA tester, otherwise False
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                # Let's try this another way
                statuses = self.get_statuses(issue.changelog.histories)
                tester = next(filter(lambda s: s['authorName'] in self.testers and 'qa release' in s['fromString'].lower() and 'qa testing' in s['toString'].lower(), statuses), None)
                return tester is not None

    def passed_qa(self, issue_key: str) -> bool:
        """Given an issue_key, check if the story has passed QA.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a passing status with a valid QA tester, otherwise False
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                statuses = self.get_statuses(issue.changelog.histories)
                tester = next(filter(lambda s: s['authorName'] in self.testers, statuses), None)
                return self.has_complete_status(issue.key) and tester is not None

    def has_failed_qa(self, issue_key: str) -> bool:
        """Given an issue_key, check if the story has failed QA in the past.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a fail status in the past, otherwise False
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                statuses = self.get_statuses(issue.changelog.histories)
                failStatus      = next(filter(
                    lambda status: (status['authorName'] in self.testers)
                    and status['fromString'] == 'QA Testing'
                    and status['toString'] == 'In Progress', statuses
                ), None)
                return True if failStatus is not None else False

    def is_currently_failed(self, issue_key: str) -> bool:
        """Given an issue_key, check if a Jira story currently has a failure status.

        :param issue_key: a Jira story key
        :return boolean: True if the story has a current fail status, otherwise False
        """
        current_status = self.get_current_status(issue_key)
        if current_status is None:
            raise JiraBoardException('[!] No current status found')
        return current_status in ['In Progress', 'Backlog']

    def is_defect(self, issue_key: str) -> bool:
        """Return True if Jira issuetype is a defect.

        :param issue_key:
        :return:
        """
        return self.get_issue(
            issue_key,
            fields='issuetype').fields.issuetype.name.lower() == 'defect'

    def is_qa_task(self, issue_key: str) -> bool:
        """Return True if Jira issuetype is a defect.

        :param issue_key:
        :return:
        """
        return self.get_issue(
            issue_key,
            fields='issuetype').fields.issuetype.name.lower() == 'qa task'

    def is_bug(self, issue_key: str) -> bool:
        """Return True if Jira issuetype is a bug.

        :param issue_key:
        :return:
        """
        return self.get_issue(
            issue_key,
            fields='issuetype').fields.issuetype.name.lower() == 'bug'

    def get_statuses(self, change_log: dict) -> list:
        """Get all status changes from a change_log associated with a Jira story.

        :param change_log: expanded list of fields returned from Jira API for a single issue
        :return list: a list of dicts representing the status change and it's author
        """
        return [dict(
            authorName  = ch.author.displayName,
            created     = ch.created,
            fromString  = ch.items[0].fromString,
            toString    = ch.items[0].toString
        ) for ch in change_log if ch.items[0].field.lower() == 'status']

    def get_subtasks(self, issue_key: str) -> list:
        """Get subtasks of a Jira story.

        :param issue_key: a Jira story key
        :return list: a list of subtask names
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='status', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='status', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.')
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                return [task.lower() for task in issue.fields.subtasks]

    def get_attachments(self, issue_key: str) -> list:
        """Get attachments from a Jira story.

        :param issue_key: a Jira story key
        :return list: a list of URLs pointing to story attachments
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='attachment', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='attachment', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.'.format(str(JIRAError)))
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                return ['{}secure/attachment/{}/{}'.format(self.host, a.id, a.filename) for a in issue.fields.attachment]

    def get_labels(self, issue_key: str) -> list:
        """Get a list of labels attached to a story by issue_key.

        :param issue_key: a Jira story key
        :return list: a list Jira story labels
        """
        issue = None
        try:
            issue = self.jira.issue(issue_key, fields='labels', expand='changelog')
        except JIRAError:
            print('[!] Failed to get Jira issue.\nRetrying in a few seconds.')
            try:
                issue = self.jira.issue(issue_key, fields='labels', expand='changelog')
            except JIRAError:
                print('[!] Failed to get Jira issue.'.format(str(JIRAError)))
        finally:
            if issue is None:
                raise JiraBoardException('[!] NoneType issue is not valid.')
            else:
                return [label.lower() for label in issue.fields.labels]

    def get_parsed_stories(self, raw_issues: list, testrail_mode: bool = False) -> list:
        """Given a collection of raw Jira stories, parses them down to JSON objects containing needed fields only.

        :param raw_issues: JSON collection of stories returned from the Jira API
        :param testrail_mode: Should QA dates be ignored? If they're in the release but haven't been QAed yet... yes.
        :return parsed_stories: a list of parsed stories ready for one of the reconcile methods
        """
        parsed_stories = []

        for issue in raw_issues:
            _story              = self.get_issue(issue.key,
                                                 fields='summary,description,comment,labels,created,updated,status')
            _testedBy           = 'unassigned'
            _hasFailed          = False
            _currentStatus      = self.get_current_status(_story.key)
            _changelog          = sorted(_story.changelog.histories, key=lambda ch: ch.created, reverse=True)
            _statuses           = self.get_statuses(_changelog)
            _validTester        = next(filter(lambda status: status['authorName'] in self.testers, _statuses), None)
            _testedBy           = _validTester['authorName'] if _validTester is not None else 'unassigned'
            _url                = urljoin(self.host, 'browse/{}'.format(_story.key))
            _labels             = self.get_labels(_story.key)

            if _story.fields.summary is not None:
                _summary = ''.join(re.findall(r'[^*`#\t\'"]', _story.fields.summary))
            else:
                _summary = ''

            if _story.fields.description is not None:
                _desc = ''.join(re.findall(r'[^*`#\t\'"]', _story.fields.description))
            else:
                _desc = ''

            if testrail_mode:
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
                _qaStatuses     = list(filter(lambda status: status['fromString'] == 'QA Testing' or status['toString'] == 'QA Testing', _statuses))
                _validTester    = next(filter(lambda status: status['authorName'] in self.testers, _statuses), None)

                _qaDateStatus   = next(filter(
                    lambda status: status['fromString'] == 'In Progress'
                    and status['toString'] == 'Ready for QA Release'
                    and _story.key not in parsed_stories, _statuses
                ), None)

                if _qaDateStatus is None:
                    if self.is_defect(_story.key) or self.is_qa_task(_story.key):
                        print(f'[-] Skipping defect {str(issue.key)} because parent story should exist.')
                        continue

                    print(f'[!] QA date not found on {str(issue.key)}\n\tEither the issue type did not get excluded or a developer may have accidentally moved the story into QA')
                    _movedToQaDate = dateutil.parser.parse(_story.fields.updated)
                else:
                    _movedToQaDate  = dateutil.parser.parse(_qaDateStatus['created'])

                _hasFailed      = True if len(_qaStatuses) > 0 else False

                _testedBy       = _validTester['authorName'] if _validTester is not None else 'unassigned'

                _comments       = '\n'.join([
                    '\n_**{}** at {}_:\n\n{}\n\n'.format(
                        comment.author,
                        dateutil.parser.parse(comment.updated).strftime('%Y-%m-%d %H:%M'),
                        ''.join(re.findall(r'[^*`#\t\'"]', comment.body))
                    ) for comment in sorted(_story.fields.comment.comments, key=lambda s: s.updated, reverse=True)
                ])

                _statuses       = '\n'.join([
                    '_**{}**_:\n\nFrom {} to {} at {}\n\n'.format(
                        s['authorName'],
                        s['fromString'],
                        s['toString'],
                        dateutil.parser.parse(s['created']).strftime('%Y-%m-%d %H:%M')
                    ) for s in _statuses
                ])

                if _movedToQaDate is not None:
                    _qaDate     = _movedToQaDate.strftime('%Y-%m-%d %H:%M:%S%z')
                else:
                    raise JiraBoardException('[!] No QA date status found')

                _api_url        = urljoin(self.host, 'rest/api/2/issue/{}'.format(_story.key))
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

        if testrail_mode:
            result = sorted(parsed_stories, key=lambda story: story['jira_updated'])
        else:
            result = sorted(parsed_stories, key=lambda story: story['jira_qa_date'])
        return result
