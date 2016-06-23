import time

import multiprocessing
from datashape import json
from flask import Flask

from agent.withings_agent import WithingsAgent
from flask import request as flask_request

app = Flask(__name__)
server = None

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


def run():
    app.run(host='0.0.0.0')