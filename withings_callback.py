import time

import multiprocessing
from datashape import json
from flask import Flask
from werkzeug.serving import run_simple

from agent.withings_agent import WithingsAgent
from flask import request as flask_request

app = Flask(__name__)
server_addr = "http://203.253.23.40"
server_port = 5000

@app.route('/cb/withings')
def callback():
    WithingsAgent.instance.oauth_verifier = flask_request.args.get("oauth_verifier")
    WithingsAgent.instance.userid = flask_request.args.get("userid")
    print("[On Authorized] Content:")
    print("\t- oauth_verifier\t= %s" % WithingsAgent.instance.oauth_verifier)
    print("\t- userid\t= %s" % WithingsAgent.instance.userid)
    WithingsAgent.instance.access()
    WithingsAgent.instance.is_authorized = True
    WithingsAgent.instance.cache()

    return '<html><body>OK</body><html>'


@app.route('/kill', methods=['GET', 'POST'])
def stop():
    if not 'werkzeug.server.shutdown' in flask_request.environ:
        raise RuntimeError('Not running the development server')
    flask_request.environ['werkzeug.server.shutdown']()
    return ""


def run():
    run_simple("0.0.0.0", server_port, app)

