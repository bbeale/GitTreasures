#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import HTTPError
from urllib.parse import urljoin
from util import get_configs
from src.exceptions import *
import dateutil.parser
import json
import os
import re


class ClubhouseBoard:

    def __init__(self):
        pass

    """
        https://clubhouse.io/api/rest/v3/
    """
