#!/usr/bin/env python

import datetime
import json
import logging
import os
import random
import time

import requests
from instagram_private_api import Client
from user_agent import generate_user_agent

from constraint import (
    BASE_URL,
)


class InstagramBot:
    """
    Created on base of https://github.com/LevPasha/instabot.py
    """

    accept_language = "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 "
        "Safari/605.1.15"
    )

    def __init__(self, login, password, target, log_to_file=False):

        self.bot_start = datetime.datetime.now()
        self.user_login = login.lower()
        self.password = password
        self.user_password = password
        self.target = target.split(",")
        self.login_post = None
        self.user_login = login
        self.password = password
        self.csrftoken = None
        self.client = None
        self.log_to_file = log_to_file
        self.session = requests.Session()
        self.session.cookies.update(
            {
                "sessionid": "",
                "mid": "",
                "ig_pr": "1",
                "ig_vw": "1920",
                "csrftoken": "",
                "s_network": "",
                "ds_user_id": "",
            }
        )
        self.session.headers.update(
            {
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": self.accept_language,
                "Connection": "keep-alive",
                "Content-Length": "0",
                "Host": "www.instagram.com",
                "Origin": "https://www.instagram.com",
                "Referer": "https://www.instagram.com/accounts/login/",
                "User-Agent": generate_user_agent(),
                "X-Instagram-AJAX": "1",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        if self.log_to_file:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(message)s",
            )
            self.logger = logging.getLogger(self.user_login)
            hdrl = logging.FileHandler(f"{self.user_login}.log", mode="w")
            hdrl.setFormatter(formatter)
            self.logger.setLevel(level=logging.INFO)
            self.logger.addHandler(hdrl)

    def login(self):
        self.client = Client(self.user_login, self.password)

    def writer_file(self, target_file, profile_data, already_liked_nodes):
        with open(target_file, "a") as f:
            for media in profile_data["graphql"]["user"][
                "edge_owner_to_timeline_media"
            ][
                "edges"
            ]:  # noqa
                if media["node"]["id"] not in already_liked_nodes:
                    if not self.client:
                        self.login()
                    data = self.client.media_info(media["node"]["id"])
                    if not data["items"][0]["has_liked"]:
                        self.client.post_like(data["items"][0]["id"])
                        sleep_time = random.randint(5, 15)
                        self.write_log("Sleeping %d" % sleep_time)
                        time.sleep(sleep_time)
                    f.write(media["node"]["id"] + "\n")

    def like_all_users_media(self):
        """ Send http request to like target's feed """
        for target in self.target:
            try:
                resp = self.session.get(
                    os.path.join(BASE_URL, target),
                    headers={"User-agent": self.user_agent},
                )
                try:
                    data = json.loads(
                        resp.text.split("window._sharedData = ")[1].split(
                            ";</script>"
                        )[0],
                    )
                except IndexError:
                    # catch error when The link you followed may be broken
                    # or the page may have been removed
                    continue
                target_file = f"{target}.txt"
                if not data["entry_data"]:
                    self.logger.warning(
                        "You are trying to access a closed account %s,"
                        " currently this functional does not support" % target,
                    )
                    continue
                profile_data = data["entry_data"]["ProfilePage"][0]
                if not os.path.exists(target_file):
                    with open(target_file, "w"):
                        already_liked_nodes = []
                else:
                    with open(target_file) as f:
                        already_liked_nodes = f.read().splitlines()

                self.writer_file(
                    target_file, profile_data, already_liked_nodes
                )

            except Exception as e:
                self.write_log("An error occurred %s" % e)
        return

    def write_log(self, log_text):
        if self.log_to_file:
            try:
                self.logger.info(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")
        else:
            try:
                print(log_text)
            except UnicodeEncodeError:
                print("Your text has unicode problem!")
