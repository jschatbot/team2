#!/usr/bin/python
# coding:utf-8

"""
sentences distant system using word2vec
"""
__author__ = "shin"
__version__ = "1"
__date__ = "2015/12/07"

import sys
#import MeCab
import re
import numpy as np
from gensim.models import word2vec
import pickle

model_file = '../model/matrix50.model'
dialog_file = '../model/NTCIR.wakati'

class sentence_vectorizer:
    """
    sentence vector のためのクラス
    """
    def __init__(self, model_file):
        """
        コンストラクタ
        model: gensimで作成したmodelのfile_name
        """
        self.model = word2vec.Word2Vec.load(model_file)
#        self.meca_tag = MeCab.Tagger("mecabrc")

    def make_vector(self, sent):
        """
        input: sentence
        output: sentence_vector
        """
        #tagger = MeCab.Tagger('-Owakati')
        #result = tagger.parse(sent)
        #words = result.strip().split(' ')
        #words = self.do_mecab(sent)
        #print sent
        words = sent.split(' ')
        sent_len = len(words)
        sentence_vector = np.zeros(25)
        for word in words:
            word = word.decode("utf-8")
            try:
                sentence_vector += self.model[word]
            except(KeyError):
                #print "%s is OOV (Out Of Vocabrary)" % word
                sent_len -= 1
        sentence_vector /= sent_len + 0.0001
        return sentence_vector, sent_len

    def cos(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def use_database(self, dialog_file, input_sentence):
        database = dict()
        for line in open(dialog_file):
            sent = line.strip().split('\t')
            if len(sent) < 2: continue 
            vec, sent_len = self.make_vector(sent[0]+sent[1])
            database[sent[-1]] = (vec, sent_len)

        input_vector, _ = self.make_vector(input_sentence)
        max_cos_similality, second, thord = 0.0, 0.0, 0.0
        best_ans, second_ans, thord_ans = str(), str(), str()
        for sent, dbvector_len in database.items():
            db_vector, sent_len = dbvector_len
            cos_similality = self.cos(input_vector, db_vector)
            cos_similality = cos_similality * 100 / (100 + sent_len)
            if cos_similality > max_cos_similality:
                max_cos_similality = cos_similality
                best_ans = sent
                #print sent
            elif cos_similality > second:
                second = cos_similality
                second_ans = sent
            elif cos_similality > thord:
                thord = cos_similality
                thord_ans = sent
        #print [(best_ans, max_cos_similality), (second_ans, second), (thord_ans, thord)]
        #return [(best_ans, max_cos_similality), (second_ans, second), (thord_ans, thord)]
        return [best_ans, second_ans, thord_ans]

#    def do_mecab(self, tweet_text):     # １行受けたら内容語のbowのリストを返す
#        text_wakati = []
#        itemlist    = self.meca_tag.parse(tweet_text)
#        itemlist2    = itemlist.strip().split('\n')
#        for item in itemlist2:
#            if item == "EOS" or item == "": break
#            item2 = item.strip().split("\t")
#            if len(item2) == 1: continue
#            surface = item2[0]
#            #pos   = item2[1].split(",")[0]
#            #if pos == "名詞" or pos == "動詞" or pos == "形容詞" or pos == "副詞":
#            text_wakati.append(surface)
#        return text_wakati



if __name__ == "__main__":
    # load
    print "model loading..."
    #model = word2vec.Word2Vec.load(dialog_file)
    # test
    SV = sentence_vectorizer(model_file)
    #konnitiwa_vec, _ = SV.make_vector("こんにちは世界")
    #print "こんにちは世界", konnitiwa_vec
    print SV.use_database(dialog_file, "おはようございます。朝ですね。")

    # dialog system
    #while(True):
    #    print "your utterance: ",
    #    input_sentence = raw_input()
    #    input_vector, _ = SV.make_vector(input_sentence)
    #    max_cos_similality = 0.0
    #    best_answer = str()
    #    for sent, dbvector_len in database.items():
    #        db_vector, sent_len = dbvector_len
    #        #cos_similality = sp.spatial.distance.cosine(input_vector, db_vector)
    #        cos_similality = SV.cos(input_vector, db_vector)
    #        cos_similality = cos_similality * 100 / (100 + sent_len)
    #        if cos_similality > max_cos_similality:
    #            max_cos_similality = cos_similality
    #            best_answer = sent
    #    print "machine answer: %s\t%f" % (best_answer, max_cos_similality)
