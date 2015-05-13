#!/usr/bin/env python

import json

import argparse, os
from collections import OrderedDict
from flask import Flask, make_response, render_template, redirect, url_for, session, Response, g
from flask.ext.rauth import RauthOAuth2
from smartsheet import make_context

current_dir = os.path.dirname(__file__)
JSON_DATA = os.path.join(current_dir,'static','smartsheet.json')

app = Flask(__name__)
# you can specify the consumer key and consumer secret in the application,
#   like this:
app.config.update(
    GOOGLE_CONSUMER_KEY=os.environ['SMARTSHEET_OAUTH_CLIENT_ID'],
    GOOGLE_CONSUMER_SECRET=os.environ['SMARTSHEET_OAUTH_CONSUMER_SECRET'],
    SECRET_KEY=os.environ['SMARTSHEET_SALT'],
    DEBUG=True
)
app.secret_key=os.environ['SMARTSHEET_SALT']
app.debug = True

google = RauthOAuth2(
    name='google',
    base_url='https://www.googleapis.com/oauth2/v1/',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    # consumer_key=os.getenv('SMARTSHEET_OAUTH_CLIENT_ID'),
    # consumer_secret=os.getenv('SMARTSHEET_OAUTH_CONSUMER_SECRET')
)

def import_data():
    f = open(JSON_DATA, 'r')
    data = json.load(f)
    factCount = len(json.dumps(data))
    f.close()
    return data

@app.before_request
def before_request():
    g.data = import_data()
    g.count = len(g.data)

@app.route('/')
def index():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    return make_response(render_template('index.html'))

@app.route('/showboards')
def showboards():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    context = g.data
    context['showboards']['DAYS'] = OrderedDict(sorted(context['showboards']['DAYS'].iteritems(), key=lambda x: x[0]))
    return make_response(render_template('showboards.html', **context))

@app.route('/assignments')
def assignments():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    context = g.data

    return make_response(render_template('assignments.html', **context))

@app.route('/planning')
def planning():
    """
    Example view demonstrating rendering a simple HTML page.
    """
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    context = g.data
    context['planning']['DAYS'] = OrderedDict(sorted(context['planning']['DAYS'].iteritems(), key=lambda x: x[0]))
    return make_response(render_template('planning.html', **context))

# the Rauth service detects the consumer_key and consumer_secret using
#   `current_app`.
@app.route('/login')
def login():
    return google.authorize(
        callback=url_for('authorized', _external=True),
        hd='chicagopublicradio.org',
        scope='https://www.googleapis.com/auth/userinfo.profile')


@app.route('/authorized/')
@google.authorized_handler()
def authorized(resp, access_token):
    if resp == 'access_denied':
        return 'You denied access. Click <a href="%s">here</a> to try again.' % (url_for('login'),)

    session['access_token'] = access_token

    return redirect(url_for('index'))


# Boilerplate
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port')
    args = parser.parse_args()
    server_port = 8047

    if args.port:
        server_port = int(args.port)

    app.run(host='0.0.0.0', port=server_port, debug=True)
