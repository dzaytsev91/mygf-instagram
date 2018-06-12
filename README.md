## What is it?

This is instagram bot for liking your girlfriend's instagram posts, just put it
script in cron and you don't waste your time checking feed.

Written in python 3.

## Configurations

Just call InstagramBot with 3 arguments

* `login` - your login;
* `password` - your password;
* `target` - Instagram account name of your gf.

## How to install and run:

1) Clone this repo.
2) Create virtual env.
3) To install the project's dependencies, run command `pip install -r
   requirements.txt`.

## Usage

#### Example of usage:

Just change password, login and target.

```bash
    virtualenv -p python3 venv
    . venv/bin/activate
    pip install -r requirements.txt
    python example.py login password gf_account_name
```

If you want to like more than one account, just pass it with comma separated, for example
```bash
    python example.py login password gf_account_name,second_gf_account_name
```

## Currently not supported
Possibility to like a closed account

## Plans

1) Add possibility to like random images
2) Send me all images that bot liked to messenger that I can check when it will
   be time for this
