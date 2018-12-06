# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:22:08 2018

@author: Leah
"""
import json
import re
import spacy
from collections import Counter
from num2words import num2words
from word2number import w2n
nlp = spacy.load("en")
from spacy.symbols import VERB, dobj, obj, nsubjpass

def getContext(word,text,buffersize = 20):
    pattern = ".{%d}%s.{%d}" % (buffersize,word,buffersize)
    return re.findall(pattern,text,re.IGNORECASE)

def iterLen(iterable):
    return sum(1 for _ in iterable)

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

jsonFile = "../Clustering/clusters.json"
outDir = "./"
senclust = [11,30]
genclust = [0,2]
docs = []
for line in open(jsonFile,'r'):
    #lines.append(json.loads(line)) #This line works for doc-per-line cleaned.json
    #Method for unzipping dictionary-of-lists-per-row cluster.json:
    cluster = json.loads(line)
    #if int(cluster['clusterid']) not in senclust + genclust: continue
    singlekeys = [key for key in cluster.keys() if not isinstance(cluster[key], list)]
    listkeys = [key for key in cluster.keys() if isinstance(cluster[key], list)]
    entries = len(cluster[listkeys[0]])
    for x in range(entries):
        docs.append({**{key:cluster[key] for key in singlekeys},**{key:cluster[key][x] for key in listkeys}})

contexts = []
for doc in docs:
    contexts.extend(getContext("reported",doc['text'],40))
contexts[:100]


docs = [{**doc,"nlpobj":nlp(doc['text'])} for doc in docs]
results = {"numUsers" : Counter(),
           "websites" : Counter()}
breachsents = [token.sent for doc in docs for token in doc['nlpobj'] if token.dep in [dobj,obj,nsubjpass] and token.head.lemma_ in ["collect","harvest","steal","obtain","leak"]]
#########################################################################
#For the dates of the breach
breachDates = []
for sent in breachsents:
    if "election" in sent.text or "campaign" in sent.text: continue
    #Filtering election stuff because "the 2016 Trump campaign" was in everything
    for ent in sent.ents:
        if ent.label_ == "DATE":
            breachDates.append(ent.text)
results['breachDates'] = Counter(breachDates)

#########################################################################
#For the number of users whose data was breached
for doc in docs:
    rawtext = doc['text']
    numtext = stdNums(rawtext)
    if int(doc['clusterid']) in genclust:
        users, websites = getUsers(numtext)
        results['numUsers'] += Counter(users)
        results['websites'] += Counter(websites)

#########################################################################
#For the kind of information leaked
harvestphrases = []
for sent in breachsents:
    for token in sent:
        if token.dep in [dobj,obj,nsubjpass] and token.head.lemma_ in ["collect","harvest","steal","obtain"]:
            harvestphrases.append(' '.join(x.text for x in token.subtree if 5 < iterLen(token.subtree) < 20))
            #Filtering by length to avoid all the instances of "data" and some long poorly-parsed sentences
            
harvestcandidates = [phrase for phrase in harvestphrases if phrase != "" and "and" in phrase and "friend" in phrase]
#Most common identical phrase--unspecific
#print(Counter(harvestcandidates).most_common(1))
#Longest phrase after filtering--very good
print(max(harvestcandidates,key=len))

#########################################################################
#For the party that obtained the leaked info
#Had planned to 

#########################################################################
#For the whistleblower
whistleblowers = []
for doc in docs:
    docnlp = doc['nlpobj']
    for name in docnlp.ents:
        if name.label_ == "PERSON":
            #keep if whistleblower is to the left/right
            whistleblower = False
            sentstart = docnlp[name.start].sent.start
            sentend = docnlp[name.start].sent.start
            if "wylie" in name.text: print(name.text, sentstart, sentend)
            #checks the words to the left in the sentence
            for x in range(1,name.start - sentstart):
                token = docnlp[name.start - x]
                if token.is_punct or token.is_stop or token.is_space:
                    continue
                elif token.text in ["whistleblower","whistle-blower"]:
                    whistleblower = True
                break
            #checks the words to the right in the sentence
            if not whistleblower:
                for x in range(sentend - name.end):
                    token = docnlp[name.end + x]
                    if token.is_punct or token.is_stop or token.is_space:
                        continue
                    elif token.text in ["whistleblower","whistle-blower"]:
                        whistleblower = True
                    break
            if whistleblower: whistleblowers.append(name.text)
#Note--code does not currently work because spaCy is not picking up names in our
#corpus as names. Suspected due to lack of capitalization.
#results['whistleblower'] = Counter(whistleblowers)

width = max([len(x) for x in results.keys()]) + 2
for key, val in results.items():
    res = val.most_common(1)[0]
    print("{slot: <{wid}}: {result: <20} {count}".format(slot = key, wid = width, result = res[0], count = res[1]))
