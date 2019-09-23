#!/usr/bin/env python
# -*- coding: utf-8 -*-
from trello import TrelloApi
from trello.actions import Actions
from trello.boards import Boards
from trello.cards import Cards
from trello.checklists import Checklists
from trello.lists import Lists
from trello.members import Members
from trello.notifications import Notifications
from trello.organizations import Organizations
from trello.tokens import Tokens
from trello.types import Types

# package level imports
from .boards import ExtendedBoards
from .cards import ExtendedCards
from .lists import ExtendedLists
from .checklists import ExtendedChecklists


class TA(TrelloApi):


    """

    Maybe this is only an issue with the environment on which this was first meant to run, but the reason for all the
    decoded_ methods in the following classes is that I found on some versions of Python, the original methods
    (RepositoryMining.get_labels()) did not work unless I decoded the response.content explicitly. Aside from the
    method names and the use of decode(), these methods are copy/pasted from the Python package.

    """


    def __init__(self, apikey, token=None):
        super().__init__(apikey, token)
        self._apikey            = apikey
        self._token             = token
        self.actions            = Actions(apikey, token)
        self.boards             = Boards(apikey, token)
        self.cards              = Cards(apikey, token)
        self.checklists         = Checklists(apikey, token)
        self.lists              = Lists(apikey, token)
        self.members            = Members(apikey, token)
        self.notifications      = Notifications(apikey, token)
        self.organizations      = Organizations(apikey, token)
        self.tokens             = Tokens(apikey, token)
        self.types              = Types(apikey, token)
        self.ExtendedBoards     = ExtendedBoards(apikey, token)
        self.ExtendedCards      = ExtendedCards(apikey, token)
        self.ExtendedLists      = ExtendedLists(apikey, token)
        self.ExtendedChecklists = ExtendedChecklists(apikey, token)
