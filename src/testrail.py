#!/usr/bin/env python
# -*- coding: utf-8 -*-
from testrail_yak import TestRailYak


class TestRail:
    """
        Interface with the TestRail API.

        Data grabbed here and methods defined here will be used in TestRailReconciler.
    """

    def __init__(self, config):

        self.yak = TestRailYak(config["url"], config["user"], config["password"])
        self.users = self.get_users()

    """
        Getters

        These methods grab entitles from the TestRail REST API. 
    """

    def get_users(self):
        """Get a list of TestRail users.

        :return: response from TestRail API containing the user collection
        """
        try:
            result = self.yak.user.get_users()
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_user(self, user_id):
        """Get a TestRail user by user_id.

        :param user_id: user ID of the user we want to grab
        :return: response from TestRail API containing the user
        """
        if not user_id or user_id is None:
            raise TestRailValidationException("[!] Invalid user_id")
        try:
            result = self.yak.user.get_user(user_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_projects(self):
        """Get all projects from the TestRail API."""
        try:
            result = self.yak.project.get_projects()
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_project(self, project_id):
        """Get a single project from the TestRail API by passing in its project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the project
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        try:
            result = self.yak.project.get_project(project_id)
        except NewTestRailException as error:
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
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        if suite_id is not None:
            if type(suite_id) not in [int, float]:
                raise TestRailValidationException("[!] suite_id must be an int or float")

            if suite_id <= 0:
                raise TestRailValidationException("[!] suite_id must be > 0")

            try:
                result = self.yak.section.get_sections(project_id, suite_id)
            except NewTestRailException as error:
                raise error

        else:
            try:
                result = self.yak.section.get_sections(project_id, suite_id)
            except NewTestRailException as error:
                raise error

        if result is None:
            raise TestRailValidationException("[!] None result detected.")
        else:
            return result

    def get_section(self, section_id):
        """Get test section from a test suite by section_id.

        :param section_id: section ID to grab section from
        :return: response from TestRail API containing the test section
        """
        if not section_id or section_id is None:
            raise TestRailValidationException("[!] Invalid section_id")

        if type(section_id) not in [int, float]:
            raise TestRailValidationException("[!] section_id must be an int or float")

        if section_id <= 0:
            raise TestRailValidationException("[!] section_id must be > 0")

        try:
            result = self.yak.section.get_section(section_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_suites(self, project_id):
        """Get a list of test suites associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test suites
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        try:
            result = self.yak.test_suite.get_test_suites(project_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_suite(self, suite_id):
        """Get a test suite by suite_id.

        :param suite_id: ID of the test suite
        :return: response from TestRail API containing the test suites
        """
        if not suite_id or suite_id is None:
            raise TestRailValidationException("[!] Invalid suite_id")

        if type(suite_id) not in [int, float]:
            raise TestRailValidationException("[!] suite_id must be an int or float")

        if suite_id <= 0:
            raise TestRailValidationException("[!] suite_id must be > 0")

        try:
            result = self.yak.test_suite.get_test_suite(suite_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_cases(self, project_id):
        """Get a list of test cases associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        try:
            result = self.yak.test_case.get_test_cases(project_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_case(self, case_id):
        """Get a test case by case_id.

        :param case_id: ID of the test case
        :return: response from TestRail API containing the test cases
        """
        if not case_id or case_id is None:
            raise TestRailValidationException("[!] Invalid case_id")

        if type(case_id) not in [int, float]:
            raise TestRailValidationException("[!] case_id must be an int or float")

        if case_id <= 0:
            raise TestRailValidationException("[!] case_id must be > 0")

        try:
            result = self.yak.test_case.get_test_case(case_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_runs(self, project_id):
        """Get a list of test runs associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        try:
            result = self.yak.test_run.get_test_runs(project_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_run(self, run_id):
        """Get a test run by run_id.

        :param run_id: ID of the test run
        :return: response from TestRail API containing the test cases
        """
        if not run_id or run_id is None:
            raise TestRailValidationException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailValidationException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailValidationException("[!] run_id must be > 0")

        try:
            result = self.yak.test_run.get_test_run(run_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_run_tests(self, run_id):
        """Get a collection of individual tests by run_id.

        :param run_id: ID of the test run
        :return: response from TestRail API containing the test cases
        """
        if not run_id or run_id is None:
            raise TestRailValidationException("[!] Invalid run_id")

        if type(run_id) not in [int, float]:
            raise TestRailValidationException("[!] run_id must be an int or float")

        if run_id <= 0:
            raise TestRailValidationException("[!] run_id must be > 0")

        try:
            result = self.yak.test.get_test_run_tests(run_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_run_test(self, test_id):
        """Get an individual test.

        :param test_id: ID of the individual test
        :return: response from TestRail API containing the test
        """
        if not test_id or test_id is None:
            raise TestRailValidationException("[!] Invalid test_id")

        if type(test_id) not in [int, float]:
            raise TestRailValidationException("[!] test_id must be an int or float")

        if test_id <= 0:
            raise TestRailValidationException("[!] test_id must be > 0")

        try:
            result = self.yak.test.get_test_run_test(test_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_plans(self, project_id):
        """Get a list of test plans associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        try:
            result = self.yak.test_plan.get_test_plans(project_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def get_test_plan(self, plan_id):
        """Get a test plan by plan_id.

        :param plan_id: ID of the test plan
        :return: response from TestRail API containing the test cases
        """
        if not plan_id or plan_id is None:
            raise TestRailValidationException("[!] Invalid plan_id")

        if type(plan_id) not in [int, float]:
            raise TestRailValidationException("[!] plan_id must be an int or float")

        if plan_id <= 0:
            raise TestRailValidationException("[!] plan_id must be > 0")

        try:
            result = self.yak.test_plan.get_test_plan(plan_id)
        except NewTestRailException as error:
            raise error
        else:
            return result

    """
        Setters

        Use these methods to create new entitles using the TestRail REST API. 
    """

    def add_project(self, name, announcement=None, show_announcement=True, suite_mode=1):
        """Add a new project to TestRail.

        :param name: name of the new TestRail project
        :param announcement: brief description of the TestRail project
        :param show_announcement: a truthy value or True show the announcement, a falsey value or False hides it
        :param suite_mode: suite mode of the project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        :return: response from TestRail API containing the newly created project
        """
        if not name or name is None:
            raise TestRailValidationException("[!] Invalid project name. Unable to create new project.")

        data = dict(
            announcement        = announcement,
            show_announcement   = show_announcement,
            suite_mode          = suite_mode
        )

        try:
            result = self.yak.project.add_project(name, data)
        except NewTestRailException as error:
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
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailValidationException("[!] Name field is required")

        try:
            result = self.yak.section.add_sprint_section(project_id, dict(name=name))
        except NewTestRailException as error:
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
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailValidationException("[!] Name field is required")

        if not description or description is None:
            raise TestRailValidationException("[!] Description field is required")

        try:
            result = self.yak.section.add_story_section(project_id, parent_id, dict(name=name, description=description))
        except NewTestRailException as error:
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
            raise TestRailValidationException("[!] Invalid project_id")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0")

        if not name or name is None:
            raise TestRailValidationException("[!] Invalid suite name. Unable to add test suite.")

        if not description or description is None:
            raise TestRailValidationException("[!] Invalid description. Unable to add test suite.")

        suite_data = dict(name=name, description=description)

        try:
            result = self.yak.test_suite.add_test_suite(project_id, suite_data)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def add_test_case(self, section_id, title, type_id=9, template_id=None, priority_id=None, estimate=None,
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
            raise TestRailValidationException("[!] Invalid section_id.")

        if type(section_id) not in [int, float]:
            raise TestRailValidationException("[!] section_id must be an int or float.")

        if section_id <= 0:
            raise TestRailValidationException("[!] section_id must be > 0.")

        try:
            self.get_section(section_id)["parent_id"] is not None
        except IndexError:
            raise TestRailValidationException(
                "[!] parent_id must not be None as that would assign a test case directly to a sprint.")

        if not title or title is None:
            raise TestRailValidationException("[!] Test case title required.")

        data = dict(title=title, type_id=type_id)

        # validate the optional args
        if template_id is not None:
            if type(template_id) not in [int, float]:
                raise TestRailValidationException("[!] template_id must be an int or float.")
            if template_id <= 0:
                raise TestRailValidationException("[!] template_id must be > 0.")
            data["template_id"] = template_id

        if priority_id is not None:
            if type(priority_id) not in [int, float]:
                raise TestRailValidationException("[!] priority_id must be an int or float.")
            if priority_id <= 0:
                raise TestRailValidationException("[!] priority_id must be > 0.")
            data["priority_id"] = priority_id

        if estimate is not None:
            data["estimate"] = estimate

        if milestone_id is not None:
            if type(milestone_id) not in [int, float]:
                raise TestRailValidationException("[!] milestone_id must be an int or float.")
            if milestone_id <= 0:
                raise TestRailValidationException("[!] milestone_id must be > 0.")
            data["milestone_id"] = milestone_id

        if refs is not None:
            data["refs"] = refs

        try:
            result = self.yak.test_case.add_test_case(section_id, title, data)
        except NewTestRailException as error:
            raise error
        else:
            return result

    def add_test_run(self, project_id, name):
        """Add a test run to a project.

        :param project_id: ID of the TestRail project
        :param name: name of the test case
        :return: response from TestRail API containing the newly created test run
        """
        if not project_id or project_id is None:
            raise TestRailValidationException("[!] Invalid project_id.")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float.")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0.")

        if not name or name is None:
            raise TestRailValidationException("[!] Test run name value required.")

        data = dict(name=name, include_all=True)

        try:
            result = self.yak.test_run.add_test_run(project_id, **data)
        except NewTestRailException as error:
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
            raise TestRailValidationException("[!] Invalid project_id.")

        if type(project_id) not in [int, float]:
            raise TestRailValidationException("[!] project_id must be an int or float.")

        if project_id <= 0:
            raise TestRailValidationException("[!] project_id must be > 0.")

        if not name or name is None:
            raise TestRailValidationException("[!] Test plan name value required.")

        # data = dict(name=name, include_all=True)

        try:
            result = self.yak.test_plan.add_test_plan(project_id, name)
        except NewTestRailException as error:
            raise error
        else:
            return result


class NewTestRailException(Exception):
    pass


class TestRailValidationException(ValueError):
    pass




# from vendor.testrail import APIClient
# from src.exceptions import (
#     TestRailUserException,
#     TestRailProjectException,
#     TestRailSectionException,
#     TestRailTestSuiteException,
#     TestRailTestCaseException,
#     TestRailTestRunException,
#     TestRailTestPlanException,
#     TestRailNewEntityException,
#     TestRailTestException
# )
#
# from urllib import error as E
# import time
#
#
# class TestRail:
#     """
#         Interface with the TestRail API.
#
#         Data grabbed here and methods defined here will be used in TestRailReconciler.
#     """
#
#     def __init__(self, config):
#
#         self.client             = APIClient(config["url"])
#         self.client.user        = config["user"]
#         self.client.password    = config["password"]
#         self.users              = self.get_users()
#
#     """
#         Getters
#
#         These methods grab entitles from the TestRail REST API.
#     """
#
#     def get_users(self):
#         """Get a list of TestRail users.
#
#         :return: response from TestRail API containing the user collection
#         """
#         result = None
#         try:
#             result = self.client.send_get("get_users")
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get users. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_users")
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get users.")
#         finally:
#             return result
#
#     def get_user(self, user_id):
#         """Get a TestRail user by user_id.
#
#         :param user_id: user ID of the user we want to grab
#         :return: response from TestRail API containing the user
#         """
#         if not user_id or user_id is None:
#             raise TestRailUserException("Invalid user_id")
#         result = None
#         try:
#             result = self.client.send_get("get_user/{}".format(user_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get user. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_user/{}".format(user_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get user.")
#         finally:
#             return result
#
#     def get_projects(self):
#         """Get all projects from the TestRail API."""
#         result = None
#         try:
#             result = self.client.send_get("get_projects")
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get projects. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_projects")
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get projects.")
#         finally:
#             return result
#
#     def get_project(self, project_id):
#         """Get a single project from the TestRail API by passing in its project_id.
#
#         :param project_id: project ID of the TestRail project
#         :return: response from TestRail API containing the project
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_project/{}".format(project_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get project. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_project/{}".format(project_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get project.")
#         finally:
#             return result
#
#     def get_sections(self, project_id, suite_id=None):
#         """Get a list of test sections associated with a project_id and an optional suite_id
#
#         :param project_id:
#         :param suite_id:
#         :return: response from TestRail API containing the collection of sections
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         if suite_id is not None:
#             if type(suite_id) not in [int, float]:
#                 raise TestRailTestSuiteException("suite_id must be an int or float")
#
#             if suite_id <= 0:
#                 raise TestRailTestSuiteException("suite_id must be > 0")
#
#             try:
#                 result = self.client.send_get("get_sections/{}&suite_id={}".format(project_id, suite_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get sections. Retrying")
#                 time.sleep(3)
#                 try:
#                     result = self.client.send_get("get_sections/{}&suite_id={}".format(project_id, suite_id))
#                 except E.HTTPError as httpe:
#                     print(httpe, "- Failed to get sections.")
#
#         else:
#             try:
#                 result = self.client.send_get("get_sections/{}".format(project_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get sections. Retrying")
#                 time.sleep(3)
#                 try:
#                     result = self.client.send_get("get_sections/{}".format(project_id))
#                 except E.HTTPError as httpe:
#                     print(httpe, "- Failed to get sections.")
#
#         return result
#
#     def get_section(self, section_id):
#         """Get test section from a test suite by section_id.
#
#         :param section_id: section ID to grab section from
#         :return: response from TestRail API containing the test section
#         """
#         if not section_id or section_id is None:
#             raise TestRailSectionException("Invalid section_id")
#
#         if type(section_id) not in [int, float]:
#             raise TestRailSectionException("section_id must be an int or float")
#
#         if section_id <= 0:
#             raise TestRailSectionException("section_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_section/{}".format(section_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test section by ID. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_section/{}".format(section_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test section by ID.")
#         finally:
#             return result
#
#     def get_test_suites(self, project_id):
#         """Get a list of test suites associated with a given project_id.
#
#         :param project_id: project ID of the TestRail project
#         :return: response from TestRail API containing the test suites
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_suites/{}".format(project_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test suites. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_suites/{}".format(project_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test suites.")
#         finally:
#             return result
#
#     def get_test_suite(self, suite_id):
#         """Get a test suite by suite_id.
#
#         :param suite_id: ID of the test suite
#         :return: response from TestRail API containing the test suites
#         """
#         if not suite_id or suite_id is None:
#             raise TestRailProjectException("Invalid suite_id")
#
#         if type(suite_id) not in [int, float]:
#             raise TestRailTestSuiteException("suite_id must be an int or float")
#
#         if suite_id <= 0:
#             raise TestRailTestSuiteException("suite_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_suite/{}".format(suite_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test suites. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_suite/{}".format(suite_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test suites.")
#         finally:
#             return result
#
#     def get_test_cases(self, project_id):
#         """Get a list of test cases associated with a given project_id.
#
#         :param project_id: project ID of the TestRail project
#         :return: response from TestRail API containing the test cases
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_cases/{}".format(project_id))    # wtf? [0]
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test cases. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_cases/{}".format(project_id))    # [0]
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test cases.")
#         finally:
#             return result
#
#     def get_test_case(self, case_id):
#         """Get a test case by case_id.
#
#         :param case_id: ID of the test case
#         :return: response from TestRail API containing the test cases
#         """
#         if not case_id or case_id is None:
#             raise TestRailTestCaseException("Invalid case_id")
#
#         if type(case_id) not in [int, float]:
#             raise TestRailTestCaseException("case_id must be an int or float")
#
#         if case_id <= 0:
#             raise TestRailTestCaseException("case_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_case/{}".format(case_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test case. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_case/{}".format(case_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test case.")
#         finally:
#             return result
#
#     def get_test_runs(self, project_id):
#         """Get a list of test runs associated with a given project_id.
#
#         :param project_id: project ID of the TestRail project
#         :return: response from TestRail API containing the test cases
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_runs/{}".format(project_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test runs. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_runs/{}".format(project_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test runs.")
#         finally:
#             return result
#
#     def get_test_run(self, run_id):
#         """Get a test run by run_id.
#
#         :param run_id: ID of the test run
#         :return: response from TestRail API containing the test cases
#         """
#         if not run_id or run_id is None:
#             raise TestRailTestRunException("Invalid run_id")
#
#         if type(run_id) not in [int, float]:
#             raise TestRailTestRunException("run_id must be an int or float")
#
#         if run_id <= 0:
#             raise TestRailTestRunException("run_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_run/{}".format(run_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test run. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_run/{}".format(run_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test run.")
#         finally:
#             return result
#
#     def get_test_run_tests(self, run_id):
#         """Get a collection of individual tests by run_id.
#
#         :param run_id: ID of the test run
#         :return: response from TestRail API containing the test cases
#         """
#         if not run_id or run_id is None:
#             raise TestRailTestRunException("Invalid run_id")
#
#         if type(run_id) not in [int, float]:
#             raise TestRailTestRunException("run_id must be an int or float")
#
#         if run_id <= 0:
#             raise TestRailTestRunException("run_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_tests/{}".format(run_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get tests from test run. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_tests/{}".format(run_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get tests from test run.")
#         finally:
#             return result
#
#     def get_test_run_test(self, test_id):
#         """Get an individual test.
#
#         :param test_id: ID of the individual test
#         :return: response from TestRail API containing the test
#         """
#         if not test_id or test_id is None:
#             raise TestRailTestException("Invalid test_id")
#
#         if type(test_id) not in [int, float]:
#             raise TestRailTestException("test_id must be an int or float")
#
#         if test_id <= 0:
#             raise TestRailTestException("test_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_test/{}".format(test_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get individual test. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_test/{}".format(test_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get individual test.")
#         finally:
#             return result
#
#     def get_test_plans(self, project_id):
#         """Get a list of test plans associated with a given project_id.
#
#         :param project_id: project ID of the TestRail project
#         :return: response from TestRail API containing the test cases
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_plans/{}".format(project_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test plans. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_plans/{}".format(project_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test plans.")
#         finally:
#             return result
#
#     def get_test_plan(self, plan_id):
#         """Get a test plan by plan_id.
#
#         :param plan_id: ID of the test plan
#         :return: response from TestRail API containing the test cases
#         """
#         if not plan_id or plan_id is None:
#             raise TestRailTestPlanException("Invalid plan_id")
#
#         if type(plan_id) not in [int, float]:
#             raise TestRailTestPlanException("plan_id must be an int or float")
#
#         if plan_id <= 0:
#             raise TestRailTestPlanException("plan_id must be > 0")
#
#         result = None
#         try:
#             result = self.client.send_get("get_plan/{}".format(plan_id))
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to get test plan. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_get("get_plan/{}".format(plan_id))
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to get test plan.")
#         finally:
#             return result
#
#     """
#         Setters
#
#         Use these methods to create new entitles using the TestRail REST API.
#     """
#
#     def add_project(self, name, announcement=None, show_announcement=True, suite_mode=1):
#         """Add a new project to TestRail.
#
#         :param name: name of the new TestRail project
#         :param announcement: brief description of the TestRail project
#         :param show_announcement: a truthy value or True show the announcement, a falsey value or False hides it
#         :param suite_mode: suite mode of the project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
#         :return: response from TestRail API containing the newly created project
#         """
#         if not name or name is None:
#             raise TestRailNewEntityException("Invalid project name. Unable to create new project.")
#
#         proj_data = dict(
#             name                = name,
#             announcement        = announcement,
#             show_announcement   = show_announcement,
#             suite_mode          = suite_mode
#         )
#
#         result = None
#         try:
#             result = self.client.send_post("add_project", proj_data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add project. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_project", proj_data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add project.")
#         finally:
#             return result
#
#     def add_sprint_section(self, project_id, name, description=None, suite_id=None):
#         """Add a new section representing a "sprint" to a TestRail project.
#
#         For readability, this separate method is just for adding parent sections (Jira sprints) vs child sections (Jira stories).
#
#         To populate a new child section with a Jira story, use add_story_section() and give it the id value returned here.
#
#         :param project_id: project ID of the TestRail project
#         :param name: name of the new TestRail test section
#         :param description: description of the test section
#         :param suite_id: suite ID of the test suite. This is ignored if the project is operating in single suite mode (suite_mode=1), required otherwise.
#         :return: response from TestRail API containing the newly created test section
#         """
#         if suite_id is not None:
#             raise NotImplementedError("Not currently using suite_id in this call")
#
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         if not name or name is None:
#             raise TestRailNewEntityException("Name field is required")
#
#         if not description or description is None:
#             raise TestRailNewEntityException("Description field is required")
#
#         sect_data = dict(
#             name=name,
#             description=description,
#         )
#
#         result = None
#         try:
#             result = self.client.send_post("add_section/{}".format(project_id), sect_data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add new section for the current sprint. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_section/{}".format(project_id), sect_data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add section.")
#         finally:
#             return result
#
#     def add_story_section(self, project_id, parent_id, name, description):
#         """Add a new section representing a "story" to a TestRail project.
#
#         This section will be assigned to a parent/child relationship with a parent section, thus parent_id is required.
#
#         Use the id value returned by add_sprint_section as the parent_id.
#
#         Because of this parent id requirement, no suite_id will be needed. If it is ever used in the future, add_sprint_section is the more appropriate place for it.
#
#         :param project_id: project ID of the TestRail project
#         :param name: name of the new TestRail test section
#         :param description: description of the test section
#         :param parent_id: section ID of the parent section (to build section hierarchies)
#         :return: response from TestRail API containing the newly created test section
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         if not name or name is None:
#             raise TestRailNewEntityException("Name field is required")
#
#         if not description or description is None:
#             raise TestRailNewEntityException("Description field is required")
#
#         sect_data = dict(
#             parent_id=parent_id,
#             name=name,
#             description=description,
#         )
#
#         result = None
#         try:
#             result = self.client.send_post("add_section/{}".format(project_id), sect_data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add new section for the current Jira story. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_section/{}".format(project_id), sect_data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add section.")
#         finally:
#             return result
#
#     def add_test_suite(self, project_id, name, description):
#         """Add a new test suite to a TestRail project.
#
#         :param project_id: ID of the TestRail project
#         :param name: name of the new TestRail test suite
#         :param description: description of the test suite
#         :return: response from TestRail API containing the newly created test suite
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0")
#
#         if not name or name is None:
#             raise TestRailNewEntityException("Invalid suite name. Unable to add test suite.")
#
#         if not description or description is None:
#             raise TestRailNewEntityException("Invalid description. Unable to add test suite.")
#
#         data = dict(name=name, description=description)
#
#         result = None
#         try:
#             result = self.client.send_post("add_suite/{}".format(project_id), data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add test suite. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_suite/{}".format(project_id), data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add test suite.")
#         finally:
#             return result
#
#     def add_test_case(self, section_id, title):
#         """Add a test case to a project by section_id.
#
#         :param section_id: ID of the TestRail section
#         :param title: title of the test case
#         :return: response from TestRail API containing the newly created test case
#         """
#         if not section_id or section_id is None:
#             raise TestRailSectionException("Invalid section_id.")
#
#         if type(section_id) not in [int, float]:
#             raise TestRailSectionException("section_id must be an int or float.")
#
#         if section_id <= 0:
#             raise TestRailSectionException("section_id must be > 0.")
#
#         try:
#             self.get_section(section_id)["parent_id"] is not None
#         except IndexError:
#             raise TestRailSectionException("parent_id must not be None as that would assign a test case directly to a sprint.")
#
#         if not title or title is None:
#             raise TestRailNewEntityException("Test case title required.")
#
#         data = dict(title=title)
#
#         result = None
#         try:
#             result = self.client.send_post("add_case/{}".format(section_id), data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add test case. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_case/{}".format(section_id), data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add test case.")
#         finally:
#             return result
#
#     def add_test_run(self, project_id, name):
#         """Add a test run to a project.
#
#         :param project_id: ID of the TestRail project
#         :param name: name of the test case
#         :return: response from TestRail API containing the newly created test run
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id.")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float.")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0.")
#
#         if not name or name is None:
#             raise TestRailNewEntityException("Test run name value required.")
#
#         data = dict(name=name, include_all=True)
#
#         result = None
#         try:
#             result = self.client.send_post("add_run/{}".format(project_id), data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add test run. Retrying.")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_run/{}".format(project_id), data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add test run.")
#         finally:
#             return result
#
#     def add_test_plan(self, project_id, name):
#         """Add a test plan to a project.
#
#         :param project_id: ID of the TestRail project
#         :param name: title of the test plan
#         :return: response from TestRail API containing the newly created test plan
#         """
#         if not project_id or project_id is None:
#             raise TestRailProjectException("Invalid project_id.")
#
#         if type(project_id) not in [int, float]:
#             raise TestRailProjectException("project_id must be an int or float.")
#
#         if project_id <= 0:
#             raise TestRailProjectException("project_id must be > 0.")
#
#         if not name or name is None:
#             raise TestRailNewEntityException("Test plan name value required.")
#
#         data = dict(name=name, include_all=True)
#
#         result = None
#         try:
#             result = self.client.send_post("add_plan/{}".format(project_id), data)
#         except E.HTTPError as httpe:
#             print(httpe, "- Failed to add test plan. Retrying")
#             time.sleep(3)
#             try:
#                 result = self.client.send_post("add_plan/{}".format(project_id), data)
#             except E.HTTPError as httpe:
#                 print(httpe, "- Failed to add test plan.")
#         finally:
#             return result
