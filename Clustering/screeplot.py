import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
from collections import Counter
import matplotlib.pyplot as plt

fname = "lsa.csv"

def create_matrix():
    print "Reading input data from CSV File..."
    mat = np.genfromtxt(fname, delimiter=',').T
    print "Size: ", mat.shape
    return mat

def normalize_mat(mat):
    print "Normalizing"
    mat = normalize(mat, axis=1)
    return mat[:,:20]

def lsa_kmeans(clusters):
    mat = create_matrix()
    print mat
    mat = normalize_mat(mat)
    print "Running K-Means with ", clusters, " clusters..."
    cluster_model = KMeans(n_clusters=clusters).fit(mat)
    print "Finished Running K-Means. Predicting Labels..."
    labels = cluster_model.predict(mat)
    centroids = cluster_model.cluster_centers_
    print centroids
    print labels
    print Counter(labels)
    #for k in np.unique(labels):
     #   mask = labels == k
     #   dist = [np.linalg.norm(mat[mask][i] - centroids[k,:]) for i in range(200)]
    return cluster_model.inertia_

ssd = []
ks = range(2,30)
for k in ks:
    inertia = lsa_kmeans(k)
    ssd.append(inertia)

print ssd
plt.plot(ks, ssd)
plt.show()


