#!/usr/bin/env python
# -*- coding: utf-8 -*-
from util import store_commit_data, get_latest_commit, get_stored_commits
from datetime import datetime, timedelta
import sqlite3
from gitlab import Gitlab
import sys
import re


class GitLabLog(object):

    def __init__(self, config: dict, testMode: bool = False):
        """Initialize the GitLabLog object.

        Very similar to GitLog, except using GitLab instead of on-premise git instance.

        :param config: Git configuration settings
        :param testMode: if True, use test commit JSON file. Otherwise, use GitLab API
        """
        print('[+] Initializing GitLabLog')

        self.testMode = testMode
        self.repoPath = config.get('repo_path')
        self.repoToken = config.get('token')
        self.project_id = config.get('project_id')
        self.branch = config.get('staging_branch_name')
        self.dbPath = config.get('db_path')
        self.jira_pattern = re.compile(config.get('jira_pattern'))
        self.today = datetime.today()
        self.startDate = datetime.today() - timedelta(days=30)
        self.lastCommit = None
        self.branches = []
        self.commits = []
        self.query_params = {
            "ref_name": self.branch,
            "with_stats": True
        }

    def store_new_commits(self, repopath: str, token: str, project_id: int, query_params: dict) -> list:
        """Store commit data pulled from GitLab API into the sqlite database.

        :param repopath: location of the repo, either a path or a URL depending on CLI args.
        :param token: API token
        :param project_id: GitLab project ID
        :param query_params: GitLab query parameters
        :return:
        """
        print('[+] Analyzing commit data from GitLab')
        with Gitlab(repopath, private_token=token) as gl:
            gl.auth()
            gl_project = gl.projects.get(project_id)
            commits = sorted(gl_project.commits.list(
                all=True,
                query_parameters=query_params),
                key=lambda c: c.attributes['committed_date']
            )

            for commit in commits:
                attr = commit.attributes

                if re.findall(self.jira_pattern, attr['message']):
                    index = commits.index(commit)

                    row = dict(
                        index           = index,
                        hash            = attr['id'],
                        committerDate   = attr['committed_date'],
                        mainBranch      = self.branch,
                        author_name     = attr['author_name'],
                        author_email    = attr['committer_email'],
                        commitMessage   = ''.join(re.findall(r'[^*`#\t\r\n\'"]', attr['message']))
                    )

                    try:
                        store_commit_data(self.dbPath, row)
                    except sqlite3.Error as sqle:
                        print(sqle, '\nUnable to store new commits')
                        sys.exit(-1)

        return get_stored_commits(self.dbPath)

    def populate(self):
        """Populate an instance list of commits with results from store_new_commits()."""
        self.lastCommit = get_latest_commit(self.dbPath)

        if self.lastCommit is not None:
            self.query_params['since'] = self.lastCommit[2]

        else:
            self.query_params['since'] = self.startDate

        self.commits = self.store_new_commits(self.repoPath, self.repoToken, self.project_id, self.query_params)
