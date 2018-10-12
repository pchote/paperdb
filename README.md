A Flask + Bootstrap + jQuery frontend for a BibDesk paper database

# Installation

Copy the ```config.default.py``` file to ```config.py``` and edit the file with the following settings:

```sh
$> cd paperdb
$> cp config.default.py config.py
```

Edit the config.py file and include the following information

## Secret Key

Generate a secret key using

```sh
$> python -c 'import os; print(os.urandom(16))'
```

add the key to ```SECRET_KEY```, e.g:

```sh
SECRET_KEY = b'\x01w\x85\xb4\x07\x8a\xb1\xe8<(\xbd\xbce\xc2\xb3B'
```

## GitHub OAuth

Create an OAuth App in your GitHub User/Organization settings
and then fill out the ```GITHUB_CLIENT_ID``` and ```GITHUB_CLIENT_SECRET``` fields, e.g:

```sh
GITHUB_CLIENT_ID = '2493k6f960f06qws373d'
GITHUB_CLIENT_SECRET = 'b0b0d01d34ab981083sc34a8fde987a744860bb6'
```

## GitHub Founder ID

Determine your GitHub user ID. This is the ```id``` value from ```https://api.github.com/users/<your user name>```, e.g:

```json
{
  "login": "jmccormac01",
  "id": 1912007,
  "node_id": "MDQ6VXNlcjE5MTIwMDc=",
  "avatar_url": "https://avatars3.githubusercontent.com/u/1912007?v=4",
  "gravatar_id": "",
  "url": "https://api.github.com/users/jmccormac01",
  "html_url": "https://github.com/jmccormac01",
  "followers_url": "https://api.github.com/users/jmccormac01/followers",
  "following_url": "https://api.github.com/users/jmccormac01/following{/other_user}",
  "gists_url": "https://api.github.com/users/jmccormac01/gists{/gist_id}",
```

Enter the ```id``` value into ```config.py```

```sh
GITHUB_FOUNDER_ID = 1912007
```

# Usage

Run the paper database server locally using:
```
export FLASK_APP=paperdb
python -m flask run
```

# Contributors


# License
