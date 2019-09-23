#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, redirect, render_template
import git_treasures
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'yek_terces'


@app.route('/')
@app.route('/index.html')
def home():

    commit = getMostRecentHash()

    commit_data = dict(
        date    = commit[0],
        hash    = commit[1],
        author  = commit[2],
        message = commit[3]
    )

    return render_template('index.html', commit_data=commit_data)


@app.route('/git_treasures')
def hit_endpoint():

    git_treasures.main()

    return redirect('index.html', code=302)


@app.route('/git_treasures_dev')
def hit_test_endpoint():

    git_treasures.dev()

    return redirect('index.html', code=302)


@app.route('/git_treasures_testrail')
def hit_testrail_endpoint():

    git_treasures.testrail_main()

    return redirect('index.html', code=302)


def getMostRecentHash():

    connection = sqlite3.connect(os.path.join('data', 'git_treasures.db'))
    cursor = connection.cursor()
    cursor.execute("SELECT committerDate, hash, author_name, commitMessage FROM commits ORDER BY committerDate DESC")
    result = cursor.fetchone()
    connection.close()

    return result


if __name__ == '__main__':
    app.run(debug=True)
