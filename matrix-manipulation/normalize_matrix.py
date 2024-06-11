import sys, getopt
import re
import argparse
import pandas as pd


ALL_NT = ["A","T","C","G"]

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will normalize a matrix file (column wise scale to max=1).

Example: python transpose_matrix.py -i INPUT.cdt -o OUTPUT.cdt''')
	parser.add_argument('-i','--input', metavar='cdt_fn', required=True, help='a CDT file to be normalized')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the normalized matrix')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	# Load data
	i_df = pd.read_csv(args.input, sep="\t", header=0, index_col=0)

	# Loop each column
	for COLUMN in i_df.columns:
		i_df[COLUMN] = 10.0 * i_df[COLUMN]/(max(i_df[COLUMN]))

	# Write divided output
	i_df.to_csv(args.output, sep="\t")
