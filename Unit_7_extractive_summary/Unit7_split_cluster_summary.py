'''
Creates an extractive summary of from a collection of articles.
Uses clustered articles to create a better summary.
Makes a 2 paragraph summary, each paragraph focusing on a different topic.

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

#json with articles in clusters
input_file_path = "../Clustering/clusters.json"

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
	record, stopwords = row
	cluster = record['text']
	topic = record['description']	
	c_id = record['clusterid']
	summary = None
	urls = record['originalurl']

	#remove bad documents by URL - ESL lesson plan
	for indx, url in enumerate(urls):	
		if "www.centerforcopyrightintegrity.com" in url or "breakingnewsenglish.com" in url or "https://www.tjack.nl/" in url:
			cluster[indx] = None

	#get only "good" clusters - only selected clusters get summarized
	if c_id == 5 or c_id == 8 or c_id == 11 or c_id == 14 or c_id == 27 or c_id == 28 or c_id == 30 or c_id == 33 or c_id == 35:
		print "Summarizing:", c_id, topic
		for doc in cluster:
			if doc == None: 
				continue
			if len(doc) > 500:
				lil_summary = summarize(doc, word_count=150, split=True)
				if summary == None:
					summary = lil_summary
				else:
					summary.extend(lil_summary)
								
		print "Finished", c_id, ":", topic

	return summary

def compile_results(individual_results, percent):
	print "Merging Results..."

	summaries = []
	diff = True
	for indx, cluster in enumerate(individual_results):
		if cluster == None:
			continue
		summary = None
		for i1, sent1 in enumerate(cluster):
			if sent1 == None:
				continue
			for i2, sent2 in enumerate(cluster):
				if sent2 == None or i1 == i2:
					continue

				diff = True
				s = difflib.SequenceMatcher(None, sent1, sent2)
				#if row is 50% similar to any other sentence in the results, 
				#don't add it and remove it from data
				if s.ratio() > percent:
					diff = False
					individual_results[indx][i2] = None
					break	
			if diff:
				if summary == None:
					summary = [sent1]
				else:
					summary.append(sent1)
		print "Done merging cluster", indx
		summaries.append(summary)	

	print "Done merging results..."
	#list where each element is a summary of an individual cluster
	return summaries

def remove_duplicates(summary, percent):
	print "Removing duplicate sentences..."
	final = ""
	for indx1, sent1 in enumerate(summary):
		diff = True
		for indx2, sent2 in enumerate(summary):
			if indx1 == indx2:
				continue
			s = difflib.SequenceMatcher(None, sent1, sent2)
			if s.ratio() > percent:
				diff = False
				break
		if diff:
			final = final + " " + sent1
	
	return final

def main():
	documents = get_input(input_file_path)
	p = Pool(15)
	#summarize individual cluster articles
	individual_results = p.map(evaluate, documents)

	#combine clutser results and remove duplicate sentences
	results = compile_results(individual_results, 0.4)
	
	general_sum = ""
	misc_sum = ""
	#concatenate all the cluster summaries based on which paragraph they are in
	for indx, summary in enumerate(results):
		#first pargraph clusters
		if indx == 0 or indx == 1 or indx == 4 or indx == 5 or indx == 7:
			general_sum = general_sum + remove_duplicates(summary, 0.4)
		#second paragraph clusters
		else:
			misc_sum = misc_sum + remove_duplicates(summary, 0.4)

	print "Summarizing final summary"
	summary_1 = summarize(general_sum, word_count=200, split=True)
	summary_2 = summarize(misc_sum, word_count=200, split=True)
	
	print "Final summary:"
	print remove_duplicates(summary_1, 0.5)
	print remove_duplicates(summary_2, 0.5)


if __name__ == '__main__':
	main()
