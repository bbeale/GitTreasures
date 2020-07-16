#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import TestRailException
from testrail_yak import TestRailYak


class TestRail:
    """
        Interface with the TestRail API.

        Data grabbed here and methods defined here will be used in TestRailReconciler.
    """

    def __init__(self, config):

        self.yak = TestRailYak(config["url"], config["user"], config["password"])
        self.users = self.get_users()
        self.current_test_run = None
        self.current_test_run_tests = []
        self.current_test_run_results = []
        self.current_test_run_passed = []
        self.current_test_run_failed = []

    def get_users(self):
        """Get a list of TestRail users.

        :return: response from TestRail API containing the user collection
        """
        try:
            result = self.yak.user.get_users()
        except TestRailException as error:
            raise error
        else:
            return result

    def get_user(self, user_id):
        """Get a TestRail user by user_id.

        :param user_id: user ID of the user we want to grab
        :return: response from TestRail API containing the user
        """
        if not user_id or user_id is None:
            raise TestRailException("[!] Invalid user_id")
        try:
            result = self.yak.user.get_user(user_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_projects(self):
        """Get all projects from the TestRail API."""
        try:
            result = self.yak.project.get_projects()
        except TestRailException as error:
            raise error
        else:
            return result

    def get_project(self, project_id):
        """Get a single project from the TestRail API by passing in its project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the project
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        try:
            result = self.yak.project.get_project(project_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_project(self, name, announcement=None, show_announcement=True, suite_mode=1):
        """Add a new project to TestRail.

        :param name: name of the new TestRail project
        :param announcement: brief description of the TestRail project
        :param show_announcement: a truthy value or True show the announcement, a falsey value or False hides it
        :param suite_mode: suite mode of the project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        :return: response from TestRail API containing the newly created project
        """
        if not name or name is None:
            raise TestRailException("[!] Invalid project name. Unable to create new project.")

        data = dict(
            announcement        = announcement,
            show_announcement   = show_announcement,
            suite_mode          = suite_mode
        )

        try:
            result = self.yak.project.add_project(name, data)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_sections(self, project_id, suite_id=None):
        """Get a list of test sections associated with a project_id and an optional suite_id

        :param project_id:
        :param suite_id:
        :return: response from TestRail API containing the collection of sections
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        if suite_id is not None:
            if type(suite_id) not in [int, float]:
                raise TestRailException("[!] suite_id must be an int or float")

            if suite_id <= 0:
                raise TestRailException("[!] suite_id must be > 0")

            try:
                result = self.yak.section.get_sections(project_id, suite_id)
            except TestRailException as error:
                raise error

        else:
            try:
                result = self.yak.section.get_sections(project_id, suite_id)
            except TestRailException as error:
                raise error

        if result is None:
            raise TestRailException("[!] None result detected.")
        else:
            return result

    def get_section(self, section_id):
        """Get test section from a test suite by section_id.

        :param section_id: section ID to grab section from
        :return: response from TestRail API containing the test section
        """
        if not section_id or section_id is None:
            raise TestRailException("[!] Invalid section_id")

        if type(section_id) not in [int, float]:
            raise TestRailException("[!] section_id must be an int or float")

        if section_id <= 0:
            raise TestRailException("[!] section_id must be > 0")

        try:
            result = self.yak.section.get_section(section_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_sprint_section(self, project_id, name):
        """Add a new section representing a "sprint" to a TestRail project.

        For readability, this separate method is just for adding parent sections (Jira sprints) vs child sections (Jira stories).

        To populate a new child section with a Jira story, use add_story_section() and give it the id value returned here.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test section
        :return: response from TestRail API containing the newly created test section
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailException("[!] Name field is required")

        try:
            result = self.yak.section.add_sprint_section(project_id, dict(name=name))
        except TestRailException as error:
            raise error
        else:
            return result

    def add_story_section(self, project_id, name, parent_id, description):
        """Add a new section representing a "story" to a TestRail project.

        This section will be assigned to a parent/child relationship with a parent section, thus parent_id is required.

        Use the id value returned by add_sprint_section as the parent_id.

        Because of this parent id requirement, no suite_id will be needed. If it is ever used in the future, add_sprint_section is the more appropriate place for it.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test section
        :param description: description of the test section
        :param parent_id: section ID of the parent section (to build section hierarchies)
        :return: response from TestRail API containing the newly created test section
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailException("[!] Name field is required")

        if not description or description is None:
            raise TestRailException("[!] Description field is required")

        try:
            result = self.yak.section.add_story_section(project_id, parent_id, dict(name=name, description=description))
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_suites(self, project_id):
        """Get a list of test suites associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test suites
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        try:
            result = self.yak.test_suite.get_test_suites(project_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_suite(self, suite_id):
        """Get a test suite by suite_id.

        :param suite_id: ID of the test suite
        :return: response from TestRail API containing the test suites
        """
        if not suite_id or suite_id is None:
            raise TestRailException("[!] Invalid suite_id")

        if type(suite_id) not in [int, float]:
            raise TestRailException("[!] suite_id must be an int or float")

        if suite_id <= 0:
            raise TestRailException("[!] suite_id must be > 0")

        try:
            result = self.yak.test_suite.get_test_suite(suite_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_test_suite(self, project_id, name, description):
        """Add a new test suite to a TestRail project.

        :param project_id: ID of the TestRail project
        :param name: name of the new TestRail test suite
        :param description: description of the test suite
        :return: response from TestRail API containing the newly created test suite
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailException("[!] Invalid suite name. Unable to add test suite.")

        if not description or description is None:
            raise TestRailException("[!] Invalid description. Unable to add test suite.")

        suite_data = dict(name=name, description=description)

        try:
            result = self.yak.test_suite.add_test_suite(project_id, suite_data)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_cases(self, project_id):
        """Get a list of test cases associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        try:
            result = self.yak.test_case.get_test_cases(project_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_case(self, case_id):
        """Get a test case by case_id.

        :param case_id: ID of the test case
        :return: response from TestRail API containing the test cases
        """
        if not case_id or case_id is None:
            raise TestRailException("[!] Invalid case_id")

        if type(case_id) not in [int, float]:
            raise TestRailException("[!] case_id must be an int or float")

        if case_id <= 0:
            raise TestRailException("[!] case_id must be > 0")

        try:
            result = self.yak.test_case.get_test_case(case_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_test_case(self, section_id, title, type_id=9, template_id=2, priority_id=None, estimate=None,
                      milestone_id=None, refs=None):
        """Add a test case to a project by section_id.

        :param section_id: ID of the TestRail section
        :param title: title of the test case
        :param type_id:
        :param template_id:
        :param priority_id:
        :param estimate:
        :param milestone_id:
        :param refs:
        :return: response from TestRail API containing the newly created test case
        """
        if not section_id or section_id is None:
            raise TestRailException("[!] Invalid section_id.")

        if type(section_id) not in [int, float]:
            raise TestRailException("[!] section_id must be an int or float.")

        if section_id <= 0:
            raise TestRailException("[!] section_id must be > 0.")

        try:
            self.get_section(section_id)["parent_id"] is not None
        except IndexError:
            raise TestRailException(
                "[!] parent_id must not be None as that would assign a test case directly to a sprint.")

        if not title or title is None:
            raise TestRailException("[!] Test case title required.")

        data = dict()

        # validate the optional args
        if type_id is not None:
            if type(type_id) != int:
                raise TestRailException("[!] type_id must be an int or float.")
            if type_id <= 0:
                raise TestRailException("[!] type_id must be > 0.")
            data["type_id"] = type_id

        if template_id is not None:
            if type(template_id) not in [int, float]:
                raise TestRailException("[!] template_id must be an int or float.")
            if template_id <= 0:
                raise TestRailException("[!] template_id must be > 0.")
            data["template_id"] = template_id

        if priority_id is not None:
            if type(priority_id) not in [int, float]:
                raise TestRailException("[!] priority_id must be an int or float.")
            if priority_id <= 0:
                raise TestRailException("[!] priority_id must be > 0.")
            data["priority_id"] = priority_id

        if estimate is not None:
            data["estimate"] = estimate

        if milestone_id is not None:
            if type(milestone_id) not in [int, float]:
                raise TestRailException("[!] milestone_id must be an int or float.")
            if milestone_id <= 0:
                raise TestRailException("[!] milestone_id must be > 0.")
            data["milestone_id"] = milestone_id

        if refs is not None:
            data["refs"] = refs

        try:
            result = self.yak.test_case.add_test_case(section_id, title, data)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_runs(self, project_id):
        """Get a list of test runs associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        try:
            result = self.yak.test_run.get_test_runs(project_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_run(self, run_id):
        """Get a test run by run_id.

        :param run_id: ID of the test run
        :return: response from TestRail API containing the test cases
        """
        if not run_id or run_id is None:
            raise TestRailException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailException("[!] run_id must be > 0")

        try:
            result = self.yak.test_run.get_test_run(run_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_test_run(self, project_id, name, description=None, milestone_id=None, assignedto_id=None, include_all=None, case_ids=None, refs=None):
        """Add a test run to a project.

        :param project_id: ID of the TestRail project
        :param name: name of the test case
        :param description:
        :param milestone_id:
        :param assignedto_id:
        :param include_all:
        :param case_ids:
        :param refs:
        :return: response from TestRail API containing the newly created test run
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id.")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float.")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0.")

        if not name or name is None:
            raise TestRailException("[!] Test run name value required.")

        data = dict()

        # optional args
        if description is not None:
            data["description"] = description

        if milestone_id is not None:
            if type(milestone_id) not in [int, float]:
                raise TestRailException("[!] milestone_id must be an int or float.")
            if milestone_id <= 0:
                raise TestRailException("[!] milestone_id must be > 0.")
            data["milestone_id"] = milestone_id

        if assignedto_id is not None:
            if type(assignedto_id) not in [int, float]:
                raise TestRailException("[!] assignedto_id must be an int or float.")
            if assignedto_id <= 0:
                raise TestRailException("[!] assignedto_id must be > 0.")
            data["assignedto_id"] = assignedto_id

        if include_all is not None:
            if type(include_all) != bool:
                raise TestRailException("[!] include_all must be a boolean.")
            data["assignedto_id"] = assignedto_id

        if case_ids is not None:
            data["case_ids"] = case_ids

        if refs is not None:
            data["refs"] = refs

        try:
            result = self.yak.test_run.add_test_run(project_id, name, data)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_run_tests(self, run_id):
        """Get a collection of individual tests by run_id.

        :param run_id: ID of the test run
        :return: response from TestRail API containing the test cases
        """
        if not run_id or run_id is None:
            raise TestRailException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailException("[!] run_id must be > 0")

        try:
            result = self.yak.test.get_test_run_tests(run_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_run_test(self, test_id):
        """Get an individual test.

        :param test_id: ID of the individual test
        :return: response from TestRail API containing the test
        """
        if not test_id or test_id is None:
            raise TestRailException("[!] Invalid test_id")

        if type(test_id) not in [int, float]:
            raise TestRailException("[!] test_id must be an int or float")

        if test_id <= 0:
            raise TestRailException("[!] test_id must be > 0")

        try:
            result = self.yak.test.get_test_run_test(test_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_plans(self, project_id):
        """Get a list of test plans associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0")

        try:
            result = self.yak.test_plan.get_test_plans(project_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_plan(self, plan_id):
        """Get a test plan by plan_id.

        :param plan_id: ID of the test plan
        :return: response from TestRail API containing the test cases
        """
        if not plan_id or plan_id is None:
            raise TestRailException("[!] Invalid plan_id")

        if type(plan_id) not in [int, float]:
            raise TestRailException("[!] plan_id must be an int or float")

        if plan_id <= 0:
            raise TestRailException("[!] plan_id must be > 0")

        try:
            result = self.yak.test_plan.get_test_plan(plan_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def add_test_plan(self, project_id, name):
        """Add a test plan to a project.

        :param project_id: ID of the TestRail project
        :param name: title of the test plan
        :return: response from TestRail API containing the newly created test plan
        """
        if not project_id or project_id is None:
            raise TestRailException("[!] Invalid project_id.")

        if type(project_id) not in [int, float]:
            raise TestRailException("[!] project_id must be an int or float.")

        if project_id <= 0:
            raise TestRailException("[!] project_id must be > 0.")

        if not name or name is None:
            raise TestRailException("[!] Test plan name value required.")

        # data = dict(name=name, include_all=True)

        try:
            result = self.yak.test_plan.add_test_plan(project_id, name)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_results(self, test_id):
        """

        :param test_id:
        :return:
        """
        if not test_id or test_id is None:
            raise TestRailException("[!] Invalid test_id")

        if type(test_id) not in [int, float]:
            raise TestRailException("[!] test_id must be an int or float")

        if test_id <= 0:
            raise TestRailException("[!] test_id must be > 0")

        try:
            result = self.yak.test_result.get_test_results(test_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_results_by_testcase(self, run_id, case_id):
        """

        :param run_id:
        :param case_id:
        :return:
        """
        if not run_id or run_id is None:
            raise TestRailException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailException("[!] run_id must be > 0")

        if not case_id or case_id is None:
            raise TestRailException("[!] Invalid case_id")

        if type(case_id) not in [int, float]:
            raise TestRailException("[!] case_id must be an int or float")

        if case_id <= 0:
            raise TestRailException("[!] case_id must be > 0")

        try:
            result = self.yak.test_result.get_testcase_test_results(run_id, case_id)
        except TestRailException as error:
            raise error
        else:
            return result

    def get_test_results_by_testrun(self, run_id):
        """

        :param run_id:
=        :return:
        """
        if not run_id or run_id is None:
            raise TestRailException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailException("[!] run_id must be > 0")

        try:
            result = self.yak.test_result.get_testrun_test_results(run_id)
        except TestRailException as error:
            raise error
        else:
            return result
