import json
import requests


class ExtendedLists(object):

    __module__ = 'trello'

    def __init__(self, apikey, token=None):
        self._apikey = apikey
        self._token = token

    def get_decoded_list(self, list_id, cards=None, card_fields=None, fields=None):
        resp = requests.get("https://trello.com/1/lists/%s" % (list_id), params=dict(key=self._apikey, token=self._token, cards=cards, card_fields=card_fields, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_card(self, list_id, actions=None, attachments=None, members=None, checkItemStates=None, checklists=None, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/lists/%s/cards" % (list_id), params=dict(key=self._apikey, token=self._token, actions=actions, attachments=attachments, members=members, checkItemStates=checkItemStates, checklists=checklists, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def archive_all_cards(self, listID):
        resp = requests.post("https://api.trello.com/1/lists/%s/archiveAllCards" % (listID), params=dict(key=self._apikey, token=self._token))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def new_decoded_list(self, name, idBoard):
        resp = requests.post("https://trello.com/1/lists" % (), params=dict(key=self._apikey, token=self._token), data=dict(name=name, idBoard=idBoard))
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))

    def new_decoded_card(self, list_id, name, desc=None):
        resp = requests.post("https://trello.com/1/lists/%s/cards" % (list_id), params=dict(key=self._apikey, token=self._token), data=dict(name=name, desc=desc))
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))

    def move_all_cards(self, listID, idBoard, idList):
        resp = requests.post("https://api.trello.com/1/lists/%s/moveAllCards" % (listID), params=dict(key=self._apikey, token=self._token), data=dict(idBoard=idBoard, idList=idList))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))
