import nltk
#from nltk.book import *
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import json
import time
import csv
from multiprocessing import Pool
from collections import Counter
import os

import codecs
import sys
reload(sys)
sys.setdefaultencoding('utf8')

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


input_file_path = "../jusText_Cleaning_Code/cleaned.json"

def get_stopwords():
	print "Retrieving list of stopwords..."
	nltk_defaults = stopwords.words('english')
	punctuation = [',', ':', '.', ';', '-', '"', '--', '!', '?', '(', ')', '``', '\'\'']
	custom_words = ['would', 'say', 'said', 'though', 'it', 'still', 'he', 'at', 'even', 'but', 'like', 'upon', 'a']
	return set(nltk_defaults + punctuation + custom_words)

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

def writeCSV(counter,outdir,filename):
	with open(os.path.join(outdir,filename), mode='w') as fp:
		writer = csv.writer(fp, delimiter=",")
		writer.writerow(['Token','Freq'])
		for tup in counter.most_common():
			writer.writerow(tup)

def main():
	st = time.time()
	print "Start Time: ", st
	documents = get_input(input_file_path)
	print "Length: ", len(documents)
	#documents = documents * 70
	#print "New len", len(documents)
	
	#individual_results = [ evaluate(record) for record in documents ]

	p = Pool(10)
	individual_results = p.map(evaluate, documents)
		
	end = time.time()
	print "End Time: ", end-st

	final_results = compile_results(individual_results)
	#print "Final Results", final_results
	
	writeCSV(final_results,".","fb_big_frequentwords.csv")

	print "Final Results: "
	for value, count in final_results.most_common():
		print value, count

if __name__ == '__main__':
	main()
