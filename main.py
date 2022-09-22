import os
from flask_sslify import SSLify
from flask import request, Flask


server = Flask(__name__)

@server.route('/')
def webhook():...