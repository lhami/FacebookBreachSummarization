
import json
import re

# Code to convert the cleaned.json dataset into a set of sentences

fname = "../../jusText_Cleaning_Code/cleaned.json"

def get_input():
        print "Reading Input JSON..."
        with open(fname) as f:
                content = f.readlines()
        content = [json.loads(x) for x in content]
        print "Done loading json!"
        return content

def get_sents(paragraph):
        res = re.split("\.\s+", paragraph)
        if res[-1] == "":
                res = res[:-1]
        elif res[-1][-1] == ".":
                last = res[-1]
                res.pop()
                res.append(last[:-1])
        return res

def write_output_file(data):
	print "Writing to output file..."
	new_file = open("fb_sentences.txt", "w")
        for line in data:
                new_file.write(line + "\n")
        new_file.close()

def solve():
	data = get_input()
	results = []
	print "Converting to sentences now..."
	for doc in data:
		sents = get_sents(doc['text'])
		results = results + sents
	write_output_file(results)	

solve()
