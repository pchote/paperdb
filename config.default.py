# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring

class PaperDBConfig(object):
    """Configuration for the papers database application"""
    PAGE_TITLE = 'Papers Database'

    # Path to the source .bib database
    BIBTEX_PATH = 'data/papers.bib'

    # Path to the directory containing pdf files referenced by the bib database
    PDF_PATH = 'data'

    # Path to the sqlite database used for user/session state
    # This will be created automatically with the correct schema if missing
    DATABASE_PATH = 'papers.db'

    # Random string used for encrypting cookie data
    # Generate using `python -c 'import os; print(os.urandom(16))'`
    SECRET_KEY = ''

    # OAuth integration tokens for GitHub
    # Create an OAuth App in your GitHub User/Organization settings
    # and then copy the Client ID and Client Secret here
    GITHUB_CLIENT_ID = ''
    GITHUB_CLIENT_SECRET = ''

    # GitHub user id for the initial user created on first run
    # This is the `id` value from https://api.github.com/users/<your user name>
    GITHUB_FOUNDER_ID = 0
