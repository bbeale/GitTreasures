#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vendor.testrail import APIClient
from src.exceptions import (
    TestRailProjectException,
    TestRailSuiteException,
    TestRailUserException,
    TestRailSectionException,
    TestRailNewEntityException,
    TestRailSuiteModeException
)

from urllib import error as E
import time


class TestRail:
    """Interface with the TestRail API. Data grabbed here and methods defined here will be used in TestRailReconciler."""

    def __init__(self, config):

        self.client             = APIClient(config["url"])
        self.client.user        = config["user"]
        self.client.password    = config["password"]
        self.users              = self.getUsers()

        self.sectionID          = None
        self.projectID          = None
        self.testCaseID         = None

    def test(self):

        self.projectID  = self.addProject(
            "Jira sprint title placeholder via treasureGit powered by TestRail API",
            "This will run every other Monday (new sprint kickoff)"
        )

        self.sectionID  = self.addSection(
            self.projectID["id"],
            "This will be a Jira key + summary",
            "And this will be a link back to the Jira issue for convenience when adding test cases."
        )

        self.testCaseID = self.addTestCase(self.sectionID["id"], "Test case placeholder", 6)
        print("...")

    def getProject(self, project_id):
        """Get a single project from the TestRail API by passing in its project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the project
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        result = None
        try:
            result = self.client.send_get("get_project/{}".format(project_id))
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get project. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_project/{}".format(project_id))
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get project.")
        finally:
            return result

    def getProjects(self):
        """Get all projects from the TestRail API."""
        result = None
        try:
            result = self.client.send_get("get_projects")
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get projects. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_projects")
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get projects.")
        finally:
            return result

    def getTestCases(self, project_id):
        """Get a list of test cases associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test cases
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        result = None
        try:
            result = self.client.send_get("get_cases/{}".format(project_id))[0]
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get test cases. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_cases/{}".format(project_id))[0]
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get test cases.")
        finally:
            return result

    def getTestSuites(self, project_id):
        """Get a list of test suites associated with a given project_id.

        :param project_id: project ID of the TestRail project
        :return: response from TestRail API containing the test suites
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        result = None
        try:
            result = self.client.send_get("get_suites/{}".format(project_id))
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get test suites. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_suites/{}".format(project_id))
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get test suites.")
        finally:
            return result

    def getSection(self, project_id, suite_id):
        """Get test section from a test suite by suite_id.

        :param project_id: project ID of the TestRail project
        :param suite_id: suite ID to grab section from
        :return: response from TestRail API containing the test section
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        if not suite_id or suite_id is None:
            raise TestRailSuiteException("Invalid suite_id")
        result = None
        try:
            result = self.client.send_get("get_sections/{}&suite_id={}".format(project_id, suite_id))
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get test sections. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_sections/{}&suite_id={}".format(project_id, suite_id))
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get test sections.")
        finally:
            return result

    def getUser(self, user_id):
        """Get a TestRail user by user_id.

        :param user_id: user ID of the user we want to grab
        :return: response from TestRail API containing the user
        """
        if not user_id or user_id is None:
            raise TestRailUserException("Invalid user_id")
        result = None
        try:
            result = self.client.send_get("get_user/{}".format(user_id))
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get user. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_user/{}".format(user_id))
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get user.")
        finally:
            return result

    def getUsers(self):
        """Get a list of TestRail users.

        :return: response from TestRail API containing the user collection
        """
        result = None
        try:
            result = self.client.send_get("get_users")
        except E.HTTPError as httpe:
            print(httpe, "- Failed to get users. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_get("get_users")
            except E.HTTPError as httpe:
                print(httpe, "- Failed to get users.")
        finally:
            return result

    def addProject(self, name, announcement=None, show_announcement=True, suite_mode=3):
        """Add a new project to TestRail.

        :param name: name of the new TestRail project
        :param announcement: brief description of the TestRail project
        :param show_announcement: a truthy value or True show the announcement, a falsey value or False hides it
        :param suite_mode: suite mode of the project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)
        :return: response from TestRail API containing the newly created project
        """
        if not name or name is None:
            raise TestRailNewEntityException("Invalid project name. Unable to create new project.")
        proj_data = dict(
            name                = name,
            announcement        = announcement,
            show_announcement   = show_announcement,
            suite_mode          = suite_mode
        )
        result = None
        try:
            result = self.client.send_post("add_project", proj_data)
        except E.HTTPError as httpe:
            print(httpe, "- Failed to add project. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_post("add_project", proj_data)
            except E.HTTPError as httpe:
                print(httpe, "- Failed to add project.")
        finally:
            return result

    def addTestSuite(self, project_id, name, description):
        """Add a new test suite to a TestRail project.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test suite
        :param description: description of the test suite
        :return: response from TestRail API containing the newly created test suite
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        if not name or name is None:
            raise TestRailNewEntityException("Invalid suite name. Unable to add test suite.")
        if not description or description is None:
            raise TestRailNewEntityException("Invalid description. Unable to add test suite.")
        data = dict(name=name, description=description)
        result = None
        try:
            result = self.client.send_post("add_suite/{}".format(project_id), data)
        except E.HTTPError as httpe:
            print(httpe, "- Failed to add test suite. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_post("add_suite/{}".format(project_id), data)
            except E.HTTPError as httpe:
                print(httpe, "- Failed to add test suite.")
        finally:
            return result

    def addSection(self, project_id, name, description, suite_id=None, parent_id=None):
        """Add a new section to a test suite.

        :param project_id: project ID of the TestRail project
        :param name: name of the new TestRail test section
        :param description: description of the test section
        :param suite_id: suite ID of the test suite. This is ignored if the project is operating in single suite mode (suite_mode=1), required otherwise.
        :param parent_id: section ID of the parent section (to build section hierarchies)
        :return: response from TestRail API containing the newly created test section
        """
        if not project_id or project_id is None:
            raise TestRailProjectException("Invalid project_id")
        if not name or name is None:
            raise TestRailNewEntityException("Invalid section name. Unable to add section.")
        if not description or description is None:
            raise TestRailNewEntityException("Invalid description. Unable to add section.")

        if self.getProject(project_id)["suite_mode"] > 1:
            if not suite_id or suite_id is None:
                raise TestRailSuiteModeException("suite_id required if test_mode > 1")
        else:
            sect_data = dict(
                name            = name,
                description     = description,
            )
            if suite_id is not None:
                sect_data["suite_id"] = suite_id
            if parent_id is not None:
                sect_data["parent_id"] = parent_id

            result = None
            try:
                result = self.client.send_post("add_section/{}".format(project_id), sect_data)
            except E.HTTPError as httpe:
                print(httpe, "- Failed to add section. Retrying")
                time.sleep(3)
                try:
                    result = self.client.send_post("add_section/{}".format(project_id), sect_data)
                except E.HTTPError as httpe:
                    print(httpe, "- Failed to add section.")
            finally:
                return result

    def addTestCase(self, section_id, title, type_id):
        """Add a test case to a project.

        :param section_id: section ID of the TestRail section
        :param title: title of the test case
        :param type_id: type_id of the test case type that is linked to the test case
        :return: response from TestRail API containing the newly created test case
        """
        if not section_id or section_id is None:
            raise TestRailSectionException("Invalid section_id")

        if not type_id or type_id is None:
            raise TestRailNewEntityException("Invalid type_id")

        test_case_data = dict(
            title           = title,
            type_id         = type_id,
        )
        result = None
        try:
            result = self.client.send_post("add_case/{}".format(section_id), test_case_data)
        except E.HTTPError as httpe:
            print(httpe, "- Failed to add test case. Retrying")
            time.sleep(3)
            try:
                result = self.client.send_post("add_case/{}".format(section_id), test_case_data)
            except E.HTTPError as httpe:
                print(httpe, "- Failed to add test case.")
        finally:
            return result
