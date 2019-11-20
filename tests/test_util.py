#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import (
    get_configs,
    is_db_init,
    get_latest_commit,
    get_latest_commit_hash
)

from src.exceptions import (
    DbPathException
)

from unittest import TestCase
import os


class TestUtil(TestCase):

    """
    positive tests for get_configs
    """
    def test_get_configs_name(self):
        configs     = "test.config.ini"
        fields      = ["name"]
        result      = get_configs(fields, configs)

        self.assertIn("name", result["test_user"])
        self.assertNotIn("email", result["test_user"])
        self.assertNotIn("jira_username", result["test_user"])
        self.assertNotIn("jira_displayname", result["test_user"])
        self.assertNotIn("trello_id", result["test_user"])
        self.assertNotIn("trello_username", result["test_user"])

    def test_get_configs_email(self):
        configs     = "test.config.ini"
        fields      = ["email"]
        result      = get_configs(fields, configs)

        self.assertIn("email", result["test_user"])
        self.assertNotIn("name", result["test_user"])
        self.assertNotIn("jira_username", result["test_user"])
        self.assertNotIn("jira_displayname", result["test_user"])
        self.assertNotIn("trello_id", result["test_user"])
        self.assertNotIn("trello_username", result["test_user"])

    def test_get_configs_all(self):
        configs     = "test.config.ini"
        fields      = ["name", "email", "jira_username", "jira_displayname", "trello_id", "trello_username"]
        result      = get_configs(fields, configs)

        self.assertIn("name", result["test_user"])
        self.assertIn("email", result["test_user"])
        self.assertIn("jira_username", result["test_user"])
        self.assertIn("jira_displayname", result["test_user"])
        self.assertIn("trello_id", result["test_user"])
        self.assertIn("trello_username", result["test_user"])

    """ 
    negative tests for get_configs
    """
    def test_get_configs_empty_fields(self):
        configs = "test.config.ini"
        fields = []
        with self.assertRaises(ValueError):
            get_configs(fields, configs)

    def test_get_configs_none_fields(self):
        configs = "test.config.ini"
        fields = None
        with self.assertRaises(ValueError):
            get_configs(fields, configs)

    def test_get_configs_empty_config(self):
        configs = ""
        fields = ["name", "email"]
        with self.assertRaises(FileNotFoundError):
            get_configs(fields, configs)

    def test_get_configs_none_config(self):
        configs = None
        fields = ["name", "email"]
        with self.assertRaises(FileNotFoundError):
            get_configs(fields, configs)


    """
    positive tests for is_db_init
    """
    def test_is_db_init_success(self):

        config_path     = "../config.ini"
        db_path         = "../{}".format(
            get_configs(["db_path"], config_path)["common"]["db_path"]
        )

        if not os.path.exists(config_path):
            self.fail("Test data issue. Unable to proceed without a valid config file")

        is_init = is_db_init(db_path)
        self.assertTrue(is_init)

    """
    negative tests for is_db_init
    """
    def test_is_db_init_empty_db_path(self):
        db_path = ""
        with self.assertRaises(DbPathException):
            is_db_init(db_path)

    def test_is_db_init_none_db_path(self):
        db_path = None
        with self.assertRaises(DbPathException):
            is_db_init(db_path)

    def test_is_db_init_invalid_db_path(self):
        db_path = "elephant.py"
        is_init = is_db_init(db_path)
        self.assertFalse(is_init)


    """
    positive tests for get_latest_commit
    """
    def test_get_latest_commit_success(self):
        config_path     = "../config.ini"
        db_path         = "../{}".format(
            get_configs(["db_path"], config_path)["common"]["db_path"]
        )

        if not os.path.exists(config_path):
            self.fail("Test data issue. Unable to proceed without a valid config file")

        result = get_latest_commit(db_path)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result[0]), 1)
        self.assertGreaterEqual(len(result[1]), 1)

    """
    negative tests for get_latest_commit
    """
    def test_get_latest_commit_empty_path(self):
        dbpath = ""
        with self.assertRaises(DbPathException):
            get_latest_commit(dbpath)

    def test_get_latest_commit_none_path(self):
        dbpath = None
        with self.assertRaises(DbPathException):
            get_latest_commit(dbpath)

    def test_get_latest_commit_invalid_path(self):
        dbpath = "donkey.py"
        with self.assertRaises(FileNotFoundError):
            get_latest_commit(dbpath)


    """
    positive tests for get_latest_commit_hash
    """
    def test_get_latest_commit_hash_success(self):
        config_path     = "../config.ini"
        db_path         = "../{}".format(
            get_configs(["db_path"], config_path)["common"]["db_path"]
        )

        if not os.path.exists(config_path):
            self.fail("Test data issue. Unable to proceed without a valid config file")

        result = get_latest_commit_hash(db_path)
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result), 0)

    """ 
    negative tests for get_latest_commit_hash
    """
    def test_get_latest_commit_hash_empty_path(self):
        dbpath = ""
        with self.assertRaises(DbPathException):
            get_latest_commit_hash(dbpath)

    def test_get_latest_commit_hash_none_path(self):
        dbpath = None
        with self.assertRaises(DbPathException):
            get_latest_commit_hash(dbpath)

    def test_get_latest_commit_hash_invalid_path(self):
        dbpath = "donkey.py"
        with self.assertRaises(FileNotFoundError):
            get_latest_commit_hash(dbpath)
