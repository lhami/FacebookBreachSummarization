import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from collections import Counter
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import DBSCAN
import pickle
import math

from sklearn.metrics.pairwise import pairwise_distances

input_fname = "lsa.csv"
output_fname = "lsa_clusters.pickle"

def create_matrix():
	#matrixx = np.array([[0.5,0.2,0.7], [1,0,0.3], [0.5,0.7,0.2]]) # todo call read_from_csv
	print "Reading input data from CSV File..."
	# documents vs topics after transpose
	matrixx = np.genfromtxt(input_fname, delimiter=',').T
	print matrixx
	print "Size: ", matrixx.shape
	#for i in range(0, matrixx.shape[0]):
		#for j in range(0, matrixx.shape[1]):
			#matrixx[i][j] = matrixx[i][j] / ((j+1)*(j+1)*1.0/200*1.0)
	print matrixx
	return matrixx

original_mat = create_matrix()
mat = np.copy(original_mat)
original_normalized_mat = normalize(original_mat, axis=1)
normalized_mat = np.copy(original_normalized_mat)

def generate_cluster_to_documents_mapping(labels):
	dist = {}
	for index, cluster_number in enumerate(labels):
		if cluster_number not in dist:
			dist[cluster_number] = []
		dist[cluster_number].append(index)

	return dist

def lsa_kmeans(n_clusters):
	print "Running K-Means with n_clusters=%d" % n_clusters
	cluster_model = KMeans(n_clusters=n_clusters).fit(normalized_mat)
	labels = cluster_model.predict(mat)
	centroids = cluster_model.cluster_centers_

	#print labels
	#print Counter(labels)

	return generate_cluster_to_documents_mapping(labels)
	

def lsa_agglomerative(n_clusters, linkage, affinity):
	assert linkage == "complete" or linkage == "average" or linkage == "single", "Invalid Parameters"
	assert affinity == "euclidean" or affinity == "cosine", "Invalid Parameters"

	print "Running lsa_agglomerative with n_clusters=%d linkage=%s affinity=%s" % (n_clusters, linkage, affinity)
	cluster_model = AgglomerativeClustering(n_clusters=n_clusters, linkage=linkage, affinity=affinity).fit(mat if affinity == "cosine" else normalized_mat)
	labels = cluster_model.labels_

	#print Counter(labels)

	return generate_cluster_to_documents_mapping(labels)

def lsa_dbscan(metric, eps=0.5, min_samples=5):
	assert metric == "euclidean" or metric == "cosine", "Invalid Parameters"

	print "Running lsa_dbscan with metric=", metric
	cluster_model = DBSCAN(metric=metric, eps=eps, min_samples=min_samples).fit(mat if metric == "cosine" else normalized_mat)
	labels = cluster_model.labels_

	#print Counter(labels)

	'''
	dist = {"normalized": {}, "original": {}}
	for index, cluster_number in enumerate(labels):
		if cluster_number not in dist["normalized"]:
			dist["normalized"][cluster_number] = []
			dist["original"][cluster_number] = []
		dist["normalized"][cluster_number].append(normalized_mat[index])
		dist["original"][cluster_number].append(mat[index])
	'''

	return generate_cluster_to_documents_mapping(labels)

def run_agglomerative_for_k_clusters(k):
	mapping = {"single":{}, "average":{}, "complete":{}}
	for linkage in mapping.keys():
		mapping[linkage]["euclidean"] = lsa_agglomerative(k, linkage, "euclidean")
		mapping[linkage]["cosine"] = lsa_agglomerative(k, linkage, "cosine")

	return mapping

def write_output_file(results):
	print "Writing to output file"
	#new_file = open("lsa_clusters_data.pickle", "w")
	pickle.dump(results, open(output_fname, "wb"))
	#new_file.close()

def final():
	topic_sizes = [100, 80, 60, 40, 20]
	weightages = ['original_weight', 'reweighted']
	results = {}

	for weight in weightages:
		results[weight] = {}
	        for topics in topic_sizes:
        	        print "Topics: ", topics
                	mat = np.copy(original_mat[:,0:topics])
	                normalized_mat = np.copy(original_normalized_mat[:,0:topics])
	
        	        algorithms = {"kmeans":{}, "complete_linkage_cosine_dist":{}}
                	for k in range((int)((topics/2) - (3*0.1*(topics/2))), (int)((topics/2) + (3*0.1*(topics/2))), (int)(0.1*(topics/2))):
	                        algorithms["kmeans"][str(k)+"-clusters"] = lsa_kmeans(k)
        	                algorithms["complete_linkage_cosine_dist"][str(k)+"-clusters"] = lsa_agglomerative(k, 'complete', 'cosine')
        	       	results[weight][str(topics)+"-topics"] = algorithms

		print 'Reweighting the matrices'
		for i in range(0, original_mat.shape[0]):
	                for j in range(0, original_mat.shape[1]):
        	                original_mat[i][j] = original_mat[i][j] / ((j+1)*(j+1)*1.0/200*1.0)
				original_normalized_mat[i][j] = original_normalized_mat[i][j] / ((j+1)*(j+1)*1.0/200*1.0)

		print original_mat, "\nNormalized: \n", original_normalized_mat
        write_output_file(results)
	#print results

def main():
	
	topic_sizes = [200, 100, 60, 40, 20]
	results = {}

	for topics in topic_sizes:
		print "topics: ", topics
		for i in range((int)((topics/2) - (3*0.1*(topics/2))), (int)((topics/2) + (3*0.1*(topics/2))), (int)(0.1*(topics/2))):
			print i

	exit()
	for topics in topic_sizes:
		print "Topics: ", topics
		mat = np.copy(original_mat[:,0:topics])
		normalized_mat = np.copy(original_normalized_mat[:,0:topics])
		print mat.shape

		algorithms = {"kmeans":{}, "agglomerative":{}, "dbscan":{}}
		for k in range((int)((topics/2) - (3*0.1*(topics/2))), (int)((topics/2) + (3*0.1*(topics/2))), (int)(0.1*(topics/2))):
			algorithms["kmeans"][str(k)+"-clusters"] = lsa_kmeans(k)
			algorithms["agglomerative"][str(k)+"-clusters"] = run_agglomerative_for_k_clusters(k)
		results[str(topics)+"-topics"] = algorithms
	
	write_output_file(results)
	print results

main()
#final()
#special()
#print lsa_kmeans(3)
