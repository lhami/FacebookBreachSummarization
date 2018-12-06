# -*- coding: utf-8 -*-
'''
This uses the Lesk algorithm for word sense disambiguation, using the wordnet
dictionary. The Lesk algorithm needs each word to still be associated with a
sentence to disambiguate senses, hence the structuring of the lists.

Modified to include lemmatizing words before finding their synsets
'''


#Fix encoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json 

import time
from multiprocessing import Pool

import nltk
from nltk.corpus import wordnet as wn
from nltk.probability import FreqDist
from nltk.wsd import lesk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

path = "../jusText_Cleaning_Code/cleaned.json"


def penn2morphy(penntag, returnNone=False):
	#default nltk pos_tags are not compatible with wordnet functions
	morphy_tag = {'NN':wn.NOUN, 'JJ':wn.ADJ,
				  'VB':wn.VERB, 'RB':wn.ADV}
	try:
		return morphy_tag[penntag[:2]]
	except:
		return None if returnNone else ''

def get_stopwords():
	#the default stopwords list isn't quite sufficient
	nltk_defaults = stopwords.words('english')
	punctuation = [',', ':', '.', ';', '-', '"', '--', '!', '?', '(', ')', '``', '\'\'']
	custom_words = ['would', 'though', 'it', 'still', 'he', 'at', 'even', 'but', 'like', 'upon', 'a']
	return set(nltk_defaults + punctuation + custom_words)

def get_input():
	stop_words = get_stopwords()
	print "Reading Input JSON..."
	with open(path) as f:
		content = f.readlines()
	content = [(json.loads(x.lower()), stop_words) for x in content]
	print "Done loading json!"
	return content


def mostcommonsyns(row):
	#print "Evaluating new row"
	record, stop_words = row
	text = record['text']
	#print "------------------\n\n", text
	#print "hi len: ", len(text)
	stopWords = get_stopwords()
	sentList = nltk.sent_tokenize(text)
	wordsInSentsPos = [nltk.pos_tag(nltk.word_tokenize(s)) for s in sentList]
	wordsInSentsWnPos = [[(w[0],penn2morphy(w[1])) for w in s if w[0].lower() not in stopWords] for s in wordsInSentsPos]
	#the above returns a list of sentences where each sentence is a list of
	#(word-as-string, pos tag) tuples. Stop words are removed here because pos_tag
	#uses grammatical structure but lesk does not. 

	#lemmatization
	lmtzr = WordNetLemmatizer()
	for sent in wordsInSentsWnPos:
		for indx, tup in enumerate(sent):
			#word = tup[0], pos = tup[1]
			if tup[1] != '': #if pos exists, reset word to lemma
				word = lmtzr.lemmatize(tup[0], tup[1])
        			#if pos tagger failed, keep original word
				newtup = (word, tup[1])
				#print tup[0], tup[1], " -- ", newtup
				sent[indx] = newtup		

	synsetsList = [lesk(s,w[0],w[1]) for s in wordsInSentsWnPos for w in s]
	#print "go"
	#print synsetsList, "\n\n"
	#return [3,2,2,2]

	#res = FreqDist([x for x in synsetsList if x is not None])
	res = [s.name() for s in synsetsList if s is not None]
	return res

def fnn():
	st = time.time()
	print "Start Time: ", st
	documents = get_input()
	#documents = documents[:2]

	print "Length: ", len(documents)
	#individual_results = [ mostcommonsyns(record) for record in documents ]

	p = Pool(15)
	individual_results = p.map(mostcommonsyns, documents)

	final_results = compile_results(individual_results)
	
	end = time.time()
	print "End Time: ", end-st

	print "Final Results"
	for key, value in final_results.most_common(50):
		print wn.synset(key).lemma_names(), value


def compile_results(addends):
	#print "ayy", addends
	running = FreqDist()
	for x in addends:
		running = running + FreqDist(x)
	return running


fnn()
