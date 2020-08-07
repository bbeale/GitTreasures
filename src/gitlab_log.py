#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.exceptions import GitLabLogException, DbException
from datetime import datetime, timedelta
from gitlab import Gitlab
import sqlite3
import json
import os
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
            'ref_name': self.branch,
            'with_stats': True
        }

    @staticmethod   # Making this static because I still need to use it in the endpoint
    def get_latest_stored_commit(db_path: str) -> tuple or None:
        """Get the most recent commit saved in the database.

        :param db_path: path to the sqlite (.db) file
        :return: a tuple representing the commit if one was found, otherwise None
        """
        if not os.path.exists(db_path):
            raise GitLabLogException('[!] Database path does not exist.')

        sql = 'SELECT commitID, hash, committerDate, author_name, commitMessage FROM commits ORDER BY committerDate DESC'

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchone()
            conn.close()
        except sqlite3.Error as sqle:
            print(sqle)
            raise GitLabLogException('[!] Failed to store new commit data.')

        return result if result is not None else None

    def get_latest_stored_commit_hash(self, db_path: str) -> str or None:
        """Get the hash of the most recently stored commit

        :param db_path:
        :return:
        """
        if not os.path.exists(db_path):
            raise GitLabLogException('[!] Database path does not exist.')

        commit = self.get_latest_stored_commit(db_path)
        return commit[1] if commit is not None else None

    @staticmethod
    def get_stored_commits(db_path: str, test_file: str = None) -> list:
        """Get a list of commits from the database.

        :param db_path: path to the sqlite (.db) file
        :param test_file: path to JSON file containing test commit data
        :return: a list of dictionaries representing database records
        """
        if test_file is not None:
            test_commit_file = open(os.path.join(test_file), 'r', encoding='utf-8')
            results = json.loads(test_commit_file.read())

        else:
            if not os.path.exists(db_path):
                raise GitLabLogException('Database path does not exist')

            sql = 'SELECT * FROM commits ORDER BY committerDate DESC'

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(sql)
            except sqlite3.Error as sqle:
                print(sqle)
                raise GitLabLogException('[!] Failed to retrieve commits from the db.')

            tmp_r = cursor.fetchall()
            conn.close()
            results = []

            for r in tmp_r:
                r_dict = {
                    'index': r[0],
                    'hash': r[1],
                    'committerDate': r[2],
                    'mainBranch': r[3],
                    'author_name': r[4],
                    'author_email': r[5],
                    'commitMessage': r[6]
                }

                results.append(r_dict)
        return results

    def store_new_commits(self, repopath: str, token: str, project_id: int, query_params: dict) -> list:
        """Store commit data pulled from GitLab API into the sqlite database.

        :param repopath: location of the repo, either a path or a URL depending on CLI args.
        :param token: API token
        :param project_id: GitLab project ID
        :param query_params: GitLab query parameters
        :return:
        """
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

                    row = {
                        'index': index,
                        'hash': attr['id'],
                        'committerDate': attr['committed_date'],
                        'mainBranch': self.branch,
                        'author_name': attr['author_name'],
                        'author_email': attr['committer_email'],
                        'commitMessage': ''.join(re.findall(r'[^*`#\t\r\n\'"]', attr['message']))
                    }

                    try:
                        # store_commit_data(self.dbPath, row)
                        self.store_new_commit(self.dbPath, row)
                    except sqlite3.Error as sqle:
                        print(sqle)
                        raise GitLabLogException('[!] Unable to store new commits')

        return self.get_stored_commits(self.dbPath)

    def store_new_commit(self, db_path: str, values: dict) -> None:
        """Add a new commit record to the database.

        :param db_path: path to the sqlite (.db) file
        :param values: a dictionary of key_value pairs to add to the databse
        """
        if not os.path.exists(db_path):
            raise GitLabLogException('Database path does not exist')

        if len(values.keys()) is 0:
            raise DbException('values must be a dict with >1 record')

        try:
            values['index'] = self.get_latest_stored_commit(db_path)[0]
        except TypeError as te:
            print(te)
            values['index'] = 0

        finally:
            values['index'] += 1
            sql = 'INSERT INTO commits (commitID,hash,committerDate,mainBranch,author_name,author_email,commitMessage) VALUES((?),(?),(?),(?),(?),(?),(?))'
            values = (values['index'], values['hash'], values['committerDate'], values['mainBranch'], values['author_name'], values['author_email'], values['commitMessage'],)

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(sql, values)
                conn.commit()
                conn.close()
            except sqlite3.Error:
                print('[!] Hash already exists')

    def populate(self) -> None:
        """Populate an instance list of commits with results from store_new_commits()."""
        self.lastCommit = self.get_latest_stored_commit(self.dbPath)

        if self.lastCommit is not None:
            self.query_params['since'] = self.lastCommit[2]

        else:
            self.query_params['since'] = self.startDate

        self.commits = self.store_new_commits(self.repoPath, self.repoToken, self.project_id, self.query_params)
