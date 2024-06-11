import sys
import argparse
import pandas as pd

def getParams():
	'''Parse parameters from the command line'''

	parser = argparse.ArgumentParser(description='''
This script gets the log fold change between two CDT files to output a new CDT file.

Example: python logfold_CDT_change.py -a CONTROL.cdt -b PERTURB.cdt -o RESULTS.cdt''')
	parser.add_argument('-a','--control', metavar='cdtfile', dest='control_fn', required=True, help='a CDT file to get log fold change from (base)')
	parser.add_argument('-b','--perturb', metavar='cdtfile', dest='perturb_fn', required=True, help='a CDT file to get log fold change from (change)')
	parser.add_argument('-o','--output', metavar='outfile', dest='output_fn', required=True, help='a CDT file of site-by-site log fold change')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Logfold two CDT files and write the result.'''

	args = getParams()

	# Load signal & background info
	dfa = pd.read_csv(args.control_fn, sep="\t", header=0, index_col=[0,1])
	dfb = pd.read_csv(args.perturb_fn, sep="\t", header=0, index_col=[0,1])
	# LogFold
	folded = dfb / dfa
	# Write output
	folded.to_csv(args.output_fn, sep="\t", na_rep='NaN')
