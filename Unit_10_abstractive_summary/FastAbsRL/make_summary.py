"""
Make an abstractive summary from the results of FastRL.
Uses clustered documents.
"""
import json
import random

# Unzip fast_abs_rl.zip and generate txt file first
absfile = "big/abslines.txt"
clusterfile = "big/clusters.json"

def get_input(fname):
    print "Reading Input JSON..."
    with open(fname) as f:
        content = f.readlines()
    content = [json.loads(x) for x in content]
    print "Done loading json!"
    return content


def get_summaries(fname):
    print "Reading abstractive summaries..."
    with open(fname) as f:
        content = f.readlines()
    return content


from gensim.summarization.summarizer import summarize
import numpy as np

# TODO do some word2vec or doc2vec stuff to get the most unique sentences
# https://github.com/RaRe-Technologies/gensim/blob/develop/docs/notebooks/doc2vec-lee.ipynb
def choose_sentences(lines, num_sentences):
    """
    # Random choice
    chosen = random.sample(lines, num_sentences)
    chosen = [c[:-1] + " " for c in chosen]   # get rid of newlines
    return "\n".join(chosen)
    """
    # Extractive summary
    seen = []
    for line in lines:
        if line not in seen:
            seen.append(line)
    lines = seen
    ratio = float(num_sentences)/len(lines)
    lines = "".join(lines)
    summ = summarize(lines, ratio=ratio)
    return "".join(summ)



if __name__ == '__main__':
    clusters = get_input(clusterfile)
    abs = get_summaries(absfile)
    ci = [] # List of index ranges for each cluster
    i0 = 0
    for c in clusters:
        l = len(c['text'])
        ci.append((i0, i0+l))
        i0 = i0 + l
        print c['clusterid'], c['description']
    summ = ""
    while True:
        print
        clust = input("Cluster number: ")
        num_sentences = raw_input("Number of sentences: ")
        i0, i1 = ci[clust]
        lines = abs[i0:i1]
        if num_sentences == 'p':
            for line in lines: print line
        else:
            summ = summ + '(%d)\n' % clust + choose_sentences(lines, int(num_sentences)) + '\n'
            print summ
