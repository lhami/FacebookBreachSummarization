# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 14:14:49 2018

@author: Leah
"""
import json
from collections import Counter
import re
import csv

k = 100

def write_output_file(data):
        new_file = open("new_cleaned.json", "w")
        for line in data:
                new_file.write(json.dumps(line) + "\n")
        new_file.close()

def extracturls(url):
    urlcore = re.match("(?:http(?:s)?:\\/\\/)?(?:www\\.)?([\\w.-]+(?:\\.[\\w\\.-]+)+)(?:[/#:]|$)",url)
    if urlcore:
        return urlcore.groups()[0]
    else:
        return ""

import_path = "../../Output_Files/big/cleaned.json"
save_path = "../../Leah/websiteDistribution.csv"

with open(import_path) as f:
    content = f.readlines()
    content = [(json.loads(x)) for x in content]

urlsList = [extracturls(x['originalurl']) for x in content]
urlsDist = Counter(urlsList).most_common(k)

print urlsDist

urlSet = set([key for (key, val) in urlsDist])

output = []
for x in content:
	if extracturls(x['originalurl']) in urlSet:
		output.append(x)

print len(output)
write_output_file(output)		
