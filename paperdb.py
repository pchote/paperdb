#
# paperdb is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# paperdb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with paperdb.  If not, see <http://www.gnu.org/licenses/>.

# pylint: disable=invalid-name
# pylint: disable=broad-except

"""
A Flask + Bootstrap + jQuery frontend for a BibDesk paper database
"""

import base64
import io
import os
import re
import sqlite3
import sys
import traceback
import bibtexparser

from bibtexparser.customization import getnames, convert_to_unicode
import biplist

from flask import abort
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import session
from flask import url_for
from flask_oauthlib.client import OAuth

DOI_REGEX = re.compile(r'^http(s)?://(dx\.)?doi.org/.*$')
ARXIV_REGEX = re.compile('^http(s)?://arxiv.org/abs/.*$')
ADS_REGEX = re.compile('^http(s)?://adsabs.harvard.edu/abs/.*$')

# Keys to include in the "Minimal BibTeX" field
MINIMAL_BIBTEX_FIELDS = [
    'ID', 'ENTRYTYPE', 'author', 'journal', 'booktitle', 'month',
    'pages', 'title', 'volume', 'year', 'eprint', 'doi'
]


# pylint: disable=too-few-public-methods
class sqldb(object):
    """Context manager that opens a db and returns a cursor on enter, commits and closes on exit"""
    def __init__(self, dbfile, create_if_missing=False):
        self.dbfile = dbfile
        self._create_if_missing = create_if_missing
        self.connection = None

    def __enter__(self):
        if self._create_if_missing:
            self.connection = sqlite3.connect(self.dbfile)
        else:
            self.connection = sqlite3.connect('file:{0}?mode=rw'.format(self.dbfile), uri=True)
        return self.connection.cursor()

    def __exit__(self, exc_class, exc, tb):
        self.connection.commit()
        self.connection.close()
# pylint: enable=too-few-public-methods

app = Flask(__name__)
app.config.from_object('config.PaperDBConfig')
oauth = OAuth(app)
github = oauth.remote_app(
    'github',
    consumer_key=app.config['GITHUB_CLIENT_ID'],
    consumer_secret=app.config['GITHUB_CLIENT_SECRET'],
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

# Create database with default schema if missing
try:
    with sqldb(app.config['DATABASE_PATH']) as _:
        pass

except sqlite3.OperationalError:
    with sqldb(app.config['DATABASE_PATH'], create_if_missing=True) as create:
        create.execute('CREATE TABLE sessions (' + \
                       'github_token varchar(40) unique, ' + \
                       'github_id integer, ' + \
                       'timestamp integer);')
        create.execute('CREATE TABLE users(' + \
                       'github_id INTEGER PRIMARY KEY, ' + \
                       'username TEXT, ' + \
                       'last_active integer default 0);')
        create.execute('INSERT INTO users (github_id) VALUES (?);',
                       (app.config['GITHUB_FOUNDER_ID'],))


def get_user_account():
    """Queries user account details from the local cache or GitHub API
       Returns None if user is not logged in, or a dictionary with fields:
          'username': GitHub username
          'github_id': GitHub user ID
          'permission': True if user has authorization to view the content,
                        False if the account is not known
    """
    # Expire cached sessions after 12 hours
    # This forces details to be queried again from github
    try:
        with sqldb(app.config['DATABASE_PATH']) as cursor:
            sql = 'DELETE FROM sessions WHERE timestamp < Datetime(\'now\', \'-12 hours\')'
            cursor.execute(sql)
    except Exception:
        print('Failed to clean expired session data with error')
        traceback.print_exc(file=sys.stdout)

    # Check whether we have received a callback argument from a login attempt
    if 'code' in request.args:
        resp = github.authorized_response()
        if resp is not None and 'access_token' in resp:
            session['github_token'] = resp['access_token']

    # Logged in users store an encrypted version of their github token in the session cookie
    if 'github_token' in session:
        # Check whether we have any cached state
        try:
            with sqldb(app.config['DATABASE_PATH']) as cursor:
                sql = 'SELECT users.github_id, users.username from users, sessions ' + \
                    'WHERE users.github_id = sessions.github_id ' + \
                    'AND sessions.github_token = ?'
                cursor.execute(sql, (session['github_token'],))

                result = cursor.fetchone()
                if result:
                    github_id = result[0]
                    github_username = result[1]

                    # Cache session state for next time
                    query = 'UPDATE users SET last_active = Datetime(\'now\')' + \
                        ' WHERE github_id = ?'
                    cursor.execute(query, (github_id,))

                    return {
                        'username': github_username,
                        'github_id': github_id,
                        'permission': True
                    }
        except Exception:
            print('Failed to query local session data with error')
            traceback.print_exc(file=sys.stdout)

        # Query user data and permissions from GitHub
        try:
            user = github.get('user')
            github_id = user.data['id']

            # Simultaneously check whether the user is authorized (has a row in the users table)
            # and update the username / last active time
            with sqldb(app.config['DATABASE_PATH']) as cursor:
                query = 'UPDATE users SET username = ?, last_active = Datetime(\'now\')' + \
                    ' WHERE github_id = ?'
                cursor.execute(query, (user.data['login'], github_id))

                # User is not authorized
                if cursor.rowcount == 0:
                    print(user.data['login'], 'not authorized')

                    # Make sure stale data is erased
                    sql = 'DELETE FROM sessions WHERE github_token = ?'
                    cursor.execute(sql, (session['github_token'],))
                    session.pop('github_token', None)

                    return {
                        'username': user.data['login'],
                        'github_id': github_id,
                        'permission': False
                    }

                # Cache session state for next time
                query = 'REPLACE INTO sessions (github_token, github_id, timestamp)' \
                    + ' VALUES (?, ?, Datetime(\'now\'))'
                cursor.execute(query, (session['github_token'], github_id))

            return {
                'username': user.data['login'],
                'github_id': github_id,
                'permission': True
            }

        except Exception:
            print('Failed to query GitHub API with error')
            traceback.print_exc(file=sys.stdout)

    return None


@github.tokengetter
def get_github_oauth_token():
    """Fetch the github oauth token.
       Used internally by the OAuth API"""
    return session.get('github_token'), ''


def parse_pdf(record):
    """Prepares 'pdf' field as a relative URL to the fetch_pdf endpoint."""
    record['pdf'] = ''
    idx = 1
    while True:
        b64_plist_data = record.get('bdsk-file-' + str(idx), '')
        if b64_plist_data:
            plist = biplist.PlistReader(io.BytesIO(base64.b64decode(b64_plist_data)))
            filename = plist.parse()['$objects'][4]
            if os.path.exists(os.path.join(app.config['PDF_PATH'], filename)):
                record['pdf'] = url_for('fetch_pdf', filename=filename)
            idx += 1
        else:
            break
    return record


def parse_urls(record):
    """Prepares 'ads', 'doi', 'arxiv', 'url' fields as absolute URLs to external sites."""
    record['ads'] = ''

    # The ADS url is conventionally defined with its own keyword
    record['ads'] = record.get('adsurl', '')
    record['doi'] = ''
    record['arxiv'] = ''
    record['url'] = ''
    idx = 1

    # The arXiv url is encoded via the Eprint keyword
    if 'eprint' in record:
        record['arxiv'] = 'https://arxiv.org/abs/' + record['eprint'].lstrip('{').rstrip('}')

    while True:
        url = record.get('bdsk-url-' + str(idx), '')
        if url:
            if DOI_REGEX.match(url):
                if not record['doi']:
                    record['doi'] = url
            elif ARXIV_REGEX.match(url):
                if not record['arxiv']:
                    record['arxiv'] = url
            elif ADS_REGEX.match(url):
                if not record['ads']:
                    record['ads'] = url
            elif not record['url']:
                record['url'] = url
            idx += 1
        else:
            break
    return record


def __clean_names(names):
    """Replaced problematic latex characters in an author name"""
    for n in names:
        yield n.replace('{', '').replace('}', '').replace('~', '&nbsp;').replace(' ', '&nbsp;')


def parse_authors(record):
    """Prepares 'authors' field as a list of author names (last, initials)"""
    authors = record.get('author', '')
    record['authors'] = ''
    if authors:
        split = authors.replace('\n', ' ').split(" and ")
        record['authors'] = list(__clean_names(getnames([i.strip() for i in split])))
    return record


def parse_journal(record):
    """Prepares 'journal' keyword as a string"""
    journal = record.get('journal', '').strip()
    if not journal:
        journal = record.get('booktitle', '').strip()
    record['journal'] = journal
    return record


def process_record(record):
    """Generate custom record keys to be sent to the browser"""
    record = convert_to_unicode(record)
    record = parse_authors(record)
    record = parse_pdf(record)
    record = parse_urls(record)
    record = parse_journal(record)
    return record


def parse_bibtex():
    """Parses bibtex into json to send to the browser"""
    with open(app.config['BIBTEX_PATH']) as bibtex_file:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        database = parser.parse_file(bibtex_file)

    results = []
    export = bibtexparser.bibdatabase.BibDatabase()
    for entry in database.entries:
        export.entries = [{key: entry[key] for key in MINIMAL_BIBTEX_FIELDS if key in entry}]
        processed = process_record(entry)
        results.append({
            'title': processed.get('title', '').lstrip('{').rstrip('}'),
            'author': processed['authors'],
            'year': processed.get('year', ''),
            'journal': processed.get('journal', ''),
            'keywords': processed.get('keywords', ''),
            'ads': processed['ads'],
            'url': processed['url'],
            'doi': processed['doi'],
            'arxiv': processed['arxiv'],
            'pdf': processed['pdf'],
            'bib': bibtexparser.dumps(export).strip(),
            'abstract': processed.get('abstract', '')
        })

    return jsonify(results)


@app.route('/')
def input_display():
    """Main page route"""
    return render_template('table.html',
                           user_account=get_user_account(),
                           page_title=app.config['PAGE_TITLE'])


@app.route('/login')
def login():
    """Login route"""
    callback = url_for('input_display', _external=True)
    if 'next' in request.args:
        callback = request.args['next']

    return github.authorize(callback=callback)


@app.route('/logout')
def logout():
    """Logout route"""
    next_page = request.args['next'] if 'next' in request.args else url_for('input_display')
    token = session.pop('github_token', None)
    if token:
        with sqldb(app.config['DATABASE_PATH']) as cursor:
            cursor.execute('DELETE FROM sessions WHERE github_token = ?', (token,))
    return redirect(next_page)


@app.route('/query')
def query_papers():
    """Paper table JSON route"""
    user_account = get_user_account()
    if not user_account or not user_account['permission']:
        abort(403)

    try:
        return parse_bibtex()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        abort(500)


@app.route('/pdf/<path:filename>')
def fetch_pdf(filename):
    """PDF file route"""
    user_account = get_user_account()
    if not user_account or not user_account['permission']:
        abort(403)

    return send_from_directory(app.config['PDF_PATH'], filename)
