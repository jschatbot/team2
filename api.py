#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import random

class API:
    def __init__(self, base, proxy_host=None, proxy_port=None):
        self.base = base
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

    def basic_auth(self, user, passwd):
        self.auth = (user, passwd)

    # 指定された日本語文字列を分単位に分割する
    def sentences(self, s):
        return requests.get(self.base+'/jmat/sentence', params={'query': s}, auth=self.auth, verify=False).json()

    # 指定された日本語文字列を形態素に分割し品詞と正規化表記を付与する
    def morphs(self, s):
        return requests.get(self.base+'/jmat/morph', params={'query': s}, auth=self.auth, verify=False).json()

    # Markov連鎖生成器
    def markov_chain(self, seed):
        return requests.get(self.base+'/tk/markov', params={'surface': seed['norm_surface'].encode('utf-8'), 'pos': seed['pos'].encode('utf-8')}, auth=self.auth, verify=False).json()['morphs']

    # 形態素列書き換え器
    def rewrite(self, morphs, grade):
        if(grade == 0):
            fileName = "2_rewrite0.txt"
        if(grade == 1):
            fileName = "2_rewrite1.txt"
        if(grade == 2):
            fileName = "2_rewrite2.txt"
        print "\n".join(morphs)
        return requests.post(self.base+'/tk/rewrite', json={'rule': fileName, 'morphs': morphs}, auth=self.auth, verify=False).json()['morphs']
        #return requests.post(self.base+'/tk/rewrite', data={'rule': 'rewrite_c08.txt', 'morphs': morphs}, auth=self.auth, verify=False).json()['morphs']

    # シナリオ変換器
    def trigger(self, morphs, grade):
        if(grade == 0):
            fileName = "2_scenario0.txt"
        if(grade == 1):
            fileName = "2_scenario1.txt"
        if(grade == 2):
            fileName = "2_scenario2.txt"
        return requests.post(self.base+'/tk/trigger', json={'rule': fileName, 'morphs': morphs}, auth=self.auth, verify=False).json()['texts']

    # ツイート検索
    def search_tweet(self, query):
        return requests.get(self.base+'/search/tweet', params={'query': query, 'limit': 3}, auth=self.auth, verify=False).json()

    # リプライ検索
    def search_reply(self, query):
        return requests.get(self.base+'/search/reply', params={'query': query, 'limit': 3}, auth=self.auth, verify=False).json()

    # リプライ取得
    def get_reply(self, name):
        return requests.get(self.base+'/tweet/get_reply', params={'bot_name': name}, auth=self.auth, verify=False).json()

    # ツイート投稿
    def send_tweet(self, name, message):
        return requests.post(self.base+'/tweet/simple', json={'bot_name': name, 'message': message}, auth=self.auth, verify=False).json()['result'] == True

    # リプライ送信
    def send_reply(self, name, mention_id, user_name, message):
        return requests.post(self.base+'/tweet/send_reply', json={'bot_name': name, 'replies': [{'mention_id': mention_id, 'user_name': user_name, 'message': message}]}, auth=self.auth, verify=False).json()[0] == 'true'


