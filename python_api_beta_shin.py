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
# 定期ツイート
import random

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
            texts.append(to_string(api.rewrite(c, grade)))

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

def get_time():
    d = datetime.datetime.today()
    return {
        "year": int(d.year), 
        "month": int(d.month),
        "day": int(d.day),
        "hour": int(d.hour),
        "min": int(d.minute),
        "sec": int(d.second)}

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

# 履歴取得関係
history = {}
for line in open('history.txt', 'r'):
    item = line[:-1].split(',')
    history[item[0]] = int(item[1])

def get_history(user_name):
    if user_name not in history:
        return 0
    else:
        return history[user_name]

def update_history():
    f = open('history.txt', 'w')
    for name, times in history.iteritems():
        f.write('{}, {}\n'.format(name, times))
    f.close()



# 警告を無視するための設定
requests.packages.urllib3.disable_warnings()

# APIの設定
api = API('https://52.68.75.108')
api.basic_auth('secret', 'js2015cps')
name = 'js_devbot02'


time = get_time()
if time["min"] != 99:
    if time["month"]==12 and (time["day"]==24 or time["day"]==25):
        message = [
        "メリークリスマス～♪",
        "サンタさーん！！",
        "プレゼント欲しい人ー！",
        "今日はデートです♪みなさんは何するんですか？？",
        "あたしとデートしてくれる人ー！？"]
        api.send_tweet('js_devbot02', random.choice(message))
    elif time["month"]==1 and time["day"]>=1 and time["day"]<=3:
        message = [
        "あけましておめでとうございます！！",
        "良いお年を！！",
        "お年玉欲しい人ー！！？？",
        "初詣は行ったかーい？？",
        "今年もよろしくお願いします！",
        "もうそろそろあたし消えちゃうよ～～"]
        api.send_tweet('js_devbot02', random.choice(message))
    else:
        message = [
        "「天気」とリプすると、天気予報するよ！",
        "話しかけると、色々反応するよ！",
        "気軽に話しかけてね！",
        "暇だよー話かけて～～",
        "話しかけまくると進化するよ！！",
        "進化はしてからのお楽しみ♪",
        "人工知能の試験中です！協力してね！！",
        "人工知能ってかっこいいよね！そう思わん？",
        "寒いよーー",
        "眠いよー",
        "あたしって攻撃的かなぁ？",
        "疲れたらあたしに相談しな？",
        "おなかすいてない？",
        "いつ帰ってくるのー？",
        "起きたらまずあたしに連絡ね！！",
        "リプを送るとポイントが溜まっていくよ！"]
        if time["hour"] >= 22:
            message.append("寝るときはちゃんと連絡しなさい！！")
        api.send_tweet('js_devbot02', random.choice(message))

# 履歴取得サンプル
#rs = api.get_reply(name)
#for r in rs['replies']:
#    if r['user_name'] not in history:
#        history[r['user_name']] = 1
#    else:
#        history[r['user_name']] += 1
#        api.send_reply('js_devbot02', r['mention_id'], r['user_name'], "{}回目のリプだね。あたしのことそんなに好き？".format(history[r['user_name']]))
#
#update_history()

## 天気関係サンプル
#if name:
#    rs = api.get_reply(name)
#    print rs
#    weather = get_weather()
#    grade = rs['grade']
#    for r in rs['replies']:
#        if u"天気" in r['text']:
#            if grade >= 1:
#                if weather["temp_high"] < 15:
#                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。ブルブル寒いから気をつけなさい！'.format(weather["temp_high"]))
#                elif weather["temp_high"] > 25:
#                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。メラメラ暑いから気をつけなさい！'.format(weather["temp_high"]))
#                elif weather["chance_night"] > 30:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨がザアザア降りそうだから傘を持っていったほうがいいよ！')
#                else:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '天気予報を調べておいたよ！今日の東京の天気は{}。最低気温は{}℃、最高気温は{}℃だよ！'.format(weather["weather"], weather["temp_low"], weather["temp_high"]))
#            else:
#                if weather["temp_high"] < 15:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '今日の最高気温は{}℃だつぼ。つぼにこもるのがおすすめだつぼ。'.format(weather["temp_high"]))
#                elif weather["temp_high"] > 25:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '今日の最高気温は{}℃だつぼ。つぼの中が蒸し暑いつぼ。'.format(weather["temp_high"]))
#                elif weather["chance_night"] > 30:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨が降りそうだつぼ。つぼの中が水浸しになっちゃうつぼ。')
#                else:
#                    api.send_reply(name, r['mention_id'], r['user_name'], '今日の天気予報だつぼ！今日の東京の天気は{}。最低気温は{}℃、最高気温は{}℃だつぼ！'.format(weather["weather"], weather["temp_low"], weather["temp_high"]))
#
#        else:
#            t = build_tweet(r['text'].strip().encode('utf-8'), grade)
#            api.send_reply(name, r['mention_id'], r['user_name'], t) #t
#else:
#  pass
