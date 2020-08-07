#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import TestRailException
from testrail_yak import TestRailYak
from testrail_yak.case import TestCaseException
from testrail_yak.plan import PlanException
from testrail_yak.project import ProjectException
from testrail_yak.result import ResultException
from testrail_yak.run import RunException
from testrail_yak.section import SectionException
from testrail_yak.suite import SuiteException
from testrail_yak.template import TemplateException
from testrail_yak.test import TestException
from testrail_yak.user import UserException


class TestRail:
    """Interface with the TestRail API.

       Data grabbed here and methods defined here will be used in TestRailReconciler.
    """

    def __init__(self, config: dict):

        self.yak = TestRailYak(config["url"], config["user"], config["password"])
        self.users = self.get_users()
        self.current_test_run = None
        self.current_test_run_tests = []
        self.current_test_run_results = []
        self.current_test_run_passed = []
        self.current_test_run_failed = []

    def get_test_cases(self, project_id: int) -> list:
        """Get a list of test cases associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.case.get_all(project_id)
        except TestCaseException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_case(self, case_id: int) -> dict:
        """Get a test case by case_id.

        :param case_id: ID of the test case
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.case.get(case_id)
        except TestCaseException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_test_case(self,
                      section_id: int,
                      title: str,
                      type_id: int = 9,
                      template_id: int = 2,
                      priority_id: int = None,
                      estimate: str = None,
                      milestone_id: int = None,
                      refs: str = None) -> dict:
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
        try:
            self.get_section(section_id)["parent_id"] is not None
        except IndexError:
            raise TestRailException(
                "[!] parent_id must not be None as that would assign a test case directly to a sprint.")

        data = {'title': title, "type_id": type_id}
        # optional args
        if template_id is not None:
            data["template_id"] = template_id

        if priority_id is not None:
            data["priority_id"] = priority_id

        if estimate is not None:
            data["estimate"] = estimate

        if milestone_id is not None:
            data["milestone_id"] = milestone_id

        if refs is not None:
            data["refs"] = refs

        try:
            result = self.yak.case.add(section_id, data)
        except TestCaseException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_plans(self, project_id: int) -> list:
        """Get a list of test plans associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.plan.get_all(project_id)
        except PlanException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_plan(self, plan_id: int) -> dict:
        """Get a test plan by plan_id.

        :param plan_id: ID of the test plan
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.plan.get(plan_id)
        except PlanException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_test_plan(self,
                      project_id: int,
                      name: str,
                      description: str = None,
                      milestone_id: int = None,
                      entries: list = None) -> dict:
        """Add a test plan to a project.

        :param project_id: ID of the TestRail project
        :param name: title of the test plan
        :param description: description of the test plan
        :param milestone_id:
        :param entries: test plan entries
        :return: response from TestRail API containing the newly created test plan
        """
        data = {'name': name}
        # optional args
        if description is not None:
            data["description"] = description

        if milestone_id is not None:
            data["milestone_id"] = milestone_id

        if entries is not None:
            data["entries"] = entries

        try:
            result = self.yak.plan.add(project_id, data)
        except PlanException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_projects(self) -> list:
        """Get all projects from the TestRail API."""
        try:
            result = self.yak.project.get_all()
        except ProjectException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_project(self, project_id: int) -> dict:
        """Get a single project from the TestRail API by passing in its project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the project
        """
        try:
            result = self.yak.project.get(project_id)
        except ProjectException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_project(self,
                    name: str,
                    announcement: str = None,
                    show_announcement: bool = True,
                    suite_mode: int = 1) -> dict:
        """Add a new project to TestRail.

        :param name: name of the new TestRail project
        :param announcement: brief description of the TestRail project
        :param show_announcement: a truthy value or True show the announcement, a falsey value or False hides it
        :param suite_mode: suite mode of the project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        :return: response from TestRail API containing the newly created project
        """
        data = {
            "announcement":         announcement,
            "show_announcement":    show_announcement,
            "suite_mode":           suite_mode
        }

        try:
            result = self.yak.project.add(name, data)
        except ProjectException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_report_by_project_id(self, project_id: int) -> dict:
        raise NotImplementedError

    def run_report(self, report_template_id: int) -> dict:
        raise NotImplementedError

    def get_results(self, test_id: int) -> list:
        """

        :param test_id:
        :return:
        """
        try:
            result = self.yak.result.get_all(test_id)
        except ResultException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_results_for_testcase(self, run_id: int, case_id: int) -> list:
        """Returns a list of test results for a test run and case combination.

        :param run_id:
        :param case_id:
        :return:
        """
        try:
            result = self.yak.result.get_all_from_test_case(run_id, case_id)
        except ResultException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_results_for_testrun(self, run_id: int) -> list:
        """Returns a list of test results for a test run.

        :param run_id:
        :return:
        """
        try:
            result = self.yak.result.get_all_from_test_run(run_id)
        except ResultException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_runs(self, project_id: int) -> list:
        """Get a list of test runs associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.run.get_all(project_id)
        except RunException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_run(self, run_id: int) -> dict:
        """Get a test run by run_id.

        :param run_id: ID of the test run
        :return: response from TestRail API containing the test cases
        """
        try:
            result = self.yak.run.get(run_id)
        except RunException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_test_run(self,
                     project_id: int,
                     name: str,
                     description: str = None,
                     milestone_id: int = None,
                     assignedto_id: int = None,
                     include_all: bool = None,
                     case_ids: list = None,
                     refs: str = None) -> dict:
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
        data = {'name': name}
        # optional args
        if description is not None:
            data["description"] = description

        if milestone_id is not None:
            data["milestone_id"] = milestone_id

        if assignedto_id is not None:
            data["assignedto_id"] = assignedto_id

        if include_all is not None:
            data["assignedto_id"] = assignedto_id

        if case_ids is not None:
            data["case_ids"] = case_ids

        if refs is not None:
            data["refs"] = refs

        try:
            result = self.yak.run.add(project_id, data)
        except RunException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_sections(self, project_id: int, suite_id: int = None) -> list:
        """Get a list of test sections associated with a project_id and an optional suite_id

        :param project_id:
        :param suite_id:
        :return: response from TestRail API containing the collection of sections
        """
        if suite_id is not None:
            try:
                result = self.yak.section.get_by_suite_id(project_id, suite_id)
            except SectionException as error:
                print("[!] TestRail error:\n", error)
                raise TestRailException

        else:
            try:
                result = self.yak.section.get_all(project_id)
            except SectionException as error:
                print("[!] TestRail error:\n", error)
                raise TestRailException

        if result is None:
            raise TestRailException("[!] None result detected.")
        else:
            return result

    def get_section(self, section_id: int) -> dict:
        """Get test section from a test suite by section_id.

        :param section_id: section ID to grab section from
        :return: response from TestRail API containing the test section
        """
        try:
            result = self.yak.section.get(section_id)
        except SectionException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_sprint_section(self, project_id: int, name: str) -> dict:
        """Add a new section representing a "sprint" to a TestRail project.

        For readability, this separate method is just for adding parent sections (Jira sprints) vs child sections (Jira stories).

        To populate a new child section with a Jira story, use add_story_section() and give it the id value returned here.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test section
        :return: response from TestRail API containing the newly created test section
        """
        try:
            result = self.yak.section.add(project_id, dict(name=name))
        except SectionException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_story_section(self, project_id: int, name: str, parent_id: int) -> dict:
        """Add a new section representing a "story" to a TestRail project.

        This section will be assigned to a parent/child relationship with a parent section, thus parent_id is required.

        Use the id value returned by add_sprint_section as the parent_id.

        Because of this parent id requirement, no suite_id will be needed. If it is ever used in the future, add_sprint_section is the more appropriate place for it.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test section
        :param parent_id: section ID of the parent section (to build section hierarchies)
        :return: response from TestRail API containing the newly created test section
        """
        try:
            result = self.yak.section.add_child(project_id, parent_id, {"name": name})
        except SectionException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_suites(self, project_id: int) -> list:
        """Get a list of test suites associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test suites
        """
        try:
            result = self.yak.suite.get_all(project_id)
        except SuiteException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test_suite(self, suite_id: int) -> dict:
        """Get a test suite by suite_id.

        :param suite_id: ID of the test suite
        :return: response from TestRail API containing the test suites
        """
        try:
            result = self.yak.suite.get(suite_id)
        except SuiteException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def add_test_suite(self, project_id: int, name: str, description: str) -> dict:
        """Add a new test suite to a TestRail project.

        :param project_id: ID of the TestRail project
        :param name: name of the new TestRail test suite
        :param description: description of the test suite
        :return: response from TestRail API containing the newly created test suite
        """
        suite_data = {"name": name, "description": description}
        try:
            result = self.yak.suite.add(project_id, suite_data)
        except SuiteException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_templates(self, project_id: int) -> list:
        """Returns a list of available templates.

        :param project_id:
        :return:
        """
        try:
            result = self.yak.template.get(project_id)
        except TemplateException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_tests(self, run_id: int) -> list:
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
            result = self.yak.test.get_all(run_id)
        except TestException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_test(self, test_id: int) -> dict:
        """Get an individual test.

        :param test_id: ID of the individual test
        :return: response from TestRail API containing the test
        """
        try:
            result = self.yak.test.get(test_id)
        except TestException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_users(self) -> list:
        """Get a list of TestRail users.

        :return: response from TestRail API containing the user collection
        """
        try:
            result = self.yak.user.get_all()
        except UserException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result

    def get_user(self, user_id: int) -> dict:
        """Get a TestRail user by user_id.

        :param user_id: user ID of the user we want to grab
        :return: response from TestRail API containing the user
        """
        try:
            result = self.yak.user.get(user_id)
        except UserException as error:
            print("[!] TestRail error:\n", error)
            raise TestRailException
        else:
            return result
