#!/usr/bin/env python
"""This is a simple example of usage. Just pass login and password of your
instagram account and account name of your GF.
"""

import click

from instagram_bot import InstagramBot


@click.command(help=__doc__)
@click.argument("login", type=str)
@click.argument("password", type=str)
@click.argument("gf-account", type=str)
def main(login, password, gf_account):
    bot = InstagramBot(login=login, password=password, target=gf_account)
    bot.like_all_users_media()


if __name__ == "__main__":
    main()
