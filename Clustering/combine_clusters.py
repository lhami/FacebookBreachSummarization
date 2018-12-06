"""
Combine results of multiple clustering runs to create a new json-formatted file containing the dataset, clusters.json
"""

import json

outfile = 'clusters.json'
descriptions = ['original_40topics_k-means_16clusters_descriptions.txt', 'reweighted_40topics_k-means_24clusters_descriptions.txt']
cluster_jsons = ['original_weight_40-topics_kmeans_16-clusters.json', 'reweighted_40-topics_kmeans_24-clusters.json']

assert len(descriptions) == len(cluster_jsons)

def get_input(fname):
    print "Reading Input JSON..."
    with open(fname) as f:
        content = f.readlines()
    content = [json.loads(x) for x in content]
    print "Done loading json!"
    return content

if __name__ == '__main__':
    f = open(outfile, 'w')
    clust_num = 0
    for i in range(len(cluster_jsons)):
        print 'Opening output file ', cluster_jsons[i], '...'
        content = get_input(cluster_jsons[i])                    # get the ith cluster output file as a list of json objects
        descr = open(descriptions[i], 'r').readlines()           # get the ith headline descriptions as a list of strings
        assert len(content) == len(descr)
        print 'Processing clusters: '
        for j in range(len(content)):
            content[j]['description'] = descr[j]
            content[j]['clusterid'] = clust_num
            print clust_num, descr[j]
            clust_num = clust_num + 1
            f.write(json.dumps(content[j]) + '\n')
        print


