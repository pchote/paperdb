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

import base64
import io
import os
import re
import sys
import traceback
import bibtexparser

from bibtexparser.customization import getnames, convert_to_unicode
from biplist import PlistReader

from flask import abort
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import send_from_directory
from flask import url_for

BIBTEX_FILE = 'data/papers.bib'
PDF_DIRECTORY = 'data'

DOI_REGEX = re.compile(r'^http(s)?://(dx\.)?doi.org/.*$')
ARXIV_REGEX = re.compile('^http(s)?://arxiv.org/abs/.*$')
ADS_REGEX = re.compile('^http(s)?://adsabs.harvard.edu/abs/.*$')

def parse_pdf(record):
    """Prepares 'pdf' field as a relative URL to the fetch_pdf endpoint."""
    record['pdf'] = ''
    idx = 1
    while True:
        b64_plist_data = record.get('bdsk-file-' + str(idx), '')
        if b64_plist_data:
            plist = PlistReader(io.BytesIO(base64.b64decode(b64_plist_data)))
            filename = plist.parse()['$objects'][4]
            if os.path.exists(os.path.join(PDF_DIRECTORY, filename)):
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
    with open(BIBTEX_FILE) as bibtex_file:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.customization = process_record
        database = parser.parse_file(bibtex_file)

    results = []
    for entry in database.entries:
        results.append({
            'title': entry.get('title', '').lstrip('{').rstrip('}'),
            'author': entry['authors'],
            'year': entry.get('year', ''),
            'journal': entry.get('journal', ''),
            'keywords': entry.get('keywords', []),
            'ads': entry['ads'],
            'url': entry['url'],
            'doi': entry['doi'],
            'arxiv': entry['arxiv'],
            'pdf': entry['pdf'],
        })

    return jsonify(results)

app = Flask(__name__)

@app.route('/')
def input_display():
    """Main page route"""
    return render_template('table.html')

@app.route('/query')
def query_papers():
    """Paper table JSON route"""
    try:
        return parse_bibtex()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        abort(500)

@app.route('/pdf/<path:filename>')
def fetch_pdf(filename):
    """PDF file route"""
    return send_from_directory(PDF_DIRECTORY, filename)
