#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests.exceptions import RequestException
from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask_dotenv import DotEnv
import os


app = Flask(__name__)
env = DotEnv()
env.init_app(app, env_file=".env", verbose_mode=False)


@app.route("/")
@app.route("/index.html")
def home():
    return "Hello, world!", 200


if __name__ == "__main__":
    # serve(app, host='127.0.0.1', port=5000)
    app.run(host='0.0.0.0', port=5000)
