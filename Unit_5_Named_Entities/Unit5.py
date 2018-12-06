#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extracts the most important named entities
"""
import nltk
from nltk.probability import FreqDist
import spacy
import json
from spacy import displacy
from multiprocessing import Pool
from collections import Counter
import en_core_web_sm
import codecs
import sys

UTF8Writer = codecs.getwriter("utf8")
sys.stdout = UTF8Writer(sys.stdout)

input_file_path = "../jusText_Cleaning_Code/cleaned.json"

def get_input(filename):
    print ("Reading Input JSON...")
    with open(filename, "r") as f:
        lines = f.readlines()
        content = [json.loads(line) for line in lines]
    content = [record for record in content] 
    print ("Done loading JSON!")
    return content

def evaluate(row):
    record = row
    text = nltk.word_tokenize(record)
    
    #SpaCy to extract named entities
    docs = get_input(input_file_path)
    nlp = spacy.load('en_core_web_sm')
    sentence = nlp(docs)
    results_entities = [(X.text, X.label_) for X in sentence.ents]
    
    #Finds the most frequent words
    fdist = FreqDist(text)
    unfiltered_frequencies = fdist.most_common(fdist.B())
    frequencies = [t for t in unfiltered_frequencies if t[1] > 5 and len(t[0]) > 2]
    return frequencies

def compile_results(individual_results):
    print ("Merging Results...")
    res = Counter()
    for row in individual_results:
        res = res + Counter(dict(row))
        print ("Done merging results!")
        return res
    
def main():
    docs = get_input(input_file_path)
    p = Pool(10)
    print(p)
    individual_results = p.map(evaluate, docs)
    final_results = compile_results(individual_results)
    
    print("Final Results: ")
    for value, count in final_results.most_common():
        print (value, count)
    
       
if __name__ == "__main__":
    main()

