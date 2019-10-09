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

        # self.testers            = [Scott, Ben, Ranjeetha, Sandhya]
        self.testrail           = testrail
        self.jira               = jira
        self.trello             = trello

        self.jira_project       = self.jira_getProject(self.jira)
        self.jira_board         = self.jira_getBoard(self.jira)
        self.current_release    = self.jira_getCurrentSprint(self.jira, self.jira_board.id)
        self.last_week          = self.jira_getStories(self.jira, config["filter_last_week"])
        self.done_this_release  = self.jira_getStories(self.jira, config["filter_this_release"])

        self.created_suites     = []

        try:
            pname = self.current_release.name.split("Sprint")[0].strip()
            self.testrail_project_name = "{} Regression Tests".format(pname)
        except ReconcileTestRailException as e:
            e.msg = "current_release undefined. Unable to determine project name from TestRail."
            print(e.msg)
            sys.exit(-1)

        self.testrail_project = self.testrail_getProject(self.testrail_project_name)

    def trello_labelRegressionTests(self, card):
        """Add a label to regression test card on Trello board.

        :param card: Trello card to label
        """
        if not card or card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        if card["name"] in self.trello.cards:
            self.trello.add_new_label(card["id"], "regressiontests", color="purple")

    # Jira methods
    def jira_getProject(self, jira):
        """Get the current project from JiraBoard instance.

        :param jira:
        :return: the current project if it exists, None if not
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        return jira.getProject()

    def jira_getBoard(self, jira, key=None):
        """Get the current board from the current project on the instance.

        :param jira:
        :param key:
        :return: the board if it exists, None if not
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        if key is None:
            key = jira.getProject()
        return jira.getBoard(key)

    def jira_getCurrentSprint(self, jira, board_id):
        """Get the current sprint (and probably some Moodle bullshit becasue they are too incompetent to make their own Jira project...).

        :param jira:
        :param board_id: board ID of the Jira board
        :return: the current sprint if one exists that matches criteria
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        if not board_id or board_id is None:
            raise ReconcileJiraBoardException("Invalid board ID")
        return jira.getCurrentSprint(board_id)

    def jira_getStories(self, jira, filter_id):
        """Get a list of Jira stories given the ID of a JQL filter.

        :param jira:
        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :return: list of stories returned by the filter
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        if not filter_id or filter_id is None:
            raise ReconcileJiraBoardException("Invalid filter ID")
        return jira.getParsedStories(jira.getStories(filter_id))

    def jira_updateFilter(self, jira, filter_id, query):
        """Update the query used by a JQL filter.

        :param jira:
        :param filter_id: filter ID of the JQL filter (defined in Jira)
        :param query: new JQL query string
        :return: JSON representation of the filter
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        if not filter_id or filter_id is None:
            raise ReconcileJiraBoardException("Invalid filter ID")
        if not query or query is None:
            raise ReconcileJiraBoardException("Invalid query")
        return jira.updateFilter(filter_id, query)

    def jira_newFilter(self, jira, name, query):
        """Create a new JQL filter.

        :param jira:
        :param name: name of the new JQL filter
        :param query: JQL query string
        :return: JSON representation of the filter
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Invalid JiraBoard object")
        if not name or name is None:
            raise ReconcileJiraBoardException("Invalid name")
        if not query or query is None:
            raise ReconcileJiraBoardException("Invalid query")
        return jira.addNewFilter(name, query)

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
        test_suite  = next(filter(lambda s: jira_key.lower() in s["name"].lower(), self.testrail.getTestSuites(project_id)), None)
        return True if test_suite is not None else False

    def testrail_getProject(self, name):
        """Get a project from TestRail by name.

        :param name:
        :return: the "name" field of a TestRail project if it exists, otherwise None
        """
        if not name or name is None:
            raise ReconcileTestRailProjectException("Invalid project name")
        return next(filter(lambda p: p["name"] == name, self.testrail.getProjects()), None)

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

    def reconcile(self):
        """Add Jira stories in need of regression tests to TestRail, and make a card with them to add to Trello."""
        # TestRail
        if self.testrail_project is None:
            self.testrail_project = self.testrail.addProject(self.testrail_project_name)

        self.testrail_suites = self.testrail_populateSections(self.testrail_project["id"], self.done_this_release)

        for ts in self.testrail_suites:
            if not self.testrail_suiteExists(ts["jira_key"], self.testrail_project["id"]):

                self.created_suites.append(
                    self.testrail.addTestSuite(
                        self.testrail_project["id"],
                        ts["name"],
                        ts["announcement"]
                    ))

        # Trello
        self.trello_checkitems = self.testrail_populateSections(self.testrail_project["id"], self.last_week)
        cardName = "{} {}".format(self.testrail_project_name, datetime.date.today().strftime("%Y-%m-%d"))
        card = next(filter(lambda c: c["name"] == cardName, [card for card in self.trello.cards]), None)

        if card is None:

            newCard = self.trello.add_new_card(cardName, self.trello.otherListId, "top",
                                             "Weekly Regression testing for stories that have passed QA over the period of the last 7 days.")


            self.trello.add_new_label(newCard["id"], "regressiontests", color="purple")

            for trello_testerID in [t["trello_id"] for t in self.testers if "trello_id" in t.keys()]:
                self.trello.add_new_member(newCard["id"], trello_testerID)

            checklist = self.trello.add_new_checklist(newCard["id"])
            for ts in self.trello_checkitems:
                self.trello.add_new_checklist_item(newCard["id"], checklist["id"], ts["name"])

        else:
            checklist = self.trello.get_checklist(card["id"])
            if checklist is None or len(checklist) is 0:
                checklist = self.trello.add_new_checklist(card["id"])

            for ts in self.trello_checkitems:
                if ts["name"] not in self.trello.get_checklist_items(checklist["id"]):
                    self.trello.add_new_checklist_item(card["id"], checklist["id"], ts["name"])

        print("\tDone")
