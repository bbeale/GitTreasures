#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lib.trello.extension import TrelloExtension as TE
from src.exceptions import TrelloBoardException
from requests.exceptions import HTTPError
from trello import TrelloApi
from util import get_configs
import sys
import os


class TrelloBoard(object):

    def __init__(self, config: dict, testMode: bool  = False) -> None:
        """Initialize TrelloBoard object.

        :param config: Trello configuration settings
        :param testMode: if True, use test board JSON file. Otherwise, use Trello API
        """
        print('[+] Initializing TrelloBoard')

        if not config or config is None:
            raise ValueError('[!] Invalid configs')

        listpath = os.path.relpath(os.path.join('config', 'trello_lists.ini'))
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
        self.extension          = TE(self.key, self.token)
        self.board              = None
        self.lists              = None
        self.labels             = None
        self.members            = None

    # methods that 'get' stuff
    def get_trello_board(self, board_id: str) -> dict:
        """Given a board_id, retrieve Trello board data from API.

        :param board_id: board_id of a Trello board
        :return: JSON representatoin of a Trello baard
        """
        try:
            result = self.trello.boards.get(board_id=board_id)
        except HTTPError as httpe:
            print('[!] {}: Unable to get Trello board.'.format(httpe.response.status_code))
            raise TrelloBoardException
        else:
            return result

    def get_trello_lists(self, board_id: str) -> dict:
        """Get all lists attached to a Trello board.

        :param board_id: ID of the board to grab lists from
        :return: JSON representation of all board lists
        """
        try:
            result = self.trello.boards.get_list(board_id=board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get Trello lists.')
            raise TrelloBoardException
        else:
            return result

    def get_board_labels(self, board_id: str) -> dict:
        """Given a board_id, returns available labels attached to a Trello board.

        :param board_id: ID of the board to grab labels from
        :return: JSON representation of card labels
        """
        try:
            result = self.trello.boards.get_label(board_id=board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get labels.')
            raise TrelloBoardException
        else:
            return result

    def get_board_members(self, board_id: str) -> dict:
        """Get members associated with a Trello board.

        :param board_id: a Trello board ID
        :return: JSON representation of board members
        """
        try:
            result = self.trello.boards.get_member(board_id=board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get members.')
            raise TrelloBoardException
        else:
            return result

    def get_card_members(self, card_id: str) -> dict:
        """Get members assigned to a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card members
        """
        try:
            result = self.trello.cards.get_member(card_id=card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get members.')
            raise TrelloBoardException
        else:
            return result

    def get_trello_card_list(self, card_id: str) -> dict:
        """Get the list object that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: JSON representation of the card's list
        """
        try:
            result = self.trello.cards.get_list(card_id_or_shortlink=card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get list.')
            raise TrelloBoardException
        else:
            return result

    def get_trello_card_list_name(self, card_id: str) -> str or None:
        """Get the list NAME that a card is in, given the card's ID

        :param card_id: ID of a card whose list to return
        :return: list name string
        """
        card_id_list = self.get_trello_card_list(card_id)
        return card_id_list.get('name') if card_id_list is not None else None

    def get_cards_from_lists(self, lists: dict) -> list:
        """Given a list of Trello lists, get data for all card on each list.

        :param lists: a list of lists to grab cards from.
        :return tmp: a list of dictionaries representing cards from lists
        """
        tmp = []
        for trello_list in lists:
            trello_cards = self.get_cards_from_list(trello_list.get('id'))
            # check if trello_cards is None or zero before trying to add them to tmp
            if len(trello_cards) > 0:
                for card in trello_cards:
                    tmp.append({
                        'listID': trello_list.get('id'),
                        'listName': trello_list.get('name'),
                        'pos': card.get('pos'),
                        'id': card.get('id'),
                        'name': card.get('name'),
                        'cardDesc': card.get('desc'),
                        'labels': card.get('idLabels'),
                        'members': card.get('idMembers')
                    })
        return tmp

    def get_cards_from_list(self, list_id: str) -> dict:
        """ Given a Trello list_ID, get data for all card on that list.

        :param list_id:
        :return:
        """
        try:
            cards = self.trello.lists.get_card(idList=list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable get all cards from list.')
            raise TrelloBoardException
        else:
            return cards

    def get_card(self, card_id: str) -> dict:
        """Get data representing a Trello card by its card_id.

        :param card_id: ID of a card whose data to return
        :return: JSON representation of the card
        """
        try:
            result = self.trello.cards.get(card_id_or_shortlink=card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get card.')
            raise TrelloBoardException
        else:
            return result

    def get_card_count(self, cards: list) -> int:
        """Given a list of cards, return the count.

        :param cards: list of cards to count
        :return: number of records in cards list
        """
        if len(cards) is 0:
            return 0
        return len(list(filter(lambda card: card['listName'] != 'complete', cards)))

    def get_attachments(self, card_id: str) -> dict:
        """Get attachments from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card attachments
        """
        try:
            result = self.trello.cards.get_attachment(card_id_or_shortlink=card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get attachments.')
            raise TrelloBoardException
        else:
            return result

    def get_checklist(self, card_id: str) -> dict:
        """Get checklist from a Trello card.

        :param card_id: a Trello card ID
        :return: JSON representation of card checklist
        """
        try:
            result = self.trello.cards.get_checklist(card_id_or_shortlink=card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get checklist.')
            raise TrelloBoardException
        else:
            return result   # if len(result) is not 0 else None

    def get_checklist_items(self, checklist_id: str) -> list:
        """Get items from a checklist (on a Trello card).

        :param checklist_id: ID of a checklist on a Trello card
        :return: JSON representation of card checklist items
        """
        try:
            checklist_items = self.trello.checklists.get_checkItem(idChecklist=checklist_id, fields='name')
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get checklist items.')
            raise TrelloBoardException
        else:
            return [li['name'] for li in checklist_items]

    def get_board_cards(self, board_id: str) -> list:
        """Given a board_id, get all cards on a board.

        :param board_id: ID of a Trello board
        :return: JSON representation of Trello board complete with cards not in 'Complete'
        """
        try:
            board_cards = self.trello.boards.get_card(board_id=board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to get cards.')
            raise TrelloBoardException
        else:
            return list(filter(lambda card: card['idList'] != self.completeListId, board_cards))

    def add_new_card(self, card_name: str, card_list_id: str, pos: int or str, card_desc: str) -> dict:
        """Add a new Trello card to a list on the board.

        :param card_name: name of the new Trello card
        :param card_list_id: ID of the list where the card will go
        :param pos: position in the list (top/bottom/arithmetic)
        :param card_desc: description/content of the card
        :return:
        """
        # put card on the bottom if it somehow gets in w/o pos
        if not pos or pos is None:
            pos = 'bottom'

        try:
            new_card = self.trello.cards.new(name=card_name, idList=card_list_id, pos=pos, desc=card_desc)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to add card.')
            raise TrelloBoardException
        else:
            return new_card

    def add_new_label(self, card_id: str, name: str, color: str = 'orange') -> dict:
        """Add a new label to a Trello card given a card_id. Default color is orange.

        :param card_id: ID of the card to get the label
        :param name: label text. If empty, a solid label with no text will be added.
        :param color: color of the label, defaults to orange
        :return:
        """
        try:
            new_label = self.trello.cards.new_label(card_id_or_shortlink=card_id, name=name, color=color)
        except HTTPError as httpe:
            print(f'[!] {httpe.response.status_code} - Card label {name} already exists.')
        else:
            return new_label

    def add_new_member(self, card_id: str, member_id: str) -> dict:
        """Given a cardID and a member_id of a team member, assign that member to the card.

        :param card_id: id of the card to assign the member
        :param member_id: Trello team member's Trello ID
        :return:
        """
        try:
            new_member = self.trello.cards.new_idMember(card_id_or_shortlink=card_id, value=member_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to add card member.')
            raise TrelloBoardException
        else:
            return new_member

    def add_new_attachment(self, card_id: str, url: str, file: str = None, name: str = None, mimeType: str = None) -> dict:
        """Add a new attachment located at the given URL to a Trello card.

        :param card_id: ID of the card receiving the attachment
        :param url: URL where the attachment lives
        :param file: Local path where the attachment lives
        :param name:
        :param mimeType:
        :return:
        """
        try:
            attachment = self.trello.cards.new_attachment(card_id_or_shortlink=card_id, url=url, file=file, name=name, mimeType=mimeType)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to add attachment.')
            raise TrelloBoardException
        else:
            return attachment

    def add_new_checklist(self, card_id: str, name: str = None) -> dict:
        """Add a new checklist to a Trello card.

        :param card_id: ID of the card getting the checklist
        :param name: name of the checklist. Defaults to 'Checklist' or something generic
        :return:
        """
        try:
            checklist = self.trello.cards.new_checklist(card_id_or_shortlink=card_id, name=name)
        except HTTPError as httpe:
            print(httpe.response.status_code,  '- Unable to add checklist.')
            raise TrelloBoardException
        else:
            return checklist

    def add_new_checklist_item(self, card_id: str, checklist_id: str, name: str) -> dict or None:
        """Add a new item to a checklist on a Trello card.

        :param card_id: ID of the card with the checklist
        :param checklist_id: ID of the checklist
        :param name: name of the new checklist item
        :return:
        """
        if self.get_checklist(card_id) is not None:
            try:
                item = self.trello.checklists.new_checkItem(idChecklist=checklist_id, name=name)
            except HTTPError as httpe:
                print(httpe.response.status_code, '- Unable to add checklist item.')
                raise TrelloBoardException
            else:
                return item

    def add_new_list(self, listName: str, board_id: str) -> dict:
        """Add a new list to a Trello board given a board_id.

        :param listName: name to give the new list
        :param board_id: ID of the board to add the list onto
        :return:
        """
        try:
            new_list = self.trello.lists.new(name=listName, idBoard=board_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to add list.')
            raise TrelloBoardException
        else:
            return new_list

    def clear_list(self, list_id: str) -> None:
        """Given a list_id, archive all cards in that list.

        :param list_id: id of a Trello list
        :return:
        """
        try:
            self.trello.lists.new_archiveAllCard(idList=list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to archive list.')
            raise TrelloBoardException

    def copy_card(self, card_id: str, destination_list_id: str = None) -> None:
        """Copy card to new list if the destination_list_id != current list_id.

        :param card_id: ID of the card to copy
        :param destination_list_id: ID of the destination list
        :return:
        """
        try:
            self.extension.copy_card(card_id, destination_list_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to copy card.')
            raise TrelloBoardException
        else:
            self.delete_card(card_id)

    def remove_member(self, card_id: str, member_id: str) -> None:
        """Remove a member from a Trello card.

        :param card_id: ID of the card from which to remove a member
        :param member_id: ID of the member to remove
        :return:
        """
        try:
            self.trello.cards.delete_member_idMember(member_id, card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to remove member.')
            raise TrelloBoardException

    def move_card(self, card_id: str, list_id: str, pos: str = 'bottom') -> None:
        """Move a card from it's current list to the list at list_id.

        :param card_id: ID of the card to move
        :param list_id: ID of the destination list
        :param pos: position within the lis. Defaults to bottom
        :return:
        """
        try:
            self.trello.cards.update_idList_pos(card_id, list_id, pos=pos)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to move card.')
            raise TrelloBoardException

    def delete_card(self, card_id: str) -> None:
        """Delete a card with the given card_id.

        :param card_id: ID of the card to delete
        :return:
        """
        try:
            self.trello.cards.delete(card_id)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to delete card.')
            raise TrelloBoardException

    def move_all_cards_in_list(self, list_id: str, idBoard: str, idList: str) -> None:
        """Move all cards in a list to another list.

        :param list_id: ID of the list to move cards from
        :param idBoard: ID of the destination board
        :param idList: ID of the destination list
        :return:
        """
        try:
            self.trello.lists.new_moveAllCard_idList(idList=list_id, idBoard=idBoard, idList2=idList)
        except HTTPError as httpe:
            print(httpe.response.status_code, '- Unable to move cards.')
            raise TrelloBoardException

    def populate(self) -> None:
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
