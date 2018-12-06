# -*- coding: utf-8 -*-
"""
Created on Sun Nov 18 18:17:02 2018

@author: Leah
"""

import getopt
import sys
import json
import os
import pandas as pd

def getSummary(directory,filenum):
    with open(os.path.join(directory,"%06d_decoded.txt" % filenum), 'r') as f:
        return ' '.join([line.rstrip() for line in f])
    
def alignSummaries(jsonFile,outFile,urlFile,sumDir):
    sumFiles = os.listdir(sumDir)
    summaries = pd.DataFrame(columns=["url","summary","cluster"])
    clusters = []
    
    #First, makes a dataframe with the cluster num and url of each summary
    #By cross-referencing a line from the metadata url file
    #With a summary .txt file.
    #Assumes the line order and sequential file numbering match up.
    print("Reading summaries...")
    with open(urlFile,'r') as urls:
        for x in range(len(sumFiles)):
            url, cluster = urls.readline().rsplit(' ',1)
            summary = getSummary(sumDir, x)
            summaries = summaries.append({"url":url,"cluster":int(cluster),"summary":summary},ignore_index = True)
    print("Done reading summaries.")
    
    print("Iterating through clusters...")
    #In each cluster, loops through the url list and makes a list of summaries in the same order
    #Then appends the list to the dict that is clusters
    for line in open(jsonFile,'r'):
        cluster = json.loads(line)
        clusterid = int(cluster["clusterid"])
        clustSums = summaries[summaries.cluster == clusterid].copy()
        entries = len(cluster["originalurl"])
        orderedSums = []
        for x in range(entries):
            orderedSums.append(clustSums[clustSums.url == cluster["originalurl"][x]].iloc[0]["summary"])
        clusters.append({**cluster,**{"abstract":orderedSums}})
        print("Cluster %d aligned." % clusterid)
    print("Done aligning clusters.")
    
    print("Preparing to write output...")
    #writing to file
    with open(outFile, 'w') as write:
        for clust in clusters:
            #write each cluster on a line as json object
            write.write(json.dumps(clust) + "\n")
    print("New json written to %s" % outFile)

if __name__ == '__main__':
        
	print((sys.argv))
	
	try:
	   opts, args = getopt.getopt(sys.argv[1:],"h:j:m:o:s:")
	except getopt.GetoptError:
		
		print(("opts:"))
		print((opts))
		
		print(('\n'))
		print(("args:"))
		print((args))
		
		print(("Incorrect usage of command line: "))
		print(('python abstracts_to_json.py -j <existing JSON file> -m <TXT file with URLs and cluster NOs> -o <output JSON file location> -s <directory of summaries>'))
	   
	  
	   
		sys.exit(2)
	   
	#initialize cmd line variables with default values
	jsonFile = None #clusters.json
	outFile = None #New .json file to be written
	sumDir = None #Directory containing individual summary files
	urlFile = None #.txt file containing urls and cluster #s

	
	for opt, arg in opts:
		print((opt,'\t',arg))
		if opt == '-h':
			print(('python abstracts_to_json.py -j <existing JSON file> -m <TXT file with URLs and cluster NOs> -o <output JSON file location> -s <directory of summaries>'))
			sys.exit()
		elif opt in ("-j"):
		   jsonFile = arg
		elif opt in ("-m"):
			urlFile = arg
		elif opt in ("-o"):
			outFile = arg
		elif opt in ("-s"):
			sumDir = arg
        

           
	print('\n')
	print("JSON file:",jsonFile)
	print("Output file:", outFile)
	print("URL file:", urlFile)
	print("Summary subdirectory:", sumDir)
	print('\n')
    
	alignSummaries(jsonFile,outFile,urlFile,sumDir)