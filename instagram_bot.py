#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import requests
import os
import datetime
import json
import logging
import random


class InstagramBot(object):
    """
        Created on base of https://github.com/LevPasha/instabot.py
    """

    url = 'https://www.instagram.com/'
    url_likes = 'https://www.instagram.com/web/likes/%s/like/'
    url_login = 'https://www.instagram.com/accounts/login/ajax/'
    url_logout = 'https://www.instagram.com/accounts/logout/'
    url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
    url_user_detail = 'https://www.instagram.com/%s/?__a=1'

    user_agent = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 "
                  "YaBrowser/17.9.1.888 Yowser/2.5 Safari/537.36")
    accept_language = 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'

    log_file_path = ''
    log_file = 0

    def __init__(self, login, password, target, log_to_file=False):

        self.bot_start = datetime.datetime.now()

        self.user_login = login.lower()
        self.user_password = password
        self.target = target.split(',')
        self.login_status = False
        self.login_post = None
        self.csrftoken = None
        self.log_to_file = log_to_file
        self.s = requests.Session()
        now_time = datetime.datetime.now()
        log_string = 'InstagramBot started at %s:\n' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))

        if self.log_to_file:
            log_full_path = '%s%s.log' % (
                self.log_file_path, self.user_login)
            formatter = logging.Formatter('%(asctime)s - %(name)s '
                                          '- %(message)s')
            self.logger = logging.getLogger(self.user_login)
            hdrl = logging.FileHandler(log_full_path, mode='w')
            hdrl.setFormatter(formatter)
            self.logger.setLevel(level=logging.INFO)
            self.logger.addHandler(hdrl)
        self.write_log(log_string)

    def login(self):
        log_string = 'Trying to login as %s...\n' % self.user_login
        self.write_log(log_string)
        self.s.cookies.update({
            'sessionid': '',
            'mid': '',
            'ig_pr': '1',
            'ig_vw': '1920',
            'csrftoken': '',
            's_network': '',
            'ds_user_id': ''
        })
        self.login_post = {
            'username': self.user_login,
            'password': self.user_password
        }
        self.s.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': self.accept_language,
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': self.user_agent,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'
        })
        r = self.s.get(self.url)
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5 * random.random())
        login = self.s.post(
            self.url_login, data=self.login_post, allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.s.get('https://www.instagram.com/')
            finder = r.text.find(self.user_login)
            if finder != -1:
                self.login_status = True
                log_string = '%s login success!' % self.user_login
                self.write_log(log_string)
                return True
            else:
                self.login_status = False
                self.write_log('Login error! Check your login data!')
                return False
        else:
            self.write_log('Login error! Connection error!')
            return False

    def logout(self):
        work_time = datetime.datetime.now() - self.bot_start
        log_string = 'Bot work time: %s' % work_time
        self.write_log(log_string)

        try:
            logout_post = {'csrfmiddlewaretoken': self.csrftoken}
            self.s.post(self.url_logout, data=logout_post)
            self.write_log("Logout success!")
            self.login_status = False
        except Exception as e:
            self.write_log("Logout error! %s" % e)

    def like_all_users_media(self):
        """ Send http request to like target's feed """

        for target in self.target:
            try:
                resp = self.s.get(os.path.join(self.url, target))
                try:
                    data = json.loads(
                        resp.text.split("window._sharedData = ")[1]
                            .split(";</script>")[0]
                    )
                except IndexError:
                    # catch error when The link you followed may be broken
                    # or the page may have been removed
                    continue
                target_file = "%s.txt" % target
                if not data['entry_data']:
                    print(
                        'You are trying to access a closed account %s,'
                        ' currently this functional does not support' % target
                    )
                    continue
                profile_data = data['entry_data']['ProfilePage'][0]
                if not os.path.exists(target_file):
                    with open(target_file, 'w') as f:
                        already_liked_nodes = []
                else:
                    with open(target_file, 'r') as f:
                        already_liked_nodes = f.read().splitlines()

                with open(target_file, 'a') as f:
                    for media in profile_data['graphql']['user']['edge_owner_to_timeline_media']['edges']:
                        if media['node']['id'] not in already_liked_nodes:
                            if not self.login_status:
                                logged = self.login()
                                if not logged:
                                    return

                            media = self.s.get(self.url_media_detail % media['node']['shortcode'])
                            if media.status_code != 200:
                                self.write_log("Media request returned %d status code"
                                               % media.status_code)
                                continue
                            media_data = json.loads(media.text)
                            media_info = media_data['graphql']['shortcode_media']
                            if not media_info['viewer_has_liked']:
                                self.like(media_info['id'])
                                sleep_time = random.randint(5, 15)
                                self.write_log("Sleeping %d" % sleep_time)
                                time.sleep(sleep_time)
                            f.write(media_info['id'] + '\n')
            except Exception as e:
                self.write_log("An error occurred %s" % e)
            if self.login_status:
                self.logout()
        return

    def like(self, media_id):
        """ Send http request to like media by ID """
        if self.login_status:
            url_likes = self.url_likes % media_id
            try:
                res = self.s.post(url_likes)
                if res.status_code != 200:
                    if res.status_code == 400:
                        # in case you get banned sleep 5 minutes
                        time.sleep(60 * 5)
                        res = self.s.post(url_likes)
                        if res.status_code != 200:
                            self.write_log("Except on like! Status code %d"
                                           % res.status_code)
                            return
                self.write_log('Successfully liked %s' % media_id)

            except Exception as e:
                self.write_log("Except on like! %s" % e)
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
