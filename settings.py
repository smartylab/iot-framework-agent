import os

BASE_DIR = os.path.dirname(__file__)

SERVER_ADDR = "http://203.253.23.30"
USER_API = SERVER_ADDR+'/api/user'
CONTEXT_API = SERVER_ADDR+'/api/context'
CONNECT_API = SERVER_ADDR+'/api/connect'
SERIES_CONTEXT_API = SERVER_ADDR+'/api/series_context'

AGENT_ADDR = "http://203.253.23.40"
AGENT_PORT = 5000