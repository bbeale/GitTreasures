#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, redirect, render_template
from src.gitlab_log import GitLabLog as GL
from argparse import ArgumentParser, ArgumentError
import git_treasures
import configparser
import sys
import os

config = configparser.ConfigParser()


def parse_args():
    parser = ArgumentParser()
    try:
        parser.add_argument(
            '-d', '--dev',
            action='store_true',
            required=False,
            help='Run the development version of the script')
        parser.add_argument(
            '-tr', '--testrail',
            action='store_true',
            required=False,
            help='If true, will reconcile TestRail after Trello is complete.')
        parser.add_argument(
            '-r', '--results',
            action='store_true',
            required=False,
            help='If true, will run test results mode.')
        parser.add_argument(
            '-p', '--persist',
            action='store_true',
            required=False,
            help='If true, will only persist TestRail results.')
    except ArgumentError as err:
        raise err
    else:
        return parser.parse_args()


try:
    config.read(os.path.join('config', 'config.ini'))
except OSError as e:
    print(e, "Cannot get settings from config file")
    sys.exit(1)

db_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "data",
    "git_treasures.db"
)


app = Flask(__name__)
app.secret_key = config["flask"]["secret_key"]


@app.route("/")
@app.route("/index.html")
def home():

    commit = GL.get_latest_stored_commit(db_path)

    commit_data = dict(
        date    = commit[2],
        hash    = commit[1],
        author  = commit[3],
        message = commit[4]
    )

    return render_template("index.html", commit_data=commit_data)


@app.route("/git_treasures")
def hit_endpoint():
    args = parse_args()
    git_treasures.main(args)

    return redirect("index.html", code=302)


@app.route("/git_treasures_dev")
def hit_test_endpoint():
    args = parse_args()
    args.dev = True
    git_treasures.main(args)

    return redirect("index.html", code=302)


@app.route("/git_treasures_testrail")
def hit_testrail_endpoint():
    args = parse_args()
    args.testrail = True
    git_treasures.main(args)

    return redirect("index.html", code=302)


@app.route("/git_treasures_testrail_dev")
def hit_testrail_test_endpoint():
    args = parse_args()
    args.testrail = True
    git_treasures.main(args)

    return redirect("index.html", code=302)


if __name__ == "__main__":
    app.run(debug=False)
