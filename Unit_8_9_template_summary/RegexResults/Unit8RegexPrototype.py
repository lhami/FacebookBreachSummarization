# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 10:07:38 2018

@author: Leah
"""
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re
from collections import Counter
import csv
import json
from num2words import num2words
from word2number import w2n
from dateutil.parser import parse
import os
from datetime import date

def dictReplace(text,replacements):
    # sort keys by length, in reverse order
    for item in sorted(replacements.keys(), key = len, reverse = True):
        text = re.sub(item, replacements[item], text, flags=re.IGNORECASE)
    return text

def meatExtractor(text):
    match = re.match("^(\\W*)(.*?)(\\W*)$",text)
    if not match: return ['',text,'']
    return [match.group(1),match.group(2),match.group(3)]

def strNum2Words(match):
    string = match.group()
    return num2words(int(string))

def words2Nums(match):
    origtext = match.group()
    if re.search('\\d+',origtext):
        origtext = re.sub('\\d+',strNum2Words,origtext)
    textSandwich = meatExtractor(origtext)
    #badjuju = ["and","and and"]
    #if textSandwich[1] in badjuju: return origtext
    try:
        if re.match("hundred|thousand|million|billion",textSandwich[1]):
            textSandwich[1] = "one " + textSandwich[1]
        return textSandwich[0] + str(w2n.word_to_num(textSandwich[1])) + textSandwich[2] #Some non-text is getting here?
    except:
        return origtext

def stdNums(text):
    if not isinstance(text,str) or text == "": return "" #str to basestring for python 2
    numwordre = re.compile('(\\d*[ -])+((' + '|'.join(w2n.american_number_system.keys()) + '|and)[ ,-.])+', re.IGNORECASE)
    
    #numbers = w2n.american_number_system
    ordinals = {'first' : 'one',
                'second' : 'two',
                'third' : 'three',
                'fourth' : 'four',
                'fifth' : 'five',
                'sixth' : 'six',
                'seventh' : 'seven',
                'eighth' : 'eight',
                'ninth' : 'nine',
                'tenth' : 'ten',
                'eleventh' : 'eleven',
                'twelfth' : 'twelve',
                'teenth' : 'teen',
                'tieth' : 'ty',
                'hundredth' : 'hundred',
                'thousandth' : 'thousand',
                'millionth' : 'million',
                'billionth' : 'billion'}
    text = dictReplace(text,ordinals)
    return numwordre.sub(words2Nums,text) #sometimes non-strings are being returned?

def arrayToCounter(arr):
    return Counter(x for xs in arr for x in xs if len(xs) > 0)
    
def getDates(text):
    text = stdNums(text)
    months = ['january','february','march','april','may','june','july','august','september','october','november','december']
    months.extend([m[:3] for m in months]+['sept'])
    datematcher = '((\\d{1,2}(st|nd|rd|th)?([ ,-.]{1,2}|( of ))?)?(' + '|'.join(months) + ')([ ,-.]{1,2}\\d{1,4}(st|nd|rd|th)?)?([ ,-.]{1,2}\'?\\d{2,4}(?!:))?|\\d{1,2}[-\\/]\\d{1,2}([-\\/](\\d{4}|\\d{2}))?)'
    dates = []
    for match in re.finditer(datematcher,text):
        try:
            candidate = match.group()
            if not re.search("\\d",candidate): continue
            d = parse(candidate)
            if d is not None: dates.append(d.date())
        except: continue
    return dates

def getUsers(text):
    text = stdNums(text)
    #if not isinstance(text,basestring) or text == "": return []
    numbers = '\\d+(?=[ ,-.]{1,2}([^ .,:;]+? )?(?:user|profile|customer)s?(?:(?: of )([^ .,:;]+?)[ .,:;])?)'
    nums = []
    services = []
    for match in re.finditer(numbers,text,re.IGNORECASE):
        nums.append(match.group(0))
        if match.group(1) is not None:
            services.append(match.group(1))
        elif match.group(2) is not None:
            services.append(match.group(2))
    return nums, services

def writeCSV(counter,outdir,filename):
    with open(os.path.join(outdir,filename), mode='w', newline='') as fp:
        writer = csv.writer(fp, delimiter=",")
        writer.writerow(['Token','Freq'])
        for tup in counter.most_common():
            writer.writerow(tup)

jsonFile = "../../Clustering/clusters.json"
outDir = "./"
senclust = [11,30]
genclust = [0,2]
docs = []
for line in open(jsonFile,'r'):
    #lines.append(json.loads(line)) #This line works for doc-per-line cleaned.json
    #Method for unzipping dictionary-of-lists-per-row cluster.json:
    cluster = json.loads(line)
    if int(cluster['clusterid']) not in senclust + genclust: continue
    singlekeys = [key for key in cluster.keys() if not isinstance(cluster[key], list)]
    listkeys = [key for key in cluster.keys() if isinstance(cluster[key], list)]
    entries = len(cluster[listkeys[0]])
    for x in range(entries):
        docs.append({**{key:cluster[key] for key in singlekeys},**{key:cluster[key][x] for key in listkeys}})

results = {"senDates" : Counter(),
           "breachDates" : Counter(),
           "numUsers" : Counter(),
           "websites" : Counter()}

for doc in docs:
    rawtext = doc['text']
    numtext = stdNums(rawtext)
    if int(doc['clusterid']) in senclust:
        results['senDates'] += Counter(getDates(numtext))
    if int(doc['clusterid']) in genclust:
        results['breachDates'] += Counter(getDates(numtext))
        users, websites = getUsers(numtext)
        results['numUsers'] += Counter(users)
        results['websites'] += Counter(websites)

for key, val in results.items():
    writeCSV(val, outDir, key + ".csv")
