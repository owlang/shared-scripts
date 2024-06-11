import sys, getopt
import re
import argparse
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import numpy as np
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram


def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will Hierarchical cluster a matrix file.

Example: python hcluster_matrix.py -i INPUT.cdt -o OUTPUT.cdt''')
	parser.add_argument('-i','--input', metavar='cdt_fn', required=True, help='a CDT file to be clustered')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the clustered matrix')
	parser.add_argument('-k','--nclusters', metavar='nClusters', default=3, type=int, help='the number (k) of clusters to look for')

	args = parser.parse_args()
	return(args)


def plot_dendrogram(model, **kwargs):
	# Create linkage matrix and then plot the dendrogram

	# create the counts of samples under each node
	counts = np.zeros(model.children_.shape[0])
	n_samples = len(model.labels_)
	for i, merge in enumerate(model.children_):
		current_count = 0
		for child_idx in merge:
			if child_idx < n_samples:
				current_count += 1  # leaf node
			else:
				current_count += counts[child_idx - n_samples]
		counts[i] = current_count

	linkage_matrix = np.column_stack(
		[model.children_, model.distances_, counts]
	).astype(float)

	# Plot the corresponding dendrogram
	dendrogram(linkage_matrix, **kwargs)

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	# Load data
	i_df = pd.read_csv(args.input, sep="\t", header=0, index_col=0)

	# Cluster matrix
	model = AgglomerativeClustering(distance_threshold=0, n_clusters=None)

	model = model.fit(i_df)
	plt.title("Hierarchical Clustering Dendrogram")
	# plot the top three levels of the dendrogram
	plot_dendrogram(model, truncate_mode="level", p=3)
	plt.xlabel("Number of points in node (or index of point if no parenthesis).")
	plt.show()

	i_df['Clusters'] = model.labels_
	i_df = i_df.sort_values(by=['Clusters'])

	# Write divided output
	i_df.to_csv(args.output, sep="\t")
