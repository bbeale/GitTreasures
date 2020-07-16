#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json


class TrelloExtension(object):

    __module__ = 'trello'

    def __init__(self, apikey, token=None):
        self._apikey = apikey
        self._token = token

    def copy_card(self, id_card_source, id_list, desc=None):
        resp = requests.post("https://trello.com/1/cards",
            params={
                "key": self._apikey,
                "token": self._token
            },

            data= {
                "idList": id_list,
                "idCardSource": id_card_source,
                "keepFromSource": "all",
                "pos": "top",
                "desc": desc
            })

        resp.raise_for_status()
        return json.loads(resp.text)
