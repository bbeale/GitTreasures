#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import (
    ListIdException,
    CardException,
    CardNameException,
    ReconcileJiraBoardException,
    ReconcileJiraStoryException,
    ReconcileGitLogException,
    ReconcileGitCommitException,
    ReconcileTrelloBoardException,
    ReconcileTrelloCardException,
    ReconcileTrelloListException,
    UpdateTrelloException
)

from util import get_configs

import sys
import os
import re


class TrelloReconciler:

    def __init__(self, jira, git, trello, config):
        """Initialize the TrelloReconciler object to reconcile the differences between git, Jira and Trello so that team members working from a Trello project board can adhere to GitFlow while putting development items through QA

        :param jira: instance of JiraBoard
        :param git: instance of GitLog
        :param trello: instance of TrelloBoard
        """
        if not jira or jira is None:
            raise ReconcileJiraBoardException("Initialization fail - missing JiraBoard instance")

        if not git or git is None:
            raise ReconcileGitLogException("Initialization fail - missing GitLog instance")

        if not trello or trello is None:
            raise ReconcileTrelloBoardException("Initialization fail - missing TrelloBoard instance")

        print("Instantiating TrelloReconciler object")

        # Tester credentials import
        upath = (os.path.relpath(os.path.join("src", "users.ini")))
        self.testers = [t for t in get_configs(["jira_displayname", "trello_id"], upath).values()]

        self.jira                   = jira
        self.git                    = git
        self.trello                 = trello
        self.jira_key_pattern       = config["jira_pattern"]
        self.filter_qa_status       = config["filter_qa_status"]
        self.filter_qa_ready        = config["filter_qa_ready"]
        self.jira_qa_statuses       = self.jira.get_parsed_stories(self.jira.get_issues(self.filter_qa_status))
        self.jira_qa_ready          = self.jira.get_parsed_stories(self.jira.get_issues(self.filter_qa_ready))
        self.staging_commits        = self.git.commits
        self.trello_labels          = self.trello.labels
        self.failed_listID          = self.trello.failedListId
        self.other_listID           = self.trello.otherListId
        self.todo_listID            = self.trello.todoListId
        self.testing_listID         = self.trello.testingListId
        self.complete_listID        = self.trello.completeListId
        self._old_complete_names    = []
        self._old_card_names        = []
        self.old_qa_ready_cards     = []
        self.new_cards              = []
        self._changed               = []
        self._last_card_pos         = None

    # Trello methods
    def trello_getOldFailed(self):
        """Get a list of pre-reconcile Trello cards currently in the "Failed" list.

        :return list: Trello cards in the "Failed" list
        """
        return self.trello.get_cards_from_list(self.failed_listID)

    def trello_getOldOtherPriorities(self):
        """Get a list of pre-reconcile Trello cards currently in the "Other Priorities" list.

        :return list: Trello cards in the "Other Priorities" list
        """
        return self.trello.get_cards_from_list(self.other_listID)

    def trello_getOldTodo(self):
        """Get a list of pre-reconcile Trello cards currently in the "To do" list.

        :return list: Trello cards in the "To do" list
        """
        return self.trello.get_cards_from_list(self.todo_listID)

    def trello_getOldTesting(self):
        """Get a list of pre-reconcile Trello cards currently in the "Testing" list.

        :return list: Trello cards in the "Testing" list
        """
        return self.trello.get_cards_from_list(self.testing_listID)

    def trello_getOldComplete(self):
        """Get a list of pre-reconcile Trello cards currently in the "Complete" list.

        :return list: Trello cards in the "Complete" list
        """
        return self.trello.get_cards_from_list(self.complete_listID)

    def trello_addCardLabel(self, card_id, label, color=None):
        """Add an individual label to a Trello card given its card_id.

        :param card_id:
        :param label:
        :param color:
        :return:
        """
        if not card_id or card_id is None:
            raise ReconcileTrelloCardException("Invalid card_id")

        if not label or label is None:
            raise ReconcileTrelloCardException("Invalid label")

        if color is not None:
            return self.trello.add_new_label(card_id, label, color=color)
        else:
            return self.trello.add_new_label(card_id, label)

    def trello_addCardLabels(self, trello_card, trello_labels):
        """Add records in in trello_labels to Trello card.

        :param trello_card: card to add labels to
        :param trello_labels: list of trello labels
        :return: response containing a collection of newly labeled cards
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")

        if self.jira.is_hotfix(trello_card["name"]):
            self.trello_addCardLabel(trello_card["id"], "hotfix", color="red")

        commit = next(filter(lambda c: trello_card["name"] in c["commitMessage"], self.staging_commits), None)

        if commit is not None:
            if self.jira_isStagingStory(trello_card["name"], commit["commitMessage"]):
                self.trello_addCardLabel(trello_card["id"], "staging", color="green")

        for label in trello_labels:
            if label.lower() != "hotfix":
                self.trello_addCardLabel(trello_card["id"], label)

    def trello_addCardMembers(self, card_id, tested_by):
        """Add Trello member to Trello card.

        The Trello member should represent the QA tester who worked on the story.

        :param card_id: the ID of a Trello card
        :param tested_by: tester name used to determine QA ownership of tickets
        """
        if not card_id or card_id is None:
            raise ReconcileTrelloCardException("Invalid card_id")

        trello_testerID = None

        for tester in self.testers:
            if tested_by == tester["jira_displayname"]:
                if "trello_id" in tester.keys():
                    trello_testerID = tester["trello_id"]

        if trello_testerID is not None and tested_by is not "unassigned":
            self.trello.add_new_member(card_id, trello_testerID)

    def trello_addCardAttachments(self, card_id, jira_attachments):
        """Add attachment items to a Trello card.

        :param card_id: the ID of a Trello card
        :param jira_attachments: list of attachment URLs grabbed from the Jira story
        """
        if not card_id or card_id is None:
            raise ReconcileTrelloCardException("Invalid card_id")


        for attachment in jira_attachments:
            self.trello.add_new_attachment(card_id, attachment)

    def trello_isCurrentlyFailed(self, trello_card):
        """Check the failure status of a Trello card.

        :param trello_card: Trello card to check the failure state of
        :return boolean:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        return self.jira.is_currently_failed(trello_card["name"]) and trello_card["listID"] != self.failed_listID

    def trello_isStaleQaReady(self, trello_card):
        """Check if a Trello card HAS previously failed QA.

        :param trello_card: Trello card to check the QA ready state of
        :return boolean:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        return self.jira_isStaleQAReady(trello_card["name"]) and (
                trello_card["listID"] != self.todo_listID and
                trello_card["listID"] != self.testing_listID
        )

    def trello_isInQaTesting(self, trello_card):
        """Check if a Trello card is currently in QA.

        :param trello_card: Trello card to check the QA testing state of
        :return:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        return self.jira_isInQaTesting(trello_card["name"]) and trello_card["listID"] != self.testing_listID

    def trello_passedQA(self, trello_card):
        """Check if a card has passed QA.

        :param trello_card: Trello card to check the QA testing state of
        :return:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        return self.jira_passedQA(trello_card["name"]) and trello_card["listID"] != self.complete_listID

    def trello_addCard(self, name, list_id, pos, desc):
        """Add a new card to the Trello board using TrelloBoard instance method.

        :param name: name of the new card
        :param list_id: Trello list ID of the new card's destination list
        :param pos: list position - defaults to "bottom" if none is found
        :param desc: card description
        :return:
        """
        if not name or name is None:
            raise CardNameException("Invalid new card name")
        if not list_id or list_id is None:
            raise ListIdException("Invalid list_id")
        if not desc or desc is None:
            raise CardException("Description must be set and cannot be None")
        if not pos or pos is None:
            pos = "bottom"
        return self.trello.add_new_card(name, list_id, pos, desc)

    def trello_deleteCard(self, trello_card):
        """Delete a Trello card.

        :param trello_card: Trello card to check the QA testing state of
        :return:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        self._changed.append(trello_card["name"])
        return self.trello.delete_card(trello_card["id"])

    def trello_copyCard(self, trello_card, destination_list_id):
        """Copy a Trello card to a new list.

        :param trello_card: Trello card to check the QA testing state of
        :param destination_list_id: list_id receiving the card copy
        :return:
        """
        if not trello_card or trello_card is None:
            raise ReconcileTrelloCardException("Invalid Trello card")
        if not destination_list_id or destination_list_id is None:
            raise ReconcileTrelloListException("Invalid destination list_id")
        if trello_card["listID"] == destination_list_id:
            raise ReconcileTrelloListException("Copy would go to the same list")
        self._changed.append(trello_card["name"])
        return self.trello.copy_card(trello_card["id"], destination_list_id)

    def trello_updateCurrentCards(self):
        """Update existing Trello cards if the state of the Jira stories they represent has changed."""
        print("Checking for existing card updates...")
        cardList = list(filter(lambda t: "{}-".format(self.jira.project_key) in t["name"] and t["listID"] in [self.other_listID, self.todo_listID, self.failed_listID, self.testing_listID], self.trello.cards))
        for card in cardList:

            jira    = next(filter(lambda j: j["jira_key"] == card["name"], self.jira_qa_statuses), None)
            if jira is None:
                continue    # Keep failed card on the board, even though this could also keep complete

            member  = next(filter(lambda t: jira and jira["tested_by"] == t, self.testers), None)
            if member is not None and len(card["members"]) == 0:
                self.trello_addCardMembers(card["id"], member)

            commit = next(filter(lambda c: jira["jira_key"] in c["commitMessage"], self.staging_commits), None)
            if commit and commit is not None and self.jira_isStagingStory(jira["jira_key"], commit["commitMessage"]):

                jira["last_known_commit_date"] = commit["committerDate"]
                jira["git_commit_message"] = commit["commitMessage"]
                jira["in_staging"] = True

            jira_labels = self.jira_getLabels(card["name"])
            if len(jira_labels) > len(card["labels"]):
                self.trello_addCardLabels(card, jira_labels)

            if self.trello_isCurrentlyFailed(card):
                self.trello_copyCard(card, self.failed_listID)
                continue

            if self.trello_isStaleQaReady(card):
                self.trello_copyCard(card, self.todo_listID)
                continue

            if self.trello_isInQaTesting(card):
                self.trello_copyCard(card, self.testing_listID)
                continue

            if self.trello_passedQA(card):
                self.trello_copyCard(card, self.complete_listID)
                continue

    def trello_getOldLists(self):
        """Generate a list of previously existing cards before reconciling.

        This list will be used to check if incoming Jira stories have already made it into the Trello QA process.

        :return list: a list of card names that were on the board prior to reconciling
        """
        self.old_qa_ready_cards = self.trello_getOldTodo()

        to_names        = [s["name"] for s in self.old_qa_ready_cards]
        f_names         = [f["name"] for f in self.trello_getOldFailed()]
        op_names        = [h["name"] for h in self.trello_getOldOtherPriorities()]
        te_names        = [o["name"] for o in self.trello_getOldTesting()]
        complete_names  = [c["name"] for c in self.trello_getOldComplete()]

        return list(
            set(f_names + op_names + to_names + te_names + complete_names))

    def trello_archiveComplete(self):
        """If the number of cards in "Complete" is >= 10, move all cards to the archive board ("QA Complete" on Trello).

        Lists on QA Complete are labeled by sprint.
            - If Complete has >= 10 cards and QA complete does not have a list for the current sprint, create it and add the Complete cards to it.
            - Otherwise, find the list covering the current sprint and append the Complete cards.
        """
        completeCount = len(self.trello_getOldComplete())

        if completeCount >= 10:
            # 1) get current sprint name
            currentSprintName = self.jira.current_sprint.name.replace(" ", "_") + "_archive"

            # 2) get the names and listIDs of existing lists on archive board
            listTuples = [(ln["name"], ln["id"]) for ln in self.trello.get_trello_lists(self.trello.archive_board_id)]
            listNames = [ln[0] for ln in listTuples]

            # 3) if the list doesn't exist, create it and grab it's listID
            if currentSprintName not in listNames:
                archiveBoardList = self.trello.add_new_list(currentSprintName, self.trello.archive_board_id)
                target_listID = archiveBoardList["id"]

            # 4) otherwise, grab it's existing listID
            else:
                archiveBoardList = next(filter(lambda lt: lt[0] == currentSprintName, listTuples), None)
                target_listID = archiveBoardList[1]

            self.trello.move_all_cards_in_list(self.trello.completeListId, self.trello.archive_board_id, target_listID)

    def trello_setNewLists(self, new_stories):
        """Parse new Jira stories and add them to a list of new Trello cards

        :param new_stories: Jira stories to loop through to see if we need to make Trello cards
        """
        jira_stories = [story for story in sorted(new_stories, key=lambda story: story["jira_qa_date"]) if
                        story["jira_key"] not in self._old_card_names]

        for story in jira_stories:
            # shouldn't happen by this point, but just in case...
            if self.jira_passedQA(story["jira_key"]):
                self.trello_addToList(story, self.complete_listID, self.new_cards)
                continue

            if self.jira_isInQaTesting(story["jira_key"]):
                self.trello_addToList(story, self.testing_listID, self.new_cards)
                continue

            if self.jira_isFreshHotfix(story["jira_key"]):
                self.trello_addToList(story, self.other_listID, self.new_cards)
                continue

            if self.jira_isStaleHotfix(story["jira_key"]):
                self.trello_addToList(story, self.todo_listID, self.new_cards, top_of_list=True)
                continue

            if self.jira_isFreshQaReady(story["jira_key"]):
                self.trello_addToList(story, self.todo_listID, self.new_cards)
                continue

            if self.jira_isStaleQAReady(story["jira_key"]):
                self.trello_addToList(story, self.todo_listID, self.new_cards, top_of_list=True)
                continue

            commit = next(filter(lambda c: story["jira_key"] in c["commitMessage"], self.staging_commits), None)
            if commit and commit is not None:
                if self.jira_isStagingStory(story["jira_key"], commit["commitMessage"]):
                    story["last_known_commit_date"] = commit["committerDate"]
                    story["git_commit_message"] = commit["commitMessage"]
                    story["in_staging"] = True

                    self.trello_addToList(story, self.todo_listID, self.new_cards, commit_date=commit["committerDate"])
                    continue

            if self.jira_isOtherItem(story["jira_key"]):
                self.trello_addToList(story, self.todo_listID, self.new_cards)

    def trello_addToList(self, jira_story, trello_listId, trello_list, top_of_list=False, commit_date=None):
        """Add an individual story's data to a list of card to add to Trello.

        :param jira_story: Jira story object to make a Trello card from
        :param trello_listId: list_id of a Trello list getting the new card
        :param trello_list: list of data from which to make Trello cards
        :param top_of_list: if True, put the new card at the top of the list
        :param commit_date: date that a commit mentioning jira_story was made to staging
            - this will be used for sorting
            - if the value is None, use the date that the story was moved to QA in Jira
        """
        if not jira_story or jira_story is None:
            raise ReconcileJiraStoryException("No Jira story to add")

        if not trello_listId or trello_listId is None:
            raise ReconcileTrelloListException("Invalid Trello list ID")

        if trello_list is None:
            raise ReconcileTrelloListException("Getting rid of the trello_list arg in this method soon... Stay tuned.")

        if commit_date and commit_date is not None:
            sort_date = commit_date

        else:
            sort_date = jira_story["jira_qa_date"]

        if top_of_list or jira_story["has_failed"]:
            list_position = "top"

        else:
            list_position = "bottom"

        card = dict(
            pos                 = list_position,
            jira_key            = jira_story["jira_key"],
            trello_listID       = trello_listId,
            date                = sort_date,
            jira_url            = jira_story["jira_url"],
            jira_summary        = jira_story["jira_summary"],
            jira_desc           = jira_story["jira_desc"],
            comments            = jira_story["comments"],
            labels              = jira_story["labels"],
            tested_by           = jira_story["tested_by"],
            current_status      = jira_story["current_status"],
            has_failed          = jira_story["has_failed"],
            statuses            = jira_story["statuses"],
            jira_attachments    = jira_story["attachments"]
        )

        self.new_cards.append(card)
        self.jira_qa_statuses.remove(jira_story)

    def trello_addCardsToBoard(self):
        """Actually add cards from the new card list to the Trello board"""
        old_qa_ready    = [li["name"] for li in self.old_qa_ready_cards]
        new_qa_ready    = [li["jira_key"] for li in self.jira.get_parsed_stories(self.jira.get_issues(self.filter_qa_ready)) if not self.jira_isHotfix(li["jira_key"])]

        for card in self.new_cards:
            if card["jira_key"] not in self._old_card_names:

                current_index   = 0
                prev_index      = None

                if card["trello_listID"] == self.todo_listID:
                    # Attempting incrementing current to account for the new pos it should be in
                    current_index   = new_qa_ready.index(card["jira_key"]) + 1
                    prev_index      = current_index - 1

                if prev_index is None or prev_index < 0:
                    card["pos"]    = "top"

                if card["pos"] != "top" and 0 <= prev_index < (len(old_qa_ready) - 1):
                    prev_t_pos  = self.old_qa_ready_cards[prev_index]["pos"]
                    next_t_pos  = self.old_qa_ready_cards[prev_index + 1]["pos"]
                    pos_incr = (next_t_pos - prev_t_pos) / 2

                    self._last_card_pos = prev_t_pos + pos_incr

                    card["pos"]    = self._last_card_pos

                desc = "**{}**\n\n**Ready for QA on:** {}\n**Original Jira link:** {}\n\n---\n\n{}\n\n---\n\nJIRA COMMENTS\n\n{}\n\n---\n\nJIRA STATUS CHANGES\n\n{}".format(
                            card["jira_summary"],
                            card["date"],
                            card["jira_url"],
                            card["jira_desc"],
                            card["comments"],
                            card["statuses"]
                )

                if len(desc) > 16384:
                    desc = "**{}**\n\n**Ready for QA on:** {}\n**Original Jira link:** {}\n\n---\n\n{}\n\n---\n\nJIRA COMMENTS\n\n{}\n\n---\n\nJIRA STATUS CHANGES\n\n{}".format(
                        card["jira_summary"],
                        card["date"],
                        card["jira_url"],
                        card["jira_desc"],
                        "Too much text -- see Jira story",
                        "Too much text -- see Jira story"
                    )

                try:
                    newcard = self.trello_addCard(card["jira_key"], card["trello_listID"], card["pos"], desc)

                except UpdateTrelloException as e:
                    e.msg = "Unable to add a new card to the Trello board"
                    print(e.msg)
                    sys.exit(-1)

                else:
                    if card["trello_listID"] == self.todo_listID:
                        old_qa_ready.insert(current_index, newcard["name"])
                        self.old_qa_ready_cards.insert(current_index, newcard)

                    self.trello_addCardMembers(newcard["id"], card["tested_by"])
                    self.trello_addCardLabels(newcard, card["labels"])
                    self.trello_addCardAttachments(newcard["id"], card["jira_attachments"])

    # Jira methods
    def jira_getStories(self, jira, filterID):
        raise NotImplementedError

    def jira_getLabels(self, jira_key):
        """ Get Jira defined labels from a story.

        :param jira_key: Jira story key to get the labels from
        :return:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.get_labels(jira_key)

    def jira_initializeData(self):
        raise NotImplementedError

    def jira_isHotfix(self, jira_key):
        """Return True if item is a hotfix.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.is_hotfix(jira_key)

    def jira_isFreshHotfix(self, jira_key):
        """Return True if item is a hotfix, is ready for QA, and has NOT previously failed testing.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira_isHotfix(jira_key) and self.jira_isFreshQaReady(jira_key)

    def jira_isStaleHotfix(self, jira_key):
        """Return True if item is a hotfix, is ready for QA and HAS previously failed testing.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira_isHotfix(jira_key) and self.jira_isStaleQAReady(jira_key)

    def jira_isFreshQaReady(self, jira_key):
        """Return True if item is ready for QA, and has NOT previously failed testing.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.is_fresh_qa_ready(jira_key)

    def jira_isStaleQAReady(self, jira_key):
        """Return True if item is ready for QA and HAS previously failed testing.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.is_stale_qa_ready(jira_key)

    def jira_keyInCommitMesssage(self, jira_key, commit_message):
        """Return True if a commit message is found with the Jira key. This is used to indicate commits with work done pertaining to development stories.

        :param jira_key: jira_key of the story we want to check
        :param commit_message: message attached to the commit we want to look at
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        if not commit_message or commit_message is None:
            raise ReconcileGitCommitException("Invalid commit message")
        return jira_key in [a.strip("[]") for a in re.findall(self.jira_key_pattern, commit_message)]

    def jira_isStagingStory(self, jira_key, commit_message):
        """Return True if Jira key is found in a commit message. This indicates that the branch we are watching (in this case staging, but that can be non-hardcoded) contains a commit with work pertaining to a given story.

        :param jira_key: jira_key of the story we want to check
        :param commit_message: message attached to the commit we want to look at
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        if not commit_message or commit_message is None:
            raise ReconcileGitCommitException("Invalid commit message")
        return self.jira_keyInCommitMesssage(jira_key, commit_message)

    def jira_isInQaTesting(self, jira_key):
        """Return true if story has a Jira status of QA Testing.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.is_in_qa_testing(jira_key)

    def jira_passedQA(self, jira_key):
        """Return true if story has passed QA.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return self.jira.passed_qa(jira_key)

    def jira_isOtherItem(self, jira_key):
        """Final check to see if story should go to Trello. Make sure story was nowhere on Trello board prior to reconciling.

        :param jira_key: jira_key of the story we want to check
        :return boolean:
        """
        if not jira_key or jira_key is None:
            raise ReconcileJiraStoryException("Invalid jira_key")
        return jira_key not in self._old_card_names

    def reconcile(self):
        """Any class named reconciler needs a reconcile method.
        Steps:
            1) update the existing Trello cards
            2) get a list of the existing card names
            3) move "Complete" cards to archive board if list length >= 10
            4) create list of new Trello cards to make
            5) add the new Trello cards from the new card list to the board
        """
        self.trello_updateCurrentCards()
        self._old_card_names = self.trello_getOldLists()

        self.trello_archiveComplete()

        self.trello_setNewLists(self.jira_qa_statuses)
        self.new_cards = sorted(self.new_cards, key=lambda c: c["date"])

        self.trello_addCardsToBoard()
