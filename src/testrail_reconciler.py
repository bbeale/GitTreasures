#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import TestRailReconcilerException
from util import get_configs
import os


class TestRailReconciler:

    def __init__(self, testrail, jira, config):
        """Initialize the TestRailReconciler object to populate TestRail and Trello with Jira stories in need of regression testing.

        :param testrail: instance of TestRail
        :param jira: instance of JiraBoard
        """
        if not jira or jira is None:
            raise TestRailReconcilerException('[!] Initialization fail - missing JiraBoard instance')

        upath = (os.path.relpath(os.path.join('config', 'users.ini')))
        self.testers = [t for t in get_configs(['jira_displayname', 'trello_id'], upath).values()]

        print('[+] Grabbing Jira stories for TestRail...')

        self.testrail = testrail
        self.jira = jira
        self._filter_this_release = config['filter_this_release']   # 24007
        self.jira_project = None
        self.jira_board = None
        self.current_jira_sprint = None
        self.done_this_release = None
        self.testrail_project_name = None
        self.testrail_testrun_name = None
        self.testrail_project = None
        self.testrail_testruns = None
        self.test_results = []
        self.failed = []
        self.passed = []

        # 2 stage initialization
        self.populate()

    def populate(self):
        """Seocnd stage of reconciler initialization."""
        self.jira_project = self.get_jira_project()
        self.jira_board = self.get_jira_board()
        self.current_jira_sprint = self.get_current_jira_sprint(self.jira_board.id)
        self.done_this_release = self.get_jira_stories(self._filter_this_release)

        try:
            pname = self.current_jira_sprint.name
        except TestRailReconcilerException(
                '[!] current_jira_sprint undefined. Unable to determine project name from TestRail.') as error:
            raise error

        else:
            self.testrail_project_name = '{} Tests'.format(pname)
            self.testrail_testrun_name = '{} Testing'.format(pname)

    # Jira methods
    def get_jira_project(self):
        """Get the current project from JiraBoard instance.

        :return: the current project if it exists, None if not
        """
        return self.jira.get_project()

    def get_jira_board(self, key=None):
        """Get the current board from the current project on the instance.

        :param key:
        :return: the board if it exists, None if not
        """
        if key is None:
            key = self.jira.get_project()
        return self.jira.get_board(key)

    def get_current_jira_sprint(self, board_id):
        """Get the current sprint (and probably some Moodle bullshit becasue they are too incompetent to make their own Jira project...).

        :param board_id: board ID of the Jira board
        :return: the current sprint if one exists that matches criteria
        """
        if not board_id or board_id is None:
            raise TestRailReconcilerException('[!] Invalid board ID')
        return self.jira.get_current_sprint(board_id)

    def get_jira_stories(self, filter_id):
        """Get a list of Jira stories given the ID of a JQL filter.

        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :return: list of stories returned by the filter
        """
        if not filter_id or filter_id is None:
            raise TestRailReconcilerException('[!] Invalid filter ID')
        return self.jira.get_parsed_stories(self.jira.get_issues(filter_id), testrail_mode=True)

    def update_jira_filter(self, filter_id, query):
        """Update the query used by a JQL filter.

        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :param query: new JQL query string
        :return: JSON representation of the filter
        """
        if not filter_id or filter_id is None:
            raise TestRailReconcilerException('[!] Invalid filter ID')
        if not query or query is None:
            raise TestRailReconcilerException('[!] Invalid query')
        return self.jira.update_filter(filter_id, query)

    def new_jira_filter(self, name, query):
        """Create a new JQL filter.

        :param name: name of the new JQL filter
        :param query: JQL query string
        :return: JSON representation of the filter
        """
        if not name or name is None:
            raise TestRailReconcilerException('[!] Invalid name')
        if not query or query is None:
            raise TestRailReconcilerException('[!] Invalid query')
        return self.jira.add_new_filter(name, query)

    def is_for_qa(self, key):
        """Make sure the story is actually one for QA to test.

        :param key:
        :return:
        """
        if not key or key is None:
            raise TestRailReconcilerException('[!] Invalid key.')
        return self.jira.for_qa_team(key)

    # TestRail methods
    def _testrail_suite_exists(self, jira_key, project_id):
        """Check the existence of a test suite in TestRail (before adding a new one).

        :param jira_key:
        :param project_id:
        :return boolean: True if the test suite exists, False if not
        """
        if not jira_key or jira_key is None:
            raise TestRailReconcilerException('[!] Invalid jira_key')
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        test_suites = self.testrail.get_test_suites(project_id)
        test_suite  = next(filter(lambda s: jira_key.lower() in s['name'].lower(), test_suites), None)
        return True if test_suite is not None else False

    def get_testrail_project(self, name):
        """Get a project from TestRail by name.

        :param name:
        :return: the 'name' field of a TestRail project if it exists, otherwise None
        """
        if not name or name is None:
            raise TestRailReconcilerException('[!] Invalid project name')
        return next(filter(lambda p: p['name'] == name, self.testrail.get_projects()), None)

    def get_testrail_sections(self, project_id):
        """Get test sections attached to a TestRail project_id.

        :param project_id:
        :return:
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        if type(project_id) not in [int, float]:
            raise TestRailReconcilerException('[!] project_id must be an int or float')

        if project_id <= 0:
            raise TestRailReconcilerException('[!] project_id must be > 0')

        return self.testrail.get_sections(project_id)

    def get_testrail_section(self, section_id):
        """Get a test section.

        :param section_id:
        :return:
        """
        if not section_id or section_id is None:
            raise TestRailReconcilerException('[!] Invalid section_id')

        if type(section_id) not in [int, float]:
            raise TestRailReconcilerException('[!] section_id must be an int or float')

        if section_id <= 0:
            raise TestRailReconcilerException('[!] section_id must be > 0')

        return self.testrail.get_section(section_id)

    def get_testrail_testruns(self, project_id):
        """Get test runs attached to a TestRail project_id.

        :param project_id:
        :return:
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        if type(project_id) not in [int, float]:
            raise TestRailReconcilerException('[!] project_id must be an int or float')

        if project_id <= 0:
            raise TestRailReconcilerException('[!] project_id must be > 0')

        return self.testrail.get_test_runs(project_id)

    def populate_testrail_sections(self, project_id, jira_stories):
        """Populate test case 'sections' (or suites?) from each Jira item

        :param project_id: TestRail project_id
        :param jira_stories: Jira stories to add to TestRail
        :return list: list of items to add to TestRail
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        sections = []
        for js in jira_stories:
            data = dict(
                project_id      = project_id,
                jira_key        = js['jira_key'],
                name            = '{} - {}'.format(js['jira_key'], js['jira_summary']),
                announcement    = '{}\n\nURL:\n{}\n\nUpdated on:\n{}'.format(js['jira_desc'], js['jira_url'], js['jira_updated'])
            )
            sections.append(data)
        return sections

    def add_testrail_sprint(self, project_id, name):
        """Add a TestRail section representing a 2 week sprint within a release.

        :param project_id:
        :param name:
        :return:
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        if type(project_id) not in [int, float]:
            raise TestRailReconcilerException('[!] project_id must be an int or float')

        if project_id <= 0:
            raise TestRailReconcilerException('[!] project_id must be > 0')

        if not name or name is None:
            raise TestRailReconcilerException('[!] name is required.')

        return self.testrail.add_sprint_section(project_id, name)

    def add_testrail_story(self, project_id, name, parent_id, description):
        """Same as add_testrail_sprint but adds a sprint section with a sprint section id as its parent_id.

        :param project_id:
        :param parent_id:
        :param name:
        :param description:
        :return:
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        if type(project_id) not in [int, float]:
            raise TestRailReconcilerException('[!] project_id must be an int or float')

        if project_id <= 0:
            raise TestRailReconcilerException('[!] project_id must be > 0')

        if not name or name is None:
            raise TestRailReconcilerException('[!] name is required.')

        if not description or description is None:
            raise TestRailReconcilerException('[!] description is required.')

        if not parent_id or parent_id is None:
            raise TestRailReconcilerException('[!] Invalid parent_id')

        if type(parent_id) not in [int, float]:
            raise TestRailReconcilerException('[!] parent_id must be an int or float')

        if parent_id <= 0:
            raise TestRailReconcilerException('[!] parent_id must be > 0')

        return self.testrail.add_story_section(project_id, name, parent_id, description)

    def add_testrail_testcase(self, story_section_id, title, type_id=9, template_id=2, priority_id=None, estimate=None, milestone_id=None, refs=None):
        """Add a test case to the project.

        :param story_section_id:
        :param title:
        :param type_id:
        :param template_id:
        :param priority_id:
        :param estimate:
        :param milestone_id:
        :param refs:
        :return:
        """
        if not story_section_id or story_section_id is None:
            raise TestRailReconcilerException('[!] Need a section_id for a story to add a test case.')

        if type(story_section_id) not in [int, float]:
            raise TestRailReconcilerException('[!] story_section_id must be an int or float')

        if story_section_id <= 0:
            raise TestRailReconcilerException('[!] story_section_id must be > 0')

        if not title or title is None:
            raise TestRailReconcilerException('[!] A valid title is required.')

        data = dict()

        if type_id is not None and type(type_id) == int and type_id > 0:
            data['type_id'] = type_id

        if template_id is not None and type(template_id) == int and template_id > 0:
            data['template_id'] = template_id

        if priority_id is not None and type(priority_id) == int and priority_id > 0:
            data['priority_id'] = priority_id

        if estimate is not None and type(estimate) == str and estimate != '':
            data['estimate'] = estimate

        if milestone_id is not None and type(milestone_id) == int and milestone_id > 0:
            data['milestone_id'] = milestone_id

        if refs is not None and type(refs) == str and refs != '':
            data['refs'] = refs

        return self.testrail.add_test_case(story_section_id, title, **data)

    def add_testrail_testrun(self, project_id, name, description=None, milestone_id=None, assignedto_id=None, include_all=None, case_ids=None, refs=None):
        """Add a new test run to the project.

        :param project_id:
        :param name:
        :param description:
        :param milestone_id:
        :param assignedto_id:
        :param include_all:
        :param case_ids:
        :param refs:
        :return:
        """
        if not project_id or project_id is None:
            raise TestRailReconcilerException('[!] Invalid project_id')

        if type(project_id) not in [int, float]:
            raise TestRailReconcilerException('[!] project_id must be an int or float')

        if project_id <= 0:
            raise TestRailReconcilerException('[!] project_id must be > 0')

        if not name or name is None:
            raise TestRailReconcilerException('[!] A valid name is required.')

        data = dict()

        if description is not None:
            data['description'] = description

        if milestone_id is not None and type(milestone_id) == int and milestone_id > 0:
            data['milestone_id'] = milestone_id

        if assignedto_id is not None and type(assignedto_id) == int and assignedto_id > 0:
            data['assignedto_id'] = assignedto_id

        if include_all is not None:
            data['include_all'] = include_all

        if case_ids is not None:
            data['case_ids'] = case_ids

        if refs is not None:
            data['refs'] = refs

        return self.testrail.add_test_run(project_id, name, **data)

    def populate_release(self):
        """Populate TestRail project and test suites."""

        # try to get the current TestRail project
        self.testrail_project = self.get_testrail_project(self.testrail_project_name)

        # add a new TestRail project for the current release if none is found
        if self.testrail_project is None:
            self.testrail_project = self.testrail.add_project(self.testrail_project_name)

        # every section in the project -- sprints and stories alike
        all_sections = self.get_testrail_sections(self.testrail_project['id'])

        # get the sprint sections from the list of sections
        sprint_sections = list(filter(lambda s: s['parent_id'] is None, all_sections))

        # get the current sprint from Jira based on our project name
        current_sprint = next(filter(lambda s: s['name'] == self.current_jira_sprint.name, sprint_sections), None)

        if current_sprint is None:
            current_sprint = self.add_testrail_sprint(self.testrail_project['id'], self.current_jira_sprint.name)

        # get all STORIES, which should always have a parent ID
        story_sections = list(filter(lambda s: s['parent_id'] is not None, all_sections))
        current_sprint_stories = list(filter(lambda s: s['parent_id'] == current_sprint['id'], story_sections))

        # create new TestRail story sections from Jira stories
        new_story_sections = self.populate_testrail_sections(self.testrail_project['id'], self.done_this_release)

        release_story_names = [s['name'] for s in story_sections]
        sprint_story_names = [s['name'] for s in current_sprint_stories]

        # test run stuff
        current_testruns = self.get_testrail_testruns(self.testrail_project['id'])
        current_testrun_names = [tr['name'] for tr in current_testruns]

        for story in new_story_sections:
            if not self.is_for_qa(story['jira_key']):
                # ignore the story if a QA tester didn't test it
                continue

            in_release = True if next(filter(lambda r: story['jira_key'] in r, release_story_names), None) is not None else False
            in_sprint = True if next(filter(lambda s: story['jira_key'] in s, sprint_story_names), None) is not None else False

            if not in_release and not in_sprint:
                new_story_section = self.add_testrail_story(self.testrail_project['id'], name=story['name'], parent_id=current_sprint['id'], description=story['announcement'])
                self.add_testrail_testcase(new_story_section['id'], title='Placeholder (change my title when you are ready to write me)', refs=story['jira_key'])
            else:
                continue

        # figure out if a test run already exists
        has_testrun = True if next(filter(lambda tr: self.testrail_testrun_name in tr or 'Master' in tr, current_testrun_names), None) is not None else False

        # Last thing I should have to do is check if there's an existing test plan. If there is, new test cases will automatically be added to it.
        if not has_testrun:
            self.add_testrail_testrun(self.testrail_project['id'], self.testrail_testrun_name)

    def get_testrun_results(self):
        """Get results from TestRail test run. """
        run = next(filter(lambda tr: tr['name'] == self.testrail_testrun_name, self.get_testrail_testruns(self.testrail_project['id'])), None)
        if run is None:
            raise TestRailReconcilerException('[!] Test run {} not found.'.format(self.testrail_testrun_name))

        if run['failed_count'] == 0:
            print('[+] No new test failures found.')
            return None
        else:
            self.test_results = self.testrail.get_test_results_by_testrun(run_id=run['id'])

        self.failed = [r for r in self.test_results if r['status_id'] == 5]
        self.passed = [r for r in self.test_results if r['status_id'] == 1]
        self.add_defects_to_jira(run)
        self.jira_staging_transitions(run)
        print('[+] Added defect subtask(s) to Jira.')

    def add_defects_to_jira(self, test_run: dict):
        """Add subtasks to Jira for any failures.

        TODO, since we are officially using subtasks

        :param test_run:
        :return:
        """
        if len(test_run.keys()) == 0:
            raise TestRailReconcilerException('[!] Test run data required.')

        parent_story = None

        # result algorithm
        for f in self.failed:
            # get the failed step
            failed_step = next(filter(lambda s: s['status_id'] == 5, f['custom_step_results']), None)

            if failed_step is None:
                # assume it didn't actually fail (for now)
                continue

            # get the Jira key
            test = self.testrail.get_test_run_test(f['test_id'])
            case = self.testrail.get_test_case(test['case_id'])
            section = self.testrail.get_section(case['section_id'])
            parent_story = section['name']
            bug_report_title = '[TestRail] {}: {} - {} - {}'.format(
                parent_story, test['title'], failed_step['content'],  failed_step['actual'])
            bug_report_desc = '[TestRail - {}|{}]'.format(test_run['name'], test_run['url'])

            fields = {
                'summary': bug_report_title,
                'description': bug_report_desc,
                'project': {
                    'key': self.jira_project
                },
                'parent': {
                    'key': parent_story
                },
                'customfield_10131': {
                    'id': '10016'
                },
                'customfield_13020': {
                    'id': '12111'
                },
                'customfield_14821': {
                    'id': '14519'
                },
                'issuetype': {
                    'name': 'Defect'
                },
                'customfield_10151': {
                    'id': '10074'
                },
                'customfield_11409': {
                    'id': '14260'
                },
                'priority': {
                    'name': 'Minor'
                }
            }

            # add the subtask to Jira
            self.jira.jira.create_issue(fields=fields)

    def complete_jira_subtask(self, jira_story: str):
        """ TODO """
        raise NotImplementedError

    def jira_staging_transitions(self, test_run):
        """Transition Jira stories to 'Ready for Staging Release' when all tests pass.

        :param test_run:
        :return:
        """
        if test_run is None or len(test_run.key()) == 0:
            raise TestRailReconcilerException('[!] Test run reference required.')

        for p in self.passed:
            # get the AMB number
            test = self.testrail.get_test_run_test(p['test_id'])
            case = self.testrail.get_test_case(test['case_id'])
            section = self.testrail.get_section(case['section_id'])
            jira_story = section['name']

            # trigger staging transition
            _staging_transition_id = 1011
            self.jira.jira.transition_issue(jira_story, transition=_staging_transition_id)
