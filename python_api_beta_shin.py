#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import random
from api import * 

# 天気予報関係
import urllib2
import datetime
import xml.etree.ElementTree as ET

def to_chainform(morphs):
    return '%s:%s' % (morphs[u'norm_surface'],morphs[u'pos'])
    #morphs.map {|m| m['norm_surface'] + ':' + m['pos'] }


def to_string(chain):
    l = ''
    for w in chain[1:-1]:
        l += w.split(':')[0]
    return l
    #chain[1...-1].map {|m| m.split(/:/)[0] }.join


def build_tweet(mention, grade):
    print grade
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

    texts += api.trigger(mentions, grade)
    #print '\n'.join(texts)

    for s in seeds:
        #print api.search_tweet(s[u'norm_surface'])
        for t in api.search_tweet(s[u'norm_surface'])[u'texts']:
            for sent in api.sentences(t)['sentences']:
                texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']], grade)))
                #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))
        for t in api.search_reply(s[u'norm_surface'])[u'texts']:
            for sent in api.sentences(t)['sentences']:
                texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']], grade)))
                #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))

    random.shuffle(texts)
    print texts[0]
    return texts[0]

# 天気予報(東京)情報を取得するAPI
def get_weather():
    d = datetime.datetime.today()
    today = '{year}/{month}/{day}'.format(year=d.year, month=str(d.month).zfill(2), day=str(d.day).zfill(2))
    url  = "http://www.drk7.jp/weather/xml/13.xml"
    res = urllib2.urlopen(url)
    feed = res.read()
    tree = ET.fromstring(feed)
    weather = tree.findall(".//area[4]/info[@date='{date}']/weather".format(date=today))
    chance = tree.findall(".//area[4]/info[@date='{date}']/rainfallchance/period".format(date=today))
    temp = tree.findall(".//area[4]/info[@date='{date}']/temperature/range".format(date=today))
    return {"weather": weather[0].text.encode('utf-8'),
            "chance_am": int(chance[1].text),
            "chance_pm": int(chance[2].text),
            "chance_night": int(chance[3].text),
            "temp_high": int(temp[0].text),
            "temp_low": int(temp[1].text),
            "time": d.hour}

# 警告を無視するための設定
requests.packages.urllib3.disable_warnings()

# APIの設定
api = API('https://52.68.75.108')
api.basic_auth('secret', 'js2015cps')
name = 'js_devbot02'

if name:
    rs = api.get_reply(name)
    print rs
    weather = get_weather()
    grade = rs['grade']
    for r in rs['replies']:
        if u"天気" in r['text']:
            if weather["temp_high"] < 15:
                api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。ブルブル寒いから気をつけなさい！'.format(weather["temp_high"]))
            elif weather["temp_high"] > 25:
                api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。メラメラ暑いから気をつけなさい！'.format(weather["temp_high"]))
            elif u'雨' in weather["weather"]:
                api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨がザアザア降りそうだから傘を持っていったほうがいいよ！')
            else:
                api.send_reply(name, r['mention_id'], r['user_name'], '今日の天気は{}だよ！'.format(weather["weather"]))

        else:
            t = build_tweet(r['text'].strip().encode('utf-8'), grade)
            api.send_reply(name, r['mention_id'], r['user_name'], t) #t
else:
  pass
  #ARGF.each do |line|
  #  puts build_tweet(line.rstrip)


#print ' '.join(api.markov_chain({"surface":"ゴリラ", "norm_surface":"ゴリラ", "pos":"一般名詞"}))
#print ' '.join(api.rewrite(["BOS:BOS", "あたくし:代名詞", "EOS:EOS"]))
#print ' '.join(api.trigger(["BOS:BOS", "おはよう:感動詞", "EOS:EOS"]))

#print api.rewrite(["BOS:BOS", "むくり:感動詞", "EOS:EOS"]).text
