#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pydriller import RepositoryMining
from datetime import datetime
from typing import List
import logging

logger = logging.getLogger(__name__)


class RM(RepositoryMining):

    def __init__(self, path_to_repo: str,
                 single: str=None,
                 since: datetime=None,
                 to: datetime=None,
                 from_commit: str=None,
                 to_commit: str=None,
                 from_tag: str=None,
                 to_tag: str=None,
                 reversed_order: bool=False,
                 only_in_main_branch: bool=False,
                 only_in_branches: List[str]=None,
                 only_modifications_with_file_types: List[str]=None,
                 only_no_merge: bool=False
            ):

        super().__init__(path_to_repo,
                                  single,
                                  since,
                                  to,
                                  from_commit,
                                  to_commit,
                                  from_tag,
                                  to_tag,
                                  reversed_order,
                                  only_in_main_branch,
                                  only_in_branches,
                                  only_modifications_with_file_types,
                                  only_no_merge)
        self.commits = []
        self.traverse_commits()

    def traverse_commits(self):
        """
        Bastardized method from pydriller library that returns commits in a list instead of a generator
        """
        logger.info('Git repository in {}'.format(self.git_repo.path))
        all_cs = self._apply_filters_on_commits(self.git_repo.get_list_commits())

        if not self.reversed_order:
            all_cs.reverse()

        for commit in all_cs:
            logger.info('Commit #{} in {} from {}'
                         .format(commit.hash, commit.author_date, commit.author.name))

            if self._is_commit_filtered(commit):
                logger.info('Commit #{} filtered'.format(commit.hash))
                continue

            self.commits.append(commit)
