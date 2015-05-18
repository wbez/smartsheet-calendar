# Smartsheet Calendars
Simple app that takes a set of smartsheets through the python API, creates json from them and feeds that to a simple flask app that provides a custom display of the sheets.

## Workflow
* Smartsheet data is loaded using the python API
* Data is processed in part using pandas, then written to json
* JSON data is imported into a flask app
* Pages are protected with Google login using flask-rauth
* Data are split into two views: Showboards and planning
* Cron generates JSON every minute. Pages autorefresh every minute.

## Needed credentials
* Smartsheet API token
* Google API credentials
* Flask secret key for sessions

## How to install
Clone this repo to your local machine. We recommend starting a new python Virtual Environment using virtualenvwrapper (see above) for your project.

```
git clone git@github.com:wbez/smartsheet-calendar.git
cd smartsheet-calendar
mkvirtualenv curiouscity-facts --python=/usr/bin/python2.7
```

The virtual environment starts up automatically on creation, but to activate it in the future just use:

```
workon smartsheet-calendar
```

Your new virtual environment comes with the pip python package manager. All libraries installed with the virtualenv active will be contained within the local environment and not available globally. This keeps different dependencies for different projects separate so there aren't any version conflicts.

The repo comes with a list of required libraries in requirements.txt. To install all of these, navigate to your project directory and run:

```
pip install -r requirements.txt
```
to get all the needed packages.

This app relies on flask-rauth for Google login, but it needs to be modified to work correctly. Comment lines 117-128 to remove the content @property before use.

## How to start the app locally

From the terminal, run:

```
python app.py 
```

Then go to http://127.0.0.1:8047/ to see your shiny new app.

