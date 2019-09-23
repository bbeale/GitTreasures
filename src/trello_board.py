#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vendor.trello.trello_api import TA as TrelloApi
from src.exceptions import (
    BoardIdException,
    ListException,
    ListIdException,
    ListNameException,
    CardException,
    CardIdException,
    CardNameException,
    ChecklistIdException,
    ListIdNotSetException,
    MemberIdException,
    CardAttachmentException,
)

from util import get_configs

import os


class TrelloBoard:

    def __init__(self, config, testMode=False):
        """Initialize TrelloBoard object.

        :param config: Trello configuration settings
        :param testMode: if True, use test board JSON file. Otherwise, use Trello API
        """
        print('Initializing TrelloBoard')

        listpath = os.path.relpath(os.path.join("src", "trello_lists.ini"))
        lists = get_configs(["other", "todo", "fail", "testing", "complete"], listpath)

        self.testMode           = testMode
        self.key                = config["key"]
        self.token              = config["token"]

        if self.testMode:
            self.board_id           = config["test_board_id"]
            self.otherListId        = lists["test"]["other"]
            self.todoListId         = lists["test"]["todo"]
            self.failedListId       = lists["test"]["fail"]
            self.testingListId      = lists["test"]["testing"]
            self.completeListId     = lists["test"]["complete"]
        else:
            self.board_id           = config["board_id"]
            self.otherListId        = lists["prod"]["other"]
            self.todoListId         = lists["prod"]["todo"]
            self.failedListId       = lists["prod"]["fail"]
            self.testingListId      = lists["prod"]["testing"]
            self.completeListId     = lists["prod"]["complete"]

        self.archive_board_id   = config["archive_board_id"]

        self.trello             = TrelloApi(self.key, self.token)
        self.board              = self.getTrelloBoard(self.board_id)
        self.lists              = self.getBoardLists(self.board_id)

        self.cards              = []

        self.members            = self.getBoardMembers(self.board_id)
        self.labels             = self.getBoardLabels(self.board_id)

        self.cardCount          = 0
        self.trelloLabelsToSave = []

        self.cards              = self.getCardDetailsByList(self.lists)
        self.cardCount          = self.getCardCount(self.cards)

    # methods that "get" stuff
    def getTrelloBoard(self, board_id):
        """Given a board_id, retrieve Trello board data from API.

        :param board_id: board_id of a Trello board
        :return: JSON representatoin of a Trello baard
        """
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return self.trello.ExtendedBoards.get_decoded_board(board_id)

    def getBoardLists(self, board_id):
        """Get all lists attached to a Trello board.

        :param board_id: ID of the board to grab lists from
        :return: JSON representation of all board lists
        """
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return self.trello.ExtendedBoards.get_decoded_list(board_id)

    def getCardList(self, card_id):
        """Get the list object that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: JSON representation of the card's list
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.get_decoded_list(card_id)

    def getCardListName(self, card_id):
        """Get the list NAME that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: list name string
        """
        return self.getCardList(card_id)["name"]

    def getCardDetailsByList(self, lists):
        """Given a list of Trello lists, get data for all card on each list.

        :param lists: a list of lists to grab cards from.
        :return tmp: a list of dictionaries representing cards from lists
        """
        if lists is None:
            raise ListException("Invalid collection of lists - cannot be None")
        tmp = []
        for trello_list in lists:
            trello_cards = self.trello.ExtendedLists.get_decoded_card(trello_list['id'])
            for card in trello_cards:
                tmp.append(
                    dict(
                        listID      = trello_list['id'],
                        listName    = trello_list['name'],
                        pos         = card['pos'],
                        cardID      = card['id'],
                        cardName    = card['name'],
                        cardDesc    = card['desc'],
                        labels      = card['idLabels'],
                        members     = card['idMembers']
                    )
                )

        return tmp

    def getCard(self, card_id):
        """Get data representing a Trello card by its card_id.

        :param card_id: ID of a card whose data to return
        :return: JSON representation of the card
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.get_decoded_card(card_id)

    def getCardCount(self, cards):
        """Given a list of cards, return the count.

        :param cards: list of cards to count
        :return: number of records in cards list
        """
        if cards is None:
            raise CardException("Cards cannot be None")
        return len(list(filter(lambda card: card['listName'] != 'complete', cards)))

    def getBoardLabels(self, board_id):
        """Given a board_id, returns available labels attached to a Trello board.

        :param board_id: ID of the board to grab labels from
        :return: JSON representation of card labels
        """
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return self.trello.ExtendedBoards.get_decoded_labels(board_id)

    def getMembers(self, card_id):
        """Get members assigned to a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card members
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.get_decoded_member(card_id)

    def getBoardMembers(self, board_id):
        """Get members associated with a Trello board.

        :param board_id: a Trello board ID
        :return: JSON representation of board members
        """
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return self.trello.ExtendedBoards.get_decoded_member(board_id)

    def getAttachments(self, card_id):
        """Get attachments from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card attachments
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.get_decoded_attachment(card_id)

    def getChecklist(self, card_id):
        """Get checklist from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card checklist
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.get_decoded_checklist(card_id)

    def getChecklistItems(self, checklist_id):
        """Get items from a checklist (on a Trello card).

        :param checklist_id: ID of a checklist on a Trello card
        :return: JSON representation of card checklist items
        """
        if not checklist_id or checklist_id is None:
            raise ChecklistIdException("Invalid checklist_id")
        return [li["name"] for li in self.trello.ExtendedChecklists.get_decoded_checkItem(checklist_id, fields="name")]

    def getBoardCards(self, board_id):
        """Given a board_id, get all cards on a board.

        :param board_id: ID of a Trello board
        :return: JSON representation of Trello board complete with cards not in "Complete"
        """
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return list(filter(lambda card: card['idList'] != self.completeListId, self.trello.ExtendedBoards.get_decoded_card(board_id)))

    def getFailedList(self):
        """Get cards in the "failed" list.

        :return: JSON representation of "failed" cards
        """
        if not self.failedListId:
            raise ListIdNotSetException("Missing a value for list_id. Did this not get set?")
        failed = self.trello.ExtendedLists.get_decoded_list(self.failedListId)
        return self.trello.ExtendedLists.get_decoded_card(failed['id'])

    def getOtherPrioritiesList(self):
        """Get cards in the "other priorities" list.

        :return: JSON representation of "other priorities" cards
        """
        if not self.otherListId:
            raise ListIdNotSetException("Missing a value for list_id. Did this not get set?")
        other = self.trello.ExtendedLists.get_decoded_list(self.otherListId)
        return self.trello.ExtendedLists.get_decoded_card(other['id'])

    def getTodoList(self):
        """Get cards in the "to do" list.

        :return: JSON representation of "to do" cards
        """
        if not self.todoListId:
            raise ListIdNotSetException("Missing a value for list_id. Did this not get set?")
        todo = self.trello.ExtendedLists.get_decoded_list(self.todoListId)
        return self.trello.ExtendedLists.get_decoded_card(todo['id'])

    def getTestingList(self):
        """Get cards in the "testing" list.

        :return: JSON representation of "testing" cards
        """
        if not self.testingListId:
            raise ListIdNotSetException("Missing a value for list_id. Did this not get set?")
        testing = self.trello.ExtendedLists.get_decoded_list(self.testingListId)
        return self.trello.ExtendedLists.get_decoded_card(testing['id'])

    def getCompleteList(self):
        """Get cards in the "complete" list.

        :return: JSON representation of "complete" cards
        """
        if not self.completeListId:
            raise ListIdNotSetException("Missing a value for list_id. Did this not get set?")
        complete = self.trello.ExtendedLists.get_decoded_list(self.completeListId)
        return self.trello.ExtendedLists.get_decoded_card(complete['id'])

    def addNewCard(self, card_name, card_list_id, pos, card_desc):
        """Add a new Trello card to a list on the board.

        :param card_name: name of the new Trello card
        :param card_list_id: ID of the list where the card will go
        :param pos: position in the list (top/bottom/arithmetic)
        :param card_desc: description/content of the card
        :return:
        """
        if not card_name or card_name is None:
            raise CardException("Invalid card_name")
        if not card_list_id or card_list_id is None:
            raise CardException("Invalid card_list_id")
        if not card_desc or card_desc is None:
            raise CardException("Invalid card_desc")
        # put card on the bottom if it somehow gets in w/o pos
        if not pos or pos is None:
            pos = "bottom"
        return self.trello.ExtendedCards.new(card_name, card_list_id, pos, card_desc)

    def addNewLabel(self, card_id, name, color='orange'):
        """Add a new label to a Trello card given a card_id. Default color is orange.

        :param card_id: ID of the card to get the label
        :param name: label text. If empty, a solid label with no text will be added.
        :param color: color of the label, defaults to orange
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not name or name is None:
            raise CardNameException("Invalid card name")
        return self.trello.ExtendedCards.add_new_label(card_id, name, color)

    def addMember(self, card_id, member_id):
        """Given a cardID and a member_id of a team member, assign that member to the card.

        :param card_id: id of the card to assign the member
        :param member_id: Trello team member's Trello ID
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not member_id or member_id is None:
            raise MemberIdException("Invalid member_id")
        return self.trello.ExtendedCards.new_member(card_id, member_id)

    def addAttachment(self, card_id, url):
        """Add a new attachment located at the given URL to a Trello card.

        :param card_id: ID of the card receiving the attachment
        :param url: URL where the attachment lives
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not url or url is None:
            raise CardAttachmentException("Invalid URL")
        return self.trello.ExtendedCards.new_decoded_attachment(card_id, url)

    def addChecklist(self, card_id, name=None):
        """Add a new checklist to a Trello card.

        :param card_id: ID of the card getting the checklist
        :param name: name of the checklist. Defaults to "Checklist" or something generic
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.new_decoded_checklist(card_id, name)

    def addChecklistItem(self, card_id, checklist_id, name):
        """Add a new item to a checklist on a Trello card.

        :param card_id: ID of the card with the checklist
        :param checklist_id: ID of the checklist
        :param name: name of the new checklist item
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")

        if not checklist_id or checklist_id is None:
            raise ChecklistIdException("Invalid checklist_id")

        if self.getChecklist(card_id) is not None:
            self.trello.ExtendedChecklists.new_decoded_checkItem(checklist_id, name)

    def addNewList(self, listName, board_id):
        """Add a new list to a Trello board given a board_id.

        :param listName: name to give the new list
        :param board_id: ID of the board to add the list onto
        :return:
        """
        if not listName or listName is None:
            raise ListNameException("List needs a name")
        if not board_id or board_id is None:
            raise BoardIdException("Invalid board_id")
        return self.trello.ExtendedLists.new_decoded_list(listName, board_id)

    def clearList(self, list_id):
        """Given a list_id, archive all cards in that list.

        :param list_id: id of a Trello list
        :return:
        """
        if not list_id or list_id is None:
            raise ListIdException("Invalid list_id")
        return self.trello.ExtendedLists.archive_all_cards(list_id)

    def copyCard(self, card_id, destination_list_id=None):
        """Copy card to new list if the destination_list_id != current list_id.

        :param card_id: ID of the card to copy
        :param destination_list_id: ID of the destination list
        :return:
        """
        if not card_id or card_id is None:
            raise CardException("Must pass in a valid card")
        if not destination_list_id or destination_list_id is None:
            raise ListIdException("Invalid destination_list_id")
        self.trello.ExtendedCards.copy_card(card_id, destination_list_id)
        self.deleteCard(card_id)

    def removeMember(self, card_id, member_id):
        """Remove a member from a Trello card.

        :param card_id: ID of the card from which to remove a member
        :param member_id: ID of the member to remove
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not member_id or member_id is None:
            raise MemberIdException("Invalid member_id")
        return self.trello.ExtendedCards.delete_member_idMember(member_id, card_id)

    def moveCard(self, card_id, list_id, pos='bottom'):
        """Move a card from it's current list to the list at list_id.

        :param card_id: ID of the card to move
        :param list_id: ID of the destination list
        :param pos: position within the lis. Defaults to bottom
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not list_id or list_id is None:
            raise ListIdException("Invalid list_id")
        return self.trello.ExtendedCards.update_idList_pos(card_id, list_id, pos=pos)

    def moveCardToTop(self, card_id, list_id):
        """Move a card card_id to the top of a list list_id.

        :param card_id: ID of the card to move
        :param list_id: ID of the list to move the card into
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        if not list_id or list_id is None:
            raise ListIdException("Invalid list_id")
        return self.trello.ExtendedCards.update_idList_pos(card_id, list_id, pos='top')

    def moveCardToComplete(self, card_id):
        """Move a card to the "complete" list

        :param card_id: ID of the card to move
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.update_idList_pos(card_id, self.completeListId, pos='bottom')

    def deleteCard(self, card_id):
        """Delete a card with the given card_id.

        :param card_id: ID of the card to delete
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException("Invalid card_id")
        return self.trello.ExtendedCards.delete(card_id)

    def moveAllCardsInList(self, list_id, idBoard, idList):
        """Move all cards in a list to another list.

        :param list_id: ID of the list to move cards from
        :param idBoard: ID of the destination board
        :param idList: ID of the destination list
        :return:
        """
        if not list_id or list_id is None:
            raise ListIdException("Invalid list_id")
        if not idBoard or idBoard is None:
            raise BoardIdException("Invalid destination idBoard")
        if not idList or idList is None:
            raise ListIdException("Invalid destination idList")
        return self.trello.ExtendedLists.move_all_cards(list_id, idBoard, idList)
