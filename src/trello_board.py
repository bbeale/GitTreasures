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
    MemberIdException,
    CardAttachmentException,
)

from util import get_configs

from requests.exceptions import HTTPError

import sys
import os


class TrelloBoard:

    def __init__(self, config, testMode=False):
        """Initialize TrelloBoard object.

        :param config: Trello configuration settings
        :param testMode: if True, use test board JSON file. Otherwise, use Trello API
        """
        print('[+] Initializing TrelloBoard')

        if not config or config is None:
            raise ValueError('[!] Invalid configs')

        listpath = os.path.relpath(os.path.join('src', 'trello_lists.ini'))
        lists = get_configs(['other', 'todo', 'fail', 'testing', 'complete'], listpath)

        self.testMode           = testMode
        self.key                = config['key']
        self.token              = config['token']

        if self.testMode:
            self.board_id           = config['test_board_id']
            self.otherListId        = lists['test']['other']
            self.todoListId         = lists['test']['todo']
            self.failedListId       = lists['test']['fail']
            self.testingListId      = lists['test']['testing']
            self.completeListId     = lists['test']['complete']
        else:
            self.board_id           = config['board_id']
            self.otherListId        = lists['prod']['other']
            self.todoListId         = lists['prod']['todo']
            self.failedListId       = lists['prod']['fail']
            self.testingListId      = lists['prod']['testing']
            self.completeListId     = lists['prod']['complete']

        self.archive_board_id   = config['archive_board_id']
        self.cards              = []
        self.cardCount          = 0
        self.trelloLabelsToSave = []

        self.trello             = TrelloApi(self.key, self.token)
        self.board              = None
        self.lists              = None
        self.labels             = None
        self.members            = None

    # methods that 'get' stuff
    def get_trello_board(self, board_id):
        """Given a board_id, retrieve Trello board data from API.

        :param board_id: board_id of a Trello board
        :return: JSON representatoin of a Trello baard
        """
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        result = None
        try:
            result = self.trello.ExtendedBoards.get_decoded_board(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get Trello board.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedBoards.get_decoded_board(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get Trello board.')
        finally:
            return result

    def get_trello_lists(self, board_id):
        """Get all lists attached to a Trello board.

        :param board_id: ID of the board to grab lists from
        :return: JSON representation of all board lists
        """
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        result = None
        try:
            result = self.trello.ExtendedBoards.get_decoded_list(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get Trello lists.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedBoards.get_decoded_list(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get Trello lists.')
        finally:
            return result

    def get_board_labels(self, board_id):
        """Given a board_id, returns available labels attached to a Trello board.

        :param board_id: ID of the board to grab labels from
        :return: JSON representation of card labels
        """
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        result = None
        try:
            result = self.trello.ExtendedBoards.get_decoded_labels(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get board-level labels.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedBoards.get_decoded_labels(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get labels.')
        finally:
            return result

    def get_board_members(self, board_id):
        """Get members associated with a Trello board.

        :param board_id: a Trello board ID
        :return: JSON representation of board members
        """
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        result = None
        try:
            result = self.trello.ExtendedBoards.get_decoded_member(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get board-level members.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedBoards.get_decoded_member(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get members.')
        finally:
            return result

    def get_card_members(self, card_id):
        """Get members assigned to a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card members
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        result = None
        try:
            result = self.trello.ExtendedCards.get_decoded_member(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get card-level members.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedCards.get_decoded_member(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get members.')
        finally:
            return result

    def get_trello_card_list(self, card_id):
        """Get the list object that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: JSON representation of the card's list
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        result = None
        try:
            result = self.trello.ExtendedCards.get_decoded_list(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get list containing given card_id.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedCards.get_decoded_list(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get list.')
        finally:
            return result

    def get_trello_card_list_name(self, card_id):
        """Get the list NAME that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: list name string
        """
        card_id_list = self.get_trello_card_list(card_id)
        return card_id_list['name'] if card_id_list is not None else None

    def get_cards_from_lists(self, lists):
        """Given a list of Trello lists, get data for all card on each list.

        :param lists: a list of lists to grab cards from.
        :return tmp: a list of dictionaries representing cards from lists
        """
        if lists is None:
            raise ListException('[!] Invalid collection of lists - cannot be None')
        tmp = []
        for trello_list in lists:
            trello_cards = self.get_cards_from_list(trello_list['id'])
            # check if trello_cards is None or zero before trying to add them to tmp
            if len(trello_cards) > 0:
                for card in trello_cards:
                    tmp.append(
                        dict(
                            listID      = trello_list['id'],
                            listName    = trello_list['name'],
                            pos         = card['pos'],
                            id          = card['id'],
                            name        = card['name'],
                            cardDesc    = card['desc'],
                            labels      = card['idLabels'],
                            members     = card['idMembers']
                        )
                    )

        return tmp

    def get_cards_from_list(self, list_id):
        """ Given a Trello list_ID, get data for all card on that list.

        :param list_id:
        :return:
        """
        if not list_id or list_id is None:
            raise ListIdException('[!] Invalid list_id')
        cards = []
        try:
            cards = self.trello.ExtendedLists.get_decoded_card(list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get cards from list.\nRetrying in a few seconds.')
            try:
                cards = self.trello.ExtendedLists.get_decoded_card(list_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Could not get all cards from list.\nReturning what we have.')
        finally:
            return cards

    def get_card(self, card_id):
        """Get data representing a Trello card by its card_id.

        :param card_id: ID of a card whose data to return
        :return: JSON representation of the card
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        result = None
        try:
            result = self.trello.ExtendedCards.get_decoded_card(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to find a card with given card_id.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedCards.get_decoded_card(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get card.')
        finally:
            return result

    def get_card_count(self, cards):
        """Given a list of cards, return the count.

        :param cards: list of cards to count
        :return: number of records in cards list
        """
        if cards is None:
            raise CardException('[!] Cards cannot be None')
        if len(cards) is 0:
            return 0
        return len(list(filter(lambda card: card['listName'] != 'complete', cards)))

    def get_attachments(self, card_id):
        """Get attachments from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card attachments
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        result = None
        try:
            result = self.trello.ExtendedCards.get_decoded_attachment(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get attachments from given card_id.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedCards.get_decoded_attachment(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get attachments.')
        finally:
            return result

    def get_checklist(self, card_id):
        """Get checklist from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card checklist
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        result = None
        try:
            result = self.trello.ExtendedCards.get_decoded_checklist(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get checklist from given card_id.\nRetrying in a few seconds.')
            try:
                result = self.trello.ExtendedCards.get_decoded_checklist(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get checklist.')
        finally:
            return result   # if len(result) is not 0 else None

    def get_checklist_items(self, checklist_id):
        """Get items from a checklist (on a Trello card).

        :param checklist_id: ID of a checklist on a Trello card
        :return: JSON representation of card checklist items
        """
        if not checklist_id or checklist_id is None:
            raise ChecklistIdException('[!] Invalid checklist_id')

        checklist_items = []
        try:
            checklist_items = self.trello.ExtendedChecklists.get_decoded_checkItem(checklist_id, fields='name')
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get items from given checklist_id.\nRetrying in a few seconds.')
            try:
                checklist_items = self.trello.ExtendedChecklists.get_decoded_checkItem(checklist_id, fields='name')
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get checklist items.')
        finally:
            return [li['name'] for li in checklist_items]

    def get_board_cards(self, board_id):
        """Given a board_id, get all cards on a board.

        :param board_id: ID of a Trello board
        :return: JSON representation of Trello board complete with cards not in 'Complete'
        """
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        board_cards = []
        try:
            board_cards = self.trello.ExtendedBoards.get_decoded_card(board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to get cards from given board_id.\nRetrying in a few seconds.')
            try:
                board_cards = self.trello.ExtendedBoards.get_decoded_card(board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to get cards.')
        finally:
            return list(filter(lambda card: card['idList'] != self.completeListId, board_cards))

    def add_new_card(self, card_name, card_list_id, pos, card_desc):
        """Add a new Trello card to a list on the board.

        :param card_name: name of the new Trello card
        :param card_list_id: ID of the list where the card will go
        :param pos: position in the list (top/bottom/arithmetic)
        :param card_desc: description/content of the card
        :return:
        """
        if not card_name or card_name is None:
            raise CardException('[!] Invalid card_name')
        if not card_list_id or card_list_id is None:
            raise CardException('[!] Invalid card_list_id')
        if not card_desc or card_desc is None:
            raise CardException('[!] Invalid card_desc')
        # put card on the bottom if it somehow gets in w/o pos
        if not pos or pos is None:
            pos = 'bottom'

        new_card = None
        try:
            new_card = self.trello.ExtendedCards.new(card_name, card_list_id, pos, card_desc)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add card.\nRetrying in a few seconds.')
            try:
                new_card = self.trello.ExtendedCards.new(card_name, card_list_id, pos, card_desc)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add card.')
        finally:
            return new_card

    def add_new_label(self, card_id, name, color='orange'):
        """Add a new label to a Trello card given a card_id. Default color is orange.

        :param card_id: ID of the card to get the label
        :param name: label text. If empty, a solid label with no text will be added.
        :param color: color of the label, defaults to orange
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        if not name or name is None:
            raise CardNameException('[!] Invalid card name')

        new_label = None
        try:
            new_label = self.trello.ExtendedCards.add_new_label(card_id, name, color)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add card label.\nRetrying in a few seconds.')
            try:
                new_label = self.trello.ExtendedCards.add_new_label(card_id, name, color)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add card label.')
        finally:
            return new_label

    def add_new_member(self, card_id, member_id):
        """Given a cardID and a member_id of a team member, assign that member to the card.

        :param card_id: id of the card to assign the member
        :param member_id: Trello team member's Trello ID
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        if not member_id or member_id is None:
            raise MemberIdException('[!] Invalid member_id')

        new_member = None
        try:
            new_member = self.trello.ExtendedCards.new_member(card_id, member_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add card member.\nRetrying in a few seconds.')
            try:
                new_member = self.trello.ExtendedCards.new_member(card_id, member_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add card member.')
        finally:
            return new_member

    def add_new_attachment(self, card_id, url):
        """Add a new attachment located at the given URL to a Trello card.

        :param card_id: ID of the card receiving the attachment
        :param url: URL where the attachment lives
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        if not url or url is None:
            raise CardAttachmentException('[!] Invalid URL')

        attachment = None
        try:
            attachment = self.trello.ExtendedCards.new_decoded_attachment(card_id, url)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add attachment.\nRetrying in a few seconds.')
            try:
                attachment = self.trello.ExtendedCards.new_decoded_attachment(card_id, url)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add attachment.')
        finally:
            return attachment

    def add_new_checklist(self, card_id, name=None):
        """Add a new checklist to a Trello card.

        :param card_id: ID of the card getting the checklist
        :param name: name of the checklist. Defaults to 'Checklist' or something generic
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        checklist = None
        try:
            checklist = self.trello.ExtendedCards.new_decoded_checklist(card_id, name)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add checklist.\nRetrying in a few seconds.')
            try:
                checklist = self.trello.ExtendedCards.new_decoded_checklist(card_id, name)
            except HTTPError as httpe:
                print(httpe.response.status_code,  '- Unable to add checklist.')
        finally:
            return checklist

    def add_new_checklist_item(self, card_id, checklist_id, name):
        """Add a new item to a checklist on a Trello card.

        :param card_id: ID of the card with the checklist
        :param checklist_id: ID of the checklist
        :param name: name of the new checklist item
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        if not checklist_id or checklist_id is None:
            raise ChecklistIdException('[!] Invalid checklist_id')

        item = None
        if self.get_checklist(card_id) is not None:
            try:
                item = self.trello.ExtendedChecklists.new_decoded_checkItem(checklist_id, name)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Failed to add checklist item.\nRetrying in a few seconds.')
                try:
                    item = self.trello.ExtendedChecklists.new_decoded_checkItem(checklist_id, name)
                except HTTPError as httpe:
                    print(httpe.response.status_code, '- Unable to add checklist item.')
            finally:
                return item

    def add_new_list(self, listName, board_id):
        """Add a new list to a Trello board given a board_id.

        :param listName: name to give the new list
        :param board_id: ID of the board to add the list onto
        :return:
        """
        if not listName or listName is None:
            raise ListNameException('[!] List needs a name')
        if not board_id or board_id is None:
            raise BoardIdException('[!] Invalid board_id')

        new_list = None
        try:
            new_list = self.trello.ExtendedLists.new_decoded_list(listName, board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to add list.\nRetrying in a few seconds.')
            try:
                new_list = self.trello.ExtendedLists.new_decoded_list(listName, board_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add list.')
        finally:
            return new_list

    def clear_list(self, list_id):
        """Given a list_id, archive all cards in that list.

        :param list_id: id of a Trello list
        :return:
        """
        if not list_id or list_id is None:
            raise ListIdException('[!] Invalid list_id')
        try:
            self.trello.ExtendedLists.archive_all_cards(list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to archive list.\nRetrying.')
            try:
                self.trello.ExtendedLists.archive_all_cards(list_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to archive list.')

    def copy_card(self, card_id, destination_list_id=None):
        """Copy card to new list if the destination_list_id != current list_id.

        :param card_id: ID of the card to copy
        :param destination_list_id: ID of the destination list
        :return:
        """
        if not card_id or card_id is None:
            raise CardException('[!] Must pass in a valid card')
        if not destination_list_id or destination_list_id is None:
            raise ListIdException('[!] Invalid destination_list_id')

        try:
            self.trello.ExtendedCards.copy_card(card_id, destination_list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to copy card.\nRetrying.')
            try:
                self.trello.ExtendedCards.copy_card(card_id, destination_list_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to copy card.')
        else:
            self.delete_card(card_id)

    def remove_member(self, card_id, member_id):
        """Remove a member from a Trello card.

        :param card_id: ID of the card from which to remove a member
        :param member_id: ID of the member to remove
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        if not member_id or member_id is None:
            raise MemberIdException('[!] Invalid member_id')

        try:
            self.trello.ExtendedCards.delete_member_idMember(member_id, card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to remove member from card.\nRetrying.')
            try:
                self.trello.ExtendedCards.delete_member_idMember(member_id, card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to remove member.')

    def move_card(self, card_id, list_id, pos='bottom'):
        """Move a card from it's current list to the list at list_id.

        :param card_id: ID of the card to move
        :param list_id: ID of the destination list
        :param pos: position within the lis. Defaults to bottom
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')
        if not list_id or list_id is None:
            raise ListIdException('[!] Invalid list_id')

        try:
            self.trello.ExtendedCards.update_idList_pos(card_id, list_id, pos=pos)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to move card.\nRetrying.')
            try:
                self.trello.ExtendedCards.update_idList_pos(card_id, list_id, pos=pos)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to move card.')

    def delete_card(self, card_id):
        """Delete a card with the given card_id.

        :param card_id: ID of the card to delete
        :return:
        """
        if not card_id or card_id is None:
            raise CardIdException('[!] Invalid card_id')

        try:
            self.trello.ExtendedCards.delete(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to delete card.\nRetrying.')
            try:
                self.trello.ExtendedCards.delete(card_id)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to delete card.')

    def move_all_cards_in_list(self, list_id, idBoard, idList):
        """Move all cards in a list to another list.

        :param list_id: ID of the list to move cards from
        :param idBoard: ID of the destination board
        :param idList: ID of the destination list
        :return:
        """
        if not list_id or list_id is None:
            raise ListIdException('[!] Invalid list_id')
        if not idBoard or idBoard is None:
            raise BoardIdException('[!] Invalid destination idBoard')
        if not idList or idList is None:
            raise ListIdException('[!] Invalid destination idList')

        try:
            self.trello.ExtendedLists.move_all_cards(list_id, idBoard, idList)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Failed to move cards to new list.\nRetrying.')
            try:
                self.trello.ExtendedLists.move_all_cards(list_id, idBoard, idList)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to move cards.')

    def populate(self):
        """Populate the things declared in __init__."""

        self.board = self.get_trello_board(self.board_id)
        self.lists = self.get_trello_lists(self.board_id)
        self.labels = self.get_board_labels(self.board_id)
        self.members = self.get_board_members(self.board_id)

        if self.board is None:
            print('[!] TrelloBoard initialization failed: Unable to grab board from Trello')
            sys.exit(-1)

        if self.lists is None:
            print('[!] TrelloBoard initialization failed: Unable to grab lists from Trello')
            sys.exit(-1)

        if self.members is None:
            print('[!] TrelloBoard initialization failed: Unable to grab board members from Trello')
            sys.exit(-1)

        if self.labels is None:
            print('[!] TrelloBoard initialization failed: Unable to grab board members from Trello')
            sys.exit(-1)

        self.cards = self.get_cards_from_lists(self.lists)
        self.cardCount = len([card for card in self.cards if card['listID'] != self.completeListId])
