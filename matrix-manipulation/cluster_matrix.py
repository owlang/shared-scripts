import sys, getopt
import re
import argparse
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np


def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will k-means cluster a matrix file.

Example: python cluster_matrix.py -i INPUT.cdt -o OUTPUT.cdt''')
	parser.add_argument('-i','--input', metavar='cdt_fn', required=True, help='a CDT file to be clustered')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the clustered matrix')
	parser.add_argument('-k','--nclusters', metavar='nClusters', default=3, type=int, help='the number (k) of clusters to look for')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	# Load data
	i_df = pd.read_csv(args.input, sep="\t", header=0, index_col=0)

	# Cluster matrix
	kmeans = KMeans(n_clusters=args.nclusters).fit(i_df)
	i_df['Clusters'] = kmeans.labels_
	i_df = i_df.sort_values(by=['Clusters'])

	# Write divided output
	i_df.to_csv(args.output, sep="\t")
