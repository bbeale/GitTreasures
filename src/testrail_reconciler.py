#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import (
    ReconcileJiraBoardException,
    ReconcileJiraStoryException,
    ReconcileTrelloBoardException,
    ReconcileTrelloCardException,
    ReconcileTestRailException,
    ReconcileTestRailProjectException
)

from util import get_configs

import datetime
import sys
import os


class TestRailReconciler:

    def __init__(self, testrail, jira, trello, config):
        """Initialize the TestRailReconciler object to populate TestRail and Trello with Jira stories in need of regression testing.

        :param testrail: instance of TestRail
        :param jira: instance of JiraBoard
        :param trello: instance of TrelloBoard
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Initialization fail - missing JiraBoard instance")
        if not trello or trello is None:
            raise ReconcileTrelloBoardException("Initialization fail - missing TrelloBoard instance")

        upath = (os.path.relpath(os.path.join("src", "users.ini")))
        self.testers = [t for t in get_configs(["jira_displayname", "trello_id"], upath).values()]

        print("Grabbing stories from Jira that need regression tests...")

        self.testrail           = testrail
        self.jira               = jira
        self.trello             = trello

        self.jira_project       = self.jira_getProject()
        self.jira_board         = self.jira_getBoard()
        self.current_release    = self.jira_getCurrentSprint(self.jira_board.id)
        self.last_week          = self.jira_getStories(config["filter_last_week"])
        self.done_this_release  = self.jira_getStories(config["filter_this_release"])

        self.created_suites     = []

    def trello_labelRegressionTests(self, card):
        """Add a label to regression test card on Trello board.

        :param card: Trello card to label
        """
        if not card or card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        if card["name"] in self.trello.cards:
            self.trello.add_new_label(card["id"], "regressiontests", color="purple")

    def trello_addCard(self, card_name, list_id, desc, pos):
        """Add a card to the Trello board.

        :param card_name:
        :param list_id:
        :param desc:
        :param pos:
        :return:
        """
        return self.trello.add_new_card(card_name, list_id, desc, pos)

    def trello_populate(self):

        self.trello_checkitems = self.testrail_populateSections(self.testrail_project["id"], self.last_week)
        cardName = "{} {}".format(self.testrail_project_name, datetime.date.today().strftime("%Y-%m-%d"))
        card = next(filter(lambda c: c["name"] == cardName, [card for card in self.trello.cards]), None)

        if card is None:
            # Add the new card
            cardtext = "Weekly Regression testing for stories that have passed QA over the period of the last 7 days."
            newCard = self.trello_addCard(cardName, self.trello.otherListId, "top", cardtext)

            # Add labels to the new card
            self.trello.add_new_label(newCard["id"], "regressiontests", color="purple")

            # Add all QA testers to the new card
            for trello_testerID in [t["trello_id"] for t in self.testers if "trello_id" in t.keys()]:
                self.trello.add_new_member(newCard["id"], trello_testerID)

            # Add checklist of stories to the card
            checklist = self.trello.add_new_checklist(newCard["id"])
            for ts in self.trello_checkitems:
                self.trello.add_new_checklist_item(newCard["id"], checklist["id"], ts["name"])

        else:
            # Check for a checklist on the existing card. If it doesn't exist, add it
            checklist = self.trello.get_checklist(card["id"])
            if checklist is None or len(checklist) is 0:
                checklist = self.trello.add_new_checklist(card["id"])

            # Add stories to the checklist if they aren't already there
            for ts in self.trello_checkitems:
                if ts["name"] not in self.trello.get_checklist_items(checklist["id"]):
                    self.trello.add_new_checklist_item(card["id"], checklist["id"], ts["name"])

    # Jira methods
    def jira_getProject(self):
        """Get the current project from JiraBoard instance.

        :return: the current project if it exists, None if not
        """
        return self.jira.get_project()

    def jira_getBoard(self, key=None):
        """Get the current board from the current project on the instance.

        :param key:
        :return: the board if it exists, None if not
        """
        if key is None:
            key = self.jira.get_project()
        return self.jira.get_board(key)

    def jira_getCurrentSprint(self, board_id):
        """Get the current sprint (and probably some Moodle bullshit becasue they are too incompetent to make their own Jira project...).

        :param board_id: board ID of the Jira board
        :return: the current sprint if one exists that matches criteria
        """
        if not board_id or board_id is None:
            raise ReconcileJiraBoardException("Invalid board ID")
        return self.jira.get_current_sprint(board_id)

    def jira_getStories(self, filter_id):
        """Get a list of Jira stories given the ID of a JQL filter.

        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :return: list of stories returned by the filter
        """
        if not filter_id or filter_id is None:
            raise ReconcileJiraBoardException("Invalid filter ID")
        return self.jira.get_parsed_stories(self.jira.get_issues(filter_id))

    def jira_updateFilter(self, filter_id, query):
        """Update the query used by a JQL filter.

        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :param query: new JQL query string
        :return: JSON representation of the filter
        """
        if not filter_id or filter_id is None:
            raise ReconcileJiraBoardException("Invalid filter ID")
        if not query or query is None:
            raise ReconcileJiraBoardException("Invalid query")
        return self.jira.update_filter(filter_id, query)

    def jira_newFilter(self, name, query):
        """Create a new JQL filter.

        :param name: name of the new JQL filter
        :param query: JQL query string
        :return: JSON representation of the filter
        """
        if not name or name is None:
            raise ReconcileJiraBoardException("Invalid name")
        if not query or query is None:
            raise ReconcileJiraBoardException("Invalid query")
        return self.jira.add_new_filter(name, query)

    # TestRail methods
    def testrail_suiteExists(self, jira_key, project_id):
        """Check the existence of a test suite in TestRail (before adding a new one).

        :param jira_key:
        :param project_id:
        :return boolean: True if the test suite exists, False if not
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        if not project_id or project_id is None:
            raise ReconcileTestRailProjectException("Invalid project_id")
        test_suite  = next(filter(lambda s: jira_key.lower() in s["name"].lower(), self.testrail.get_test_suites(project_id)), None)
        return True if test_suite is not None else False

    def testrail_getProject(self, name):
        """Get a project from TestRail by name.

        :param name:
        :return: the "name" field of a TestRail project if it exists, otherwise None
        """
        if not name or name is None:
            raise ReconcileTestRailProjectException("Invalid project name")
        return next(filter(lambda p: p["name"] == name, self.testrail.get_projects()), None)

    def testrail_setProjectName(self, date):
        """Set the string representing the name of the TestRail project.

        :param date: date to use for setting a unique project name
        :return string: the project name (a formatted string)
        """
        if not date or date is None:
            raise ReconcileTestRailProjectException("Invalid date")
        return "Weekly Regression Tests {}".format(date)

    def testrail_populateSections(self, project_id, jira_stories):
        """Populate test case "sections" (or suites?) from each Jira item

        :param project_id: TestRail project_id
        :param jira_stories: Jira stories to add to TestRail
        :return list: list of items to add to TestRail
        """
        if not project_id or project_id is None:
            raise ReconcileTestRailProjectException("Invalid project_id")
        toTestRail = []
        testers = [t["jira_displayname"] for t in self.testers]
        for untested in list(filter(lambda s: s["tested_by"] in testers, jira_stories)):

            data = dict(
                project_id      = project_id,
                jira_key        = untested["jira_key"],
                name            = "{} - {}".format(untested["jira_key"], untested["jira_summary"]),
                announcement    = "{}\n\nURL:\n{}\n\nUpdated on:\n{}".format(untested["jira_desc"], untested["jira_url"], untested["jira_updated"])
            )
            toTestRail.append(data)
        return toTestRail

    def testrail_addTestPlan(self, projectID, plan_name, ):
        raise NotImplementedError

    def testrail_addToTestPlan(self, planID, item, ):
        raise NotImplementedError

    def testrail_addTestSuite(self, test_suite):
        """Add a test suite to the current project.

        :param test_suite:
        :return:
        """
        self.created_suites.append(
            self.testrail.addTestSuite(
                self.testrail_project["id"],
                test_suite["name"],
                test_suite["announcement"]
            ))

    def testrail_populateTestSuites(self, test_suites):
        """Add a list of test suites to the current project using self.testrail_addTestSuite

        :param test_suites:
        :return:
        """
        for suite in test_suites:
            if not self.testrail_suiteExists(suite["jira_key"], self.testrail_project["id"]):
                self.testrail_addTestSuite(suite)

    def testrail_populate(self):
        """Populate TestRail project and test suites.
        Steps:
            1) try to get the project name from the current Jira sprint
            2) if a project doesnt't exist by our name, create it
            3) add test sections to TestRail project
            4) add test suites to TestRail
        """
        try:
            pname = self.current_release.name.split("Sprint")[0].strip()
        except ReconcileTestRailException:
            print("current_release undefined. Unable to determine project name from TestRail.")
            sys.exit(-1)

        else:
            self.testrail_project_name = "{} Regression Tests".format(pname)
            self.testrail_project = self.testrail_getProject(self.testrail_project_name)
            if self.testrail_project is None:
                self.testrail_project = self.testrail.add_project(self.testrail_project_name)

            self.testrail_suites = self.testrail_populateSections(self.testrail_project["id"], self.done_this_release)

            self.testrail_populateTestSuites(self.testrail_suites)

    def reconcile(self):
        """Add Jira stories in need of regression tests to TestRail, and make a card with them to add to Trello."""
        self.testrail_populate()
        self.trello_populate()
