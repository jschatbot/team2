#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import random
import sys

"""
python make_scenario.py 入力1 入力2
python make_scenario.py こんにちは はろおおおおおおおお

出力：シナリオのルール
BOS:BOS こんにちは:感動詞 EOS:EOS   はろおおおおおおおお
"""



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
    def rewrite(self, morphs):
        return requests.post(self.base+'/tk/rewrite', json={'rule': 'rewrite_c08.txt', 'morphs': morphs}, auth=self.auth, verify=False).json()['morphs']
        #return requests.post(self.base+'/tk/rewrite', data={'rule': 'rewrite_c08.txt', 'morphs': morphs}, auth=self.auth, verify=False).json()['morphs']

    # シナリオ変換器
    def trigger(self, morphs):
        return requests.post(self.base+'/tk/trigger', json={'rule': 'scenario_c08.txt', 'morphs': morphs}, auth=self.auth, verify=False).json()['texts']

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
        return requests.post(self.base+'/tweet/simple', data={'bot_name': name, 'message': message}, auth=self.auth, verify=False).json()['result'] == 'true'

    # リプライ送信
    def send_reply(self, name, mention_id, user_name, message):
        return requests.post(self.base+'/tweet/send_reply', json={'bot_name': name, 'replies': [{'mention_id': mention_id, 'user_name': user_name, 'message': message}]}, auth=self.auth, verify=False).json()[0] == 'true'


def to_chainform(morphs):
    return '%s:%s' % (morphs[u'norm_surface'],morphs[u'pos'])
    #morphs.map {|m| m['norm_surface'] + ':' + m['pos'] }


def to_string(chain):
    l = ''
    for w in chain[1:-1]:
        l += w.split(':')[0]
    return l
    #chain[1...-1].map {|m| m.split(/:/)[0] }.join


# 警告を無視するための設定
requests.packages.urllib3.disable_warnings()

# APIの設定
api = API('https://52.68.75.108')
api.basic_auth('secret', 'js2015cps')
name = 'js_devbot02'

mentions = []
mention = sys.argv[1].strip()
for sent in api.sentences(mention)['sentences']:
    for m in api.morphs(sent)['morphs']:
        mentions.append(to_chainform(m))
print "%s\t%s" % (' '.join(mentions), sys.argv[2].decode("utf-8"))
a=open("2_scenario2.txt","a")
st = " ".join(mentions)
st = st.split()[1:-1]
j=""
for i in st[:-1]:
    j+=i+" "
j+=st[-1]
st = "%s\t%s\n" % (j, sys.argv[2].decode("utf-8"))
a.write(st.encode("utf-8"))
a.close()


#print ' '.join(api.markov_chain({"surface":"ゴリラ", "norm_surface":"ゴリラ", "pos":"一般名詞"}))
#print ' '.join(api.rewrite(["BOS:BOS", "あたくし:代名詞", "EOS:EOS"]))
#print ' '.join(api.trigger(["BOS:BOS", "おはよう:感動詞", "EOS:EOS"]))

#print api.rewrite(["BOS:BOS", "むくり:感動詞", "EOS:EOS"]).text
