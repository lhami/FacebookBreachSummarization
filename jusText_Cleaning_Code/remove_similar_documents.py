import json
import copy
import re

fname = "cleaned.json"
threshold = 0.4 # if more than threshold*100% is common between two documents, delete the smaller one

'''
This file is used to remove documents that are 'similar' by a factor grater than the threshold.
Similarity is defined by the number of sentences common to both documents.

for example - if the threshold is 0.6, and documents d1 and d2 have over 60% of common sentences, the smaller document will be deleted from the database.
'''

def read_input_file():
        with open(fname) as f:
                content = f.readlines()
        original_content = [json.loads(x) for x in content]
        lowercase_content = [json.loads(x.lower()) for x in content]

        return (original_content, lowercase_content)

def createset(paragraph):
	res = re.split("\.\s+", paragraph)
	if res[-1] == "":
		res = res[:-1]
	elif res[-1][-1] == ".":
		last = res[-1]
		res.pop()
		res.append(last[:-1])
	return set(res)

def filter_documents(biglist):
	print "Running algorithm to filter similar entries... on ", len(biglist), "entries"
	sims = []

        for i in range(0, len(biglist)):
                for j in range(i+1, len(biglist)):
                        if biglist[i] == None:
                                break
                        if biglist[j] == None:
                                continue

                        intersect = biglist[i][1].intersection(biglist[j][1])
			if len(biglist[j][1]) == 0:
				print biglist[j]
				exit()
                        score = len(intersect)*1.0/len(biglist[j][1])*1.0
                        if score > threshold:
                                print "Deleted document ", j, " since it is similar to document ", i, " -- Similarity: ", score
                                sims.append(score)


                                #print biglist[i][0]['originalurl']
                                #print biglist[j][0]['originalurl']
                                #print '\n\n'


                                biglist[j] = None

        sims.sort()
        #print sims
	shortlist = [x[0] for x in biglist if x is not None]
        print "Original Length: ", len(biglist)
        print "New Length: ", len(shortlist)

	return shortlist

def main():
	
	print "Reading Input File..."
	og_content, jsondocs = read_input_file()

	#Removing duplicate DOCUMENTS
	biglist = []
	for i in range(0, len(jsondocs)):
		biglist.append([og_content[i], createset(" ".join(jsondocs[i]['text']))])

	print "Sorting all docs..."
	biglist.sort(key=lambda x: len(x[1]), reverse=True)

	no_duplicate_docs_list = filter_documents(biglist)
	

	#Removing duplicate PARAGRAPHS
	'''
	paragraphs_list = []
	for doc in no_duplicate_docs_list:
		for para in doc["text"]:
			line = doc
			line["text"] = para

			paragraphs_list.append(copy.copy(line))

	biglist = []
	for i in range(0, len(paragraphs_list)):
                biglist.append([paragraphs_list[i], createset(paragraphs_list[i]['text'].lower())])

	print "Sorting all paras..."
        biglist.sort(key=lambda x: len(x[1]), reverse=True)

	filtered_paras = filter_documents(biglist)
	'''

	new_file = open("new3.json", "w")
	for line in no_duplicate_docs_list:
		new_file.write(json.dumps(line) + "\n")
	new_file.close()

main()
