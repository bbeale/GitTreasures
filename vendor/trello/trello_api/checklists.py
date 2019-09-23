import json
import requests


class ExtendedChecklists(object):

    __module__ = 'trello'

    def __init__(self, apikey, token=None):
        self._apikey = apikey
        self._token = token

    def get_decoded_checkItem(self, checklist_id, filter=None, fields=None):
        resp = requests.get("https://trello.com/1/checklists/%s/checkItems" % (checklist_id), params=dict(key=self._apikey, token=self._token, filter=filter, fields=fields), data=None)
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))

    def new_decoded_checkItem(self, checklist_id, name):
        resp = requests.post("https://trello.com/1/checklists/%s/checkItems" % (checklist_id), params=dict(key=self._apikey, token=self._token), data=dict(name=name))
        resp.raise_for_status()
        return json.loads(resp.content.decode("utf-8"))
