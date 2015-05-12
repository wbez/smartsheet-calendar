activate_this = '/home/ubuntu/.virtenvs/smartsheet/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys, logging, os

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/srv/smartsheet')

def application(environ, start_response):
    for key in ['SMARTSHEET_TOKEN', 'SMARTSHEET_OAUTH_CLIENT_ID', 'SMARTSHEET_OAUTH_CONSUMER_SECRET', 'SMARTSHEET_SALT' ]:
        os.environ[key] = environ.get(key, '')

    from app import app as _application
    _application.secret_key = environ.get('SMARTSHEET_SALT', '')

    return _application(environ, start_response)