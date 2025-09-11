import sys
import argparse
import pandas as pd

def getParams():
	'''Parse parameters from the command line'''

	parser = argparse.ArgumentParser(description='''
This script gets the element-wise sum between two CDT files to output a new CDT file.

Example: python add_two_CDT.py -a CONTROL.cdt -b PERTURB.cdt -o RESULTS.cdt''')
	parser.add_argument('-a','--control', metavar='cdtfile', dest='control_fn', required=True, help='a CDT file to add')
	parser.add_argument('-b','--perturb', metavar='cdtfile', dest='perturb_fn', required=True, help='a CDT file to add')
	parser.add_argument('-o','--output', metavar='outfile', dest='output_fn', required=True, help='a CDT file of site-by-site sum')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Add two CDT files and write the result.'''

	args = getParams()

	# Load signal & background info
	dfa = pd.read_csv(args.control_fn, sep="\t", header=0, index_col=[0,1])
	dfb = pd.read_csv(args.perturb_fn, sep="\t", header=0, index_col=[0,1])
	# Add
	added = (dfb + dfa)
	# Write output
	added.to_csv(args.output_fn, sep="\t")
