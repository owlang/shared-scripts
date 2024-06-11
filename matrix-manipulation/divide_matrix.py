import sys, getopt
import re
import argparse
import pandas as pd
import numpy as np

ALL_NT = ["A","T","C","G"]

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will divide two matrix files.

Example: python divide_matrix.py -a NUMERATOR.cdt -b DIVISOR.cdt -o OUTPUT.cdt''')
	parser.add_argument('-a','--numerator', metavar='cdt_fn', required=True, help='a CDT file that represents the numerator')
	parser.add_argument('-b','--divisor', metavar='cdt_fn', required=True, help='a CDT file that represents the divisor')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the divided matrix')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	# Load data
	a_df = pd.read_csv(args.numerator, sep="\t", header=0, index_col=0)
	b_df = pd.read_csv(args.divisor, sep="\t", header=0, index_col=0)

	# Match column_ids
	b_df.columns = a_df.columns

	# Divide values
	a_df = a_df.divide(b_df)
	a_df.replace([np.inf, -np.inf], 1000, inplace=True)
	a_df.replace([np.NaN], 0, inplace=True)

	# Write divided output
	a_df.to_csv(args.output, sep="\t")
