'''
Creates an extractive summary of from a collection of articles.
Summary is approx 500 words in length.
 
'''

import nltk
from nltk.corpus import stopwords
import json
from multiprocessing import Pool
from gensim.summarization import summarize
import difflib

import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

#top-k documents json
input_file_path = "../select_top_k_documents/new_cleaned.json"

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
	text = record['text']
	
	#filters out any documents under 500 words long
	if len(text) > 500:
		return summarize(text, 0.03)

	return ""

def compile_results(individual_results):
	print "Merging Results..."
	summary = ""
	for indx1, row in enumerate(individual_results):
		for indx2, row2 in enumerate(individual_results):
			if individual_results[indx1] == None:
				break
			if individual_results[indx2] == None or indx1 == indx2:
				continue

			diff = True
			s = difflib.SequenceMatcher(None, row2, row)
			#if row is 50% similar to any other sentence in the results, 
			#don't add it to the summary and remove it from data
			if s.ratio() > 0.50:
				diff = False
				individual_results[indx2] = None	
		if diff:
			summary = summary + " " + row
		diff = False
	print "Done merging results..."
	return summary

def main():
	documents = get_input(input_file_path)
	p = Pool(15)
	
	#create inital summaries
	individual_results = p.map(evaluate, documents)
	
	#concatenate individual article summaries
	first_pass_results = compile_results(individual_results)
	
	#create overall summary of article summaries
	new_summary = summarize(first_pass_results, word_count=500, split=True)
	
	#remove the duplicate sentences to produce final summary
	final_results = compile_results(new_summary)

	print "Final Summary\n", final_results


if __name__ == '__main__':
	main()
