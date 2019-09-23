#!/usr/bin/env python
# -*- coding: utf-8 -*-
from vendor.pydriller.repository_mining import RM as RepositoryMining
from util import get_latest_commit_hash, store_commit_data, get_stored_commits
from datetime import datetime, timedelta
import subprocess, os
import json
import re


class GitLog:

    def __init__(self, config, testMode=False):
        """Initialize the GitLog object.

        :param config: Git configuration settings
        :param testMode: if True, use test commit JSON file. Otherwise, use PyDriller
        """
        print("Initializing GitLog")

        self.testMode           = testMode
        self.repoPath           = config["repo_path"]
        self.branch_name        = config["staging_branch_name"]
        self.jira_pattern       = config["jira_pattern"]
        self.dbPath             = config["db_path"]
        self.today              = datetime.today()
        self.startDate          = datetime.today() - timedelta(days=15)
        self.lastCommitHash     = get_latest_commit_hash(self.dbPath)
        self.lastCommitDate     = ""
        self.currentBranch      = ""
        self.commits            = []
        self.branches           = []

        # make sure I'm on staging before I go
        subprocess.check_call(["git", "-C", self.repoPath, "checkout", "staging"])
        subprocess.check_call(["git", "-C", self.repoPath, "pull"])

        if self.lastCommitHash is not None:
            self.miner = RepositoryMining(self.repoPath,
                                          only_in_main_branch=False,
                                          from_commit=self.lastCommitHash,
                                          reversed_order=False)

        else:
            self.miner = RepositoryMining(self.repoPath,
                                          only_in_main_branch=False,
                                          since=self.startDate,
                                          reversed_order=False)

    def get_new_commits(self, test_file=None):
        """Get commits from the repository via the RepositoryMiner object.

        :param test_file: JSON file representing commits used for testing
        """
        if self.testMode and test_file:
            test_commit_file = open(os.path.join(test_file), "r", encoding="utf-8")
            self.commits = json.loads(test_commit_file.read())

        else:
            print("Going through the repository...")
            for commit in self.miner.commits:
                if re.findall(self.jira_pattern, commit.msg):
                    count = self.miner.commits.index(commit)
                    other_branches = "|".join([branch for branch in commit.branches])

                    row = dict(
                        index           =count,
                        hash            =commit.hash,
                        committerDate   =commit.committer_date.strftime("%Y-%m-%d %H:%M:%S%z"),
                        mainBranch      =commit._main_branch,
                        otherBranches   =other_branches,
                        author_name     =commit.author.name,
                        author_email    =commit.author.email,
                        commitMessage   ="".join(re.findall(r'[^*`#\t\'"]', commit.msg))
                    )

                    store_commit_data(self.dbPath, row)
            print("\tdone")
        return get_stored_commits(self.dbPath)

    def populate(self):
        """Populate an instance list of commits with results from get_new_commits()."""
        self.commits = self.get_new_commits()
