import json
import requests


class ExtendedBoards(object):

    __module__ = 'trello'

    def __init__(self, apikey, token=None):
        self._apikey = apikey
        self._token = token

    def get_decoded_labels(self, board_id, cards=None, card_fields=None, checkItems=None, checkItem_fields=None, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/boards/%s/labels" % (board_id), params=dict(key=self._apikey, token=self._token, cards=cards, card_fields=card_fields, checkItems=checkItems, checkItem_fields=checkItem_fields, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_board(self, board_id, actions=None, action_fields=None, action_limit=None, cards=None, card_fields=None, lists=None, list_fields=None, members=None, member_fields=None, membersInvited=None, membersInvited_fields=None, checklists=None, checklist_fields=None, organization=None, organization_fields=None, myPrefs=None, fields=None):
        resp = requests.get("https://trello.com/1/boards/%s" % (board_id), params=dict(key=self._apikey, token=self._token, actions=actions, action_fields=action_fields, action_limit=action_limit, cards=cards, card_fields=card_fields, lists=lists, list_fields=list_fields, members=members, member_fields=member_fields, membersInvited=membersInvited, membersInvited_fields=membersInvited_fields, checklists=checklists, checklist_fields=checklist_fields, organization=organization, organization_fields=organization_fields, myPrefs=myPrefs, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_list(self, board_id, cards=None, card_fields=None, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/boards/%s/lists" % (board_id), params=dict(key=self._apikey, token=self._token, cards=cards, card_fields=card_fields, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_card(self, board_id, actions=None, attachments=None, members=None, checkItemStates=None, checklists=None, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/boards/%s/cards" % (board_id), params=dict(key=self._apikey, token=self._token, actions=actions, attachments=attachments, members=members, checkItemStates=checkItemStates, checklists=checklists, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_member(self, board_id, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/boards/%s/members" % (board_id), params=dict(key=self._apikey, token=self._token, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))
