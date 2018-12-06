'''
Lemmatizes the word list.
Then gives a list of most frequent words based on the lemmas.

'''

import nltk
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import json
from multiprocessing import Pool
from collections import Counter

import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

input_file_path = "../jusText_Cleaning_Code/cleaned.json"

def get_stopwords():
	print "Retrieving list of stopwords..."
	nltk_defaults = stopwords.words('english')
	punctuation = [',', ':', '.', ';', '-', '"', '--', '!', '?', '(', ')', '``', '\'\'']
	custom_words = ['would', 'say', 'said', 'though', 'it', 'still', 'he', 'at', 'even', 'but', 'like', 'upon', 'a']
	return set(nltk_defaults + punctuation + custom_words)

def penn2morphy(penntag, returnNone=False):
        #default nltk pos_tags are not compatible with wordnet functions
        morphy_tag = {'NN':wn.NOUN, 'JJ':wn.ADJ,
                                  'VB':wn.VERB, 'RB':wn.ADV}
        try:
                return morphy_tag[penntag[:2]]
        except:
                return None if returnNone else ''

def get_input(fname):
	stop_words = get_stopwords()
	print "Reading Input JSON..."
	with open(fname) as f:
		content = f.readlines()
	content = [(json.loads(x.lower()), stop_words) for x in content]
	print "Done loading json!"
	return content

def test():
	documents = get_input(input_file_path)
	print documents

def evaluate(row):
	record, stop_words = row
	text = nltk.word_tokenize(record['text'])
	
        sentList = nltk.sent_tokenize(record['text'])
        wordsInSentsPos = [nltk.pos_tag(nltk.word_tokenize(s)) for s in sentList]
        wordsInSentsWnPos = [[(w[0],penn2morphy(w[1])) for w in s if w[0].lower() not in stop_words] for s in wordsInSentsPos]
        #the above returns a list of sentences where each sentence is a list of
        #(word-as-string, pos tag) tuples. Stop words are removed here because pos_tag
        #uses grammatical structure but lesk does not.

        #lemmatization
        lmtzr = WordNetLemmatizer()
        for sent in wordsInSentsWnPos:
                for indx, tup in enumerate(sent):
                        if tup[1] != '': #if pos exists, reset word to lemma
                                word = lmtzr.lemmatize(tup[0], tup[1])
                                text[indx] = word
                        #if pos tagger failed, keep original word

	fdist = FreqDist(text)
	unfiltered_frequencies = fdist.most_common(fdist.B())
	frequencies = [t for t in unfiltered_frequencies if t[0] not in stop_words and t[1] > 5 and len(t[0]) > 2]
	return frequencies

def compile_results(individual_results):
	print "Merging Results..."
	res = Counter()
	for row in individual_results:
		res = res + Counter(dict(row))
	print "Done merging results..."
	return res

def main():
	documents = get_input(input_file_path)
	p = Pool(10)
	individual_results = p.map(evaluate, documents)
	final_results = compile_results(individual_results)
	
	print "Final Results: "
	for value, count in final_results.most_common():
		print value, count		

if __name__ == '__main__':
	main()
