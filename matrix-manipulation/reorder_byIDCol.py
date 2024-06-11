import sys, getopt
import re
import argparse


ALL_NT = ["A","T","C","G"]

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will reorder a file.

Example: python reorder_byIDCol.py -i INPUT -r REF.tab -c 4 -o OUTPUT''')
	parser.add_argument('-i','--input', metavar='input', required=True, help='a BED file of signal to pileup')
	parser.add_argument('-r','--reference', metavar='tab_fn', required=True, help='a single column of identifiers in desired order')
	parser.add_argument('-c','--column', metavar='index', type=int, required=True, help='the column index of input that contains identifiers (0-based)')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the signal matrix')

	#parser.add_argument('-t','--title', metavar='figure_title', dest='title', required=True, help='')

	args = parser.parse_args()
	return(args)


def loadInput(tab_file, col_idx):
	'''Load coordinate intervals into dictionary keyed on id column'''
	id2coords = {}
	reader = open(tab_file,'r')
	# Update sequence with each variant
	for line in reader:
		tokens = line.strip().split("\t")
		id = tokens[col_idx]
		if(id in id2coords.keys()):
			print("Column Index provided does not contain unique values!! (%s):%s" % (id,line))
			quit()
		id2coords.update({id:line})
	reader.close()
	return id2coords

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	# Load all BED file entries into memory
	id2Lines = loadInput(args.input, args.column)

	N = None
	lines = []
	reader = open(args.reference,'r')
	for line in reader:
		id = line.strip().split("\t")[0]

		new_line = id2Lines.get(id,None)
		if (line == None):
			print("Could not find identifier provided in ordered list!!! (%s)" % id)
			quit()
		lines.append(new_line)
	reader.close()

	# Write CDT
	writer = open(args.output,'w')
	writer.write("".join(lines))
	writer.close()
