#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import random
#import tweepy
from api import * 

# 天気予報関係
import urllib2
import datetime
import xml.etree.ElementTree as ET
# 定期ツイート
import random
#word2vec関係
import w2v_dialog

def to_chainform(morphs):
    return '%s:%s' % (morphs[u'norm_surface'],morphs[u'pos'])
    #morphs.map {|m| m['norm_surface'] + ':' + m['pos'] }


def to_string(chain):
    l = ''
    for w in chain[1:-1]:
        l += w.split(':')[0]
    return l
    #chain[1...-1].map {|m| m.split(/:/)[0] }.join

def get_name(username):
    consumer_key = "zZ2LrsIRPtgRfC9hCshRItf4N"
    consumer_secret = "t5zCvheQNu2nYjd1Kovh0jo970pnV5xt4AolrxMcBTCoXs8eWL"
    access_token = "4445286687-w2Zar27rxyfKSbQcMhyUhS1RmVU5UE8A52vvqrY"
    access_secret = "bXVd3ZcUSsu44KKFdHE1W1cin96sp02XdMlfmt5tk2AAp"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)
    api = tweepy.API(auth)
    user = get_user(username)
    return user.screen_name

def build_tweet(mention, grade):
    print grade
    seeds = []
    mentions = []

    mentions1 = []
    for m in api.morphs(api.sentences(r['text'])['sentences'][0])['morphs']:
        mentions1.append(to_chainform(m).split(':')[0])
    r_now = ' '.join(mentions1)[4:-4]
    SV = w2v_dialog.sentence_vectorizer('matrix25.w7.model')
    w2v_list = SV.use_database('NTCIR.wakati.u20', r_now.encode('utf-8'))
    seeds.append(''.join(w2v_list[0].split()))
    seeds.append(''.join(w2v_list[1].split()))
    seeds.append(''.join(w2v_list[2].split()))
    #print r['text']
    print "w2v_list", '\n'.join(w2v_list)
    #api.send_reply(name, r['mention_id'], r['user_name'], ''.join(w2v_list[0].split()))


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
            pass
            #print s[u'norm_surface']
            #c = api.markov_chain(s)
            #texts.append(to_string(api.rewrite(c, grade)))
    print " ".join(mentions)
    trigger_result = api.trigger(mentions, grade)
    texts += trigger_result
    texts += trigger_result
    texts += trigger_result
    print '\n'.join(trigger_result)

    for s in seeds:
        pass
        #print api.search_tweet(s[u'norm_surface'])
        #for t in api.search_tweet(s[u'norm_surface'])[u'texts']:
        #    for sent in api.sentences(t)['sentences']:
        #        texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']], grade)))
        #        #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))
        #for t in api.search_reply(s[u'norm_surface'])[u'texts']:
        #    for sent in api.sentences(t)['sentences']:
        #        texts.append(to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']], grade)))
                #print to_string(api.rewrite([to_chainform(m) for m in api.morphs(sent)['morphs']]))

    texts = seeds
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

# 天気関係サンプル
if name:
    rs = api.get_reply(name)
    print rs
    weather = get_weather()
    grade = rs['grade']
    grade = 2
    for r in rs['replies']:
        if u"天気" in r['text']:
            if(grade == 2):
                if weather["temp_high"] < 15:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。ブルブル寒いから気をつけなさい！'.format(weather["temp_high"]))
                elif weather["temp_high"] > 25:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。メラメラ暑いから気をつけなさい！'.format(weather["temp_high"]))
                elif weather["chance_night"] > 30:
                    api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨がザアザア降りそうだから傘を持っていったほうがいいよ！')
                else:
                    api.send_reply(name, r['mention_id'], r['user_name'], '天気予報を調べておいたよ！今日の東京の天気は{}。最低気温は{}℃、最高気温は{}℃だよ！'.format(weather["weather"], weather["temp_low"], weather["temp_high"]))
            if(grade == 1):
                if weather["temp_high"] < 15:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。ブルブル寒いから気をつけなさい！カチカチッ♪'.format(weather["temp_high"]))
                elif weather["temp_high"] > 25:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あんたのために天気予報を見たら最高気温は{}℃だったよ。メラメラ暑いから気をつけなさい！カチカチッ♪'.format(weather["temp_high"]))
                elif weather["chance_night"] > 30:
                    api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨がザアザア降りそうだから傘を持っていったほうがいいよ！カチカチッ♪')
                else:
                    api.send_reply(name, r['mention_id'], r['user_name'], '天気予報を調べておいたよ！今日の東京の天気は{}。最低気温は{}℃、最高気温は{}℃だよ！カチカチッ♪'.format(weather["weather"], weather["temp_low"], weather["temp_high"]))
            if(grade == 0):
                if weather["temp_high"] < 15:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あなたのために天気予報を見たら最高気温は{}℃だったつぼ。ブルブル寒いから気をつけてくださいつぼ！'.format(weather["temp_high"]))
                elif weather["temp_high"] > 25:
                    api.send_reply(name, r['mention_id'], r['user_name'], 'あなたのために天気予報を見たら最高気温は{}℃だったつぼ。メラメラ暑いから気をつけてくださいつぼ！'.format(weather["temp_high"]))
                elif weather["chance_night"] > 30:
                    api.send_reply(name, r['mention_id'], r['user_name'], '今日は雨がザアザア降りそうだから傘を持っていったほうがいいつぼ！')
                else:
                    api.send_reply(name, r['mention_id'], r['user_name'], '天気予報を調べておいたつぼ！今日の東京の天気は{}。最低気温は{}℃、最高気温は{}℃つぼ！'.format(weather["weather"], weather["temp_low"], weather["temp_high"]))
        else:
            t = build_tweet(r['text'].strip().encode('utf-8'), grade)
            api.send_reply(name, r['mention_id'], r['user_name'], t) #t
else:
  pass

time = get_time()
if time["min"] != 0:
    if time["month"]==12 and (time["day"]==24 or time["day"]==25):
        message = [
        [
         "メリークリスマス～♪つぼ！",
         "サンタさーんつぼ！つぼ！つぼ！",
         "プレゼント欲しい人ーつぼ！つぼ！",
         "今日はデートですつぼ♪みなさんは何するんですかつぼ？？つぼ！",
         "つぼとデートしてくれる人ーつぼ！？"],
         [
          "メリークリスマス～♪カチカチッ♪",
          "サンタさーん！！カチカチッ♪",
          "プレゼント欲しい人ー！カチカチッ♪",
          "今日はデートです♪みなさんは何するんですか？？カチカチッ♪",
          "あたしとデートしてくれる人ー！？カチカチッ♪"],
          [
        "メリークリスマス～♪",
        "サンタさーん！！",
        "プレゼント欲しい人ー！",
        "今日はデートです♪みなさんは何するんですか？？",
        "あたしとデートしてくれる人ー！？"]]
        api.send_tweet('js_devbot02', random.choice(message[grade]))
    elif time["month"]==1 and time["day"]>=1 and time["day"]<=3:
        message = [
        [
         "あけましておめでとうございますつぼ！つぼ！つぼ！",
         "良いお年をつぼ！つぼ！つぼ！",
         "お年玉欲しい人ーつぼ！つぼ！？？つぼ！",
         "初詣は行ったかーい？？つぼ！",
         "今年もよろしくお願いしますつぼ！つぼ！",
         "もうそろそろ消えちゃうよ～～つぼ～～"],
          [
          "あけましておめでとうございます！！カチカチッ♪",
          "良いお年を！！カチカチッ♪",
          "お年玉欲しい人ー！！？？カチカチッ♪",
          "初詣は行ったかーい？？カチカチッ♪",
          "今年もよろしくお願いします！カチカチッ♪",
          "もうそろそろあたし消えちゃうよ～～カチカチッ♪"],
          [
        "あけましておめでとうございます！！",
        "良いお年を！！",
        "お年玉欲しい人ー！！？？",
        "初詣は行ったかーい？？",
        "今年もよろしくお願いします！",
        "もうそろそろあたし消えちゃうよ～～"]]
        api.send_tweet('js_devbot02', random.choice(message[grade]))
    else:
        message = [
         ["「天気」とリプすると、天気予報するよつぼ！つぼ！",
         "話しかけると、色々反応するよつぼ！つぼ！",
         "気軽に話しかけてねつぼ！つぼ！",
         "暇だよー話かけて～～つぼ！",
         "話しかけまくると進化するよつぼ！つぼ！つぼ！",
         "進化はしてからのお楽しみ♪つぼ！",
         "人工知能の試験中ですつぼ！協力してねつぼ！つぼ！つぼ！",
         "人工知能ってかっこいいよねつぼ！そう思わん？つぼ！",
         "寒いよーーつぼ！",
         "眠いよーつぼ！",
         "つぼって攻撃的かなぁ？つぼ！",
         "疲れたらに相談しな？つぼ！",
         "おなかすいてない？つぼ！",
         "いつ帰ってくるのー？つぼ！",
         "起きたらまずに連絡ねつぼ！つぼ！つぼ！",
         "リプを送るとポイントが溜まっていくよつぼ！"],
          [
          "「天気」とリプすると、天気予報するよ！カチカチッ♪",
          "話しかけると、色々反応するよ！カチカチッ♪",
          "気軽に話しかけてね！カチカチッ♪",
          "暇だよー話かけて～～カチカチッ♪",
          "話しかけまくると進化するよ！！カチカチッ♪",
          "進化はしてからのお楽しみ♪カチカチッ♪",
          "人工知能の試験中です！協力してね！！カチカチッ♪",
          "人工知能ってかっこいいよね！そう思わん？カチカチッ♪",
          "寒いよーーカチカチッ♪",
          "眠いよーカチカチッ♪",
          "あたしって攻撃的かなぁ？カチカチッ♪",
          "疲れたらあたしに相談しな？カチカチッ♪",
          "おなかすいてない？カチカチッ♪",
          "いつ帰ってくるのー？カチカチッ♪",
          "起きたらまずあたしに連絡ね！！カチカチッ♪",
          "リプを送るとポイントが溜まっていくよ！カチカチッ♪"],
          [
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
        "リプを送るとポイントが溜まっていくよ！"]]
        if time["hour"] >= 22:
            message.append("寝るときはちゃんと連絡しなさい！！")
        api.send_tweet('js_devbot02', random.choice(message[grade]))

# 履歴取得サンプル
rs = api.get_reply(name)
for r in rs['replies']:
    if r['user_name'] not in history:
        history[r['user_name']] = 1
    else:
        history[r['user_name']] += 1
        print history[r['user_name']]
        if(history[r['user_name']] % 10 == 0):
            if(grade == 0):
                api.send_reply('js_devbot02', r['mention_id'], r['user_name'], "{}回目のリプだつぼ。こんなに話しかけてくれてありがとうつぼ！".format(history[r['user_name']]))
            if(grade == 1):
                api.send_reply('js_devbot02', r['mention_id'], r['user_name'], "{}回目のリプだね。あたしのことそんなに好き？カチッカチッ♩".format(history[r['user_name']]))
            if(grade == 2):
                api.send_reply('js_devbot02', r['mention_id'], r['user_name'], "{}回目のリプだね。あたしのことそんなに好き？".format(history[r['user_name']]))

update_history()
