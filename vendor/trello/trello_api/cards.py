import json
import requests


class ExtendedCards(object):

    __module__ = 'trello'

    def __init__(self, apikey, token=None):
        self._apikey = apikey
        self._token = token

    def get_decoded_list(self, card_id, fields=None):
        resp = requests.get("https://trello.com/1/cards/%s/list" % (card_id), params=dict(key=self._apikey, token=self._token, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def new(self, name, idList, pos, desc=None):
        resp = requests.post("https://trello.com/1/cards" % (), params=dict(key=self._apikey, token=self._token), data=dict(name=name, idList=idList, pos=pos, desc=desc))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def copy_card(self, id_card_source, id_list, desc=None):
        resp = requests.post("https://trello.com/1/cards" % (), params=dict(key=self._apikey, token=self._token), data=dict(idList=id_list, idCardSource=id_card_source, keepFromSource="all", pos="top", desc=desc))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def update_idList_pos(self, card_id, idList, pos):
        resp = requests.put("https://trello.com/1/cards/%s" % (card_id), params=dict(key=self._apikey, token=self._token), data=dict(idList=idList, pos=pos))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def add_label(self, cardID, labelID):
        resp = requests.post("https://trello.com/1/cards/%s/idLabels" % (cardID), params=dict(key=self._apikey, token=self._token), data=dict(value=labelID))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def add_new_label(self, cardID, name, color):
        resp = requests.post("https://trello.com/1/cards/%s/labels" % (cardID), params=dict(key=self._apikey, token=self._token), data=dict(color=color, name=name))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def delete(self, card_id):
        resp = requests.delete("https://trello.com/1/cards/%s" % (card_id), params=dict(key=self._apikey, token=self._token), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_member(self, card_id, fields=None):
        resp = requests.get("https://trello.com/1/cards/%s/members" % (card_id), params=dict(key=self._apikey, token=self._token, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def new_member(self, card_id, value):
        resp = requests.post("https://trello.com/1/cards/%s/idMembers" % (card_id), params=dict(key=self._apikey, token=self._token), data=dict(value=value))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def delete_member_idMember(self, idMember, card_id):
        resp = requests.delete("https://trello.com/1/cards/%s/idMembers/%s" % (card_id, idMember), params=dict(key=self._apikey, token=self._token), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_card(self, card_id, actions=None, action_fields=None, action_limit=None, attachments=None, attachment_fields=None, members=None, member_fields=None, checkItemStates=None, checkItemState_fields=None, checklists=None, checklist_fields=None, fields=None):
        resp = requests.get("https://trello.com/1/cards/%s" % (card_id), params=dict(key=self._apikey, token=self._token, actions=actions, action_fields=action_fields, action_limit=action_limit, attachments=attachments, attachment_fields=attachment_fields, members=members, member_fields=member_fields, checkItemStates=checkItemStates, checkItemState_fields=checkItemState_fields, checklists=checklists, checklist_fields=checklist_fields, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_attachment(self, card_id, fields="all"):
        resp = requests.get("https://trello.com/1/cards/%s/attachments" % (card_id), params=dict(key=self._apikey, token=self._token, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def new_decoded_attachment(self, card_id, url):
        resp = requests.post("https://trello.com/1/cards/%s/attachments" % (card_id), params=dict(key=self._apikey, token=self._token), data=dict(url=url))
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def delete_decoded_attachment(self, card_id, idAttachment):
        resp = requests.delete("https://trello.com/1/cards/%s/attachments/%s" % (card_id, idAttachment), params=dict(key=self._apikey, token=self._token), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode('utf-8'))

    def get_decoded_checklist(self, card_id, cards=None, card_fields=None, checkItems=None, checkItem_fields=None, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/cards/%s/checklists" % (card_id), params=dict(key=self._apikey, token=self._token, cards=cards, card_fields=card_fields, checkItems=checkItems, checkItem_fields=checkItem_fields, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))

    def new_decoded_checklist(self, card_id, value):
        resp = requests.post("https://trello.com/1/cards/%s/checklists" % (card_id), params=dict(key=self._apikey, token=self._token), data=dict(value=value))
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))
