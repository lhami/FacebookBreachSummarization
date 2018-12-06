import nltk
#from nltk.book import *
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import json
import time
from multiprocessing import Pool
from collections import Counter
from gensim.summarization import summarize
import difflib

import codecs
import sys

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)


#input_file_path = "new_cleaned.json" #top k documents json
#input_file_path = "clusters.json"
input_file_path = "abstracts.json"
#input_file_path = "../Output_Files/small/cleaned.json"

def get_input(fname):
	print "Reading Input JSON...\n"
	lines = []
	with open(fname, 'r') as f:
		for line in f:
			lines.append(json.loads(line))
	print "Done loading json!\n"
	return lines

def summarize_cluster(record):
	cluster = record['abstract']
	topic = record['description']
	c_id = record['clusterid']
	text = None
	urls = record['originalurl']
	percent = 0.5

	print c_id, topic
	diff = True
	for indx1, doc1 in enumerate(cluster):
		if doc1 is None or doc1 == "": 
			continue
		url = urls[indx1]
		if "breakingnewsenglish.com" in url or "https://www.tjack.nl/" in url:
			continue
		for indx2, doc2 in enumerate(cluster):
			if indx1 == indx2 or doc2 is None or doc2 == "":
				continue
			diff = True
			s = difflib.SequenceMatcher(None, doc1, doc2)
			#if row is 50% similar to any other sentence in the results, 
			#don't add it and remove it from the list
			if s.ratio() > percent:
				cluster[indx1] == None
				diff = False
				break
		if diff:
			if text == None:
				text = doc1
			else:
				text = text + " " + doc1
	
	summary = summarize(text, 0.01, split = False) #May need to change split to True and run the sentence-checker afterwards before returning results.
	print "cluster:", c_id, ",", topic, "summarized\n"
	return c_id, summary

def main():
	st = time.time()
	print "Start Time: ", st, "\n"
	documents = get_input(input_file_path)
	print "Length: ", len(documents), "\n"
	#documents = documents * 70
	#print "New len", len(documents)
	
	#individual_results = [ evaluate(record) for record in documents ]
	
	goodClustA = [5,8,27,28,33]
	goodClustB = [11,14,30,35]
	goodDocs = [cluster for cluster in documents if cluster['clusterid'] in goodClustA + goodClustB]
		
	end = time.time()
	print "End Time: ", end-st, "\n"
	
	p = Pool(15)
	cluster_summaries = p.map(summarize_cluster,goodDocs)
	
	print "All clusters summarized.\n"
	
	for c_id, summary in cluster_summaries:
		if c_id in goodClustA: print summary, "\n"
	print "\n"
	for c_id, summary in cluster_summaries:
		if c_id in goodClustB: print summary, "\n"

	#print type(first_pass_results)
	#print first_pass_results, "\n\n"
	#print "10% sumarry \n", summarize(first_pass_results, ratio=0.03)
	#new_summary = summarize(first_pass_results, ratio=0.05, split=True)
	#print len(new_summary)
	#print new_summary
	#final_results = compile_results(new_summary, .5)
	#print "final\n", final_results

#	for sent in new_summary:
#		#print sent
#		if sent not in final_results:
#			final_results = final_results + " " + sent

	#print "Final Summary\n", new_summary #final_results

	#print "Final Results: "
	#for value, count in final_results.most_common():
	#	print value, count

if __name__ == '__main__':
	main()
