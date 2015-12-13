#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import random
from api import * 

def to_chainform(morphs):
    return '%s:%s' % (morphs[u'norm_surface'],morphs[u'pos'])
    #morphs.map {|m| m['norm_surface'] + ':' + m['pos'] }


def to_string(chain):
    l = ''
    for w in chain[1:-1]:
        l += w.split(':')[0]
    return l
    #chain[1...-1].map {|m| m.split(/:/)[0] }.join


def build_tweet(mention):
    seeds = []
    mentions = []
    for sent in api.sentences(mention)['sentences']:
        for m in api.morphs(sent)['morphs']:
            mentions.append(to_chainform(m))
            if m['pos'][-2] == u'名' and m['pos'] != u'代名詞' :
                #print m
                seeds.append(m)
        #print seeds
    texts = []
    for _ in range(0, 5):
        if not seeds: seeds = [{ u'norm_surface': u'BOS', u'pos': u'BOS' }]
        for s in seeds:
            #print s[u'norm_surface']
            c = api.markov_chain(s)
            texts.append(to_string(api.rewrite(c)))

    texts += api.trigger(mentions)
    #print '\n'.join(texts)

    for s in seeds:
        #print api.search_tweet(s[u'norm_surface'])
        for t in api.search_tweet(s[u'norm_surface'])[u'texts']:
            for sent in api.sentences(t)['sentences']:
                texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']])))
                #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))
        for t in api.search_reply(s[u'norm_surface'])[u'texts']:
            for sent in api.sentences(t)['sentences']:
                texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']])))
                #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))

    random.shuffle(texts)
    print texts[0]
    return texts[0]


# 警告を無視するための設定
requests.packages.urllib3.disable_warnings()

# APIの設定
api = API('https://52.68.75.108')
api.basic_auth('secret', 'js2015cps')
name = 'js_devbot02'


if name:
    rs = api.get_reply(name)
    print rs
    for r in rs['replies']:
        t = build_tweet(r['text'].strip().encode('utf-8'))
        api.send_reply(name, r['mention_id'], r['user_name'], t) #t
else:
  pass
  #ARGF.each do |line|
  #  puts build_tweet(line.rstrip)


#print ' '.join(api.markov_chain({"surface":"ゴリラ", "norm_surface":"ゴリラ", "pos":"一般名詞"}))
#print ' '.join(api.rewrite(["BOS:BOS", "あたくし:代名詞", "EOS:EOS"]))
#print ' '.join(api.trigger(["BOS:BOS", "おはよう:感動詞", "EOS:EOS"]))

#print api.rewrite(["BOS:BOS", "むくり:感動詞", "EOS:EOS"]).text
