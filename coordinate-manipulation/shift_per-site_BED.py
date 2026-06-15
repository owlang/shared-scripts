#!/usr/bin/env python3
import sys, warnings
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will reorder a file.

Example: python reorder_byIDCol.py -i INPUT.bed -r REF.tsv -c 4 -o OUTPUT.bed''')
	parser.add_argument('-i','--input', metavar='bed_fn', required=True, help='a BED file to shift')
	parser.add_argument('-r','--reference', metavar='tsv_fn', required=True, help='a TSV file with the first column filled with ids matching the .bed entries and the second column indicating the strand-aware shift distance')
	parser.add_argument('-o','--output', metavar='bed_fn', required=True, help='a BED file with the distance scores')

	parser.add_argument('--ignore-empty', action='store_true', help='ignore INPUT.bed entries that haven\'t a provided shift values in -r (no shift applied)')
	parser.add_argument('--ignore-non-numeric', action='store_true', help='ignore REF.tsv entries that provided non-numeric shift values in -r (no shift applied)')

	args = parser.parse_args()
	return(args)

def load_shifts(tsv_fn, ignore_non_int=False):
	id2shift = {}
	non_int = False
	with open(tsv_fn,'r') as reader:
		for line in reader:
			tokens = line.strip().split('\t')
			if tokens[0] == 'YORF':
				continue
			try:
				id2shift.update({tokens[0]:int(tokens[1])})
			except ValueError:
				non_int = True
				assert ignore_non_int, "Some non-numeric values were parsed from this reference input file. Please use --ignore-non-numeric if you wish for these to be ignored (no shift applied)."
	if non_int:
		warnings.warn("Some non-numeric values were parsed from this reference input file. They were ignored (no shift applied).")
	return(id2shift)

if __name__ == "__main__":
	'''Calls max signal within CDT pileup and returns BED-formatted coordinates for the max signal positions.'''

	args = getParams()

	# Load shift vals
	id2shift = load_shifts(args.reference, args.ignore_non_numeric)

	empty_found = False

	writer = open(args.output,'w')
	# Parse pileup
	with open(args.input,'r') as fh:
		for line in fh:
			# Skip comment line
			if(line.find("#")==0):
				continue

			tokens = line.strip().split('\t')

			assert len(tokens)>=6, f"Check your input BED file contains at least 6 columns. TOKENS: {';'.join(tokens)}"
			assert (tokens[3] in id2shift.keys()), f"Check that the .bed ID entry ({tokens[3]}) has a shift value in your --reference input file."

			if [tokens[3]] not in id2shift.keys():
				empty_found = True
				assert args.ignore_empty, "Some .bed records did not have IDs parsed from REF.tsv. Please use --ignore-non-numeric if you wish for these to be ignored (no shift applied)."
			shift_dist = [tokens[3]]

			# Strand-dependent shift
			if(tokens[5]=='-'):
				tokens[1] = str(int(tokens[1]) - shift_dist)
				tokens[2] = str(int(tokens[2]) - shift_dist)
			else:
				tokens[1] = str(int(tokens[1]) + shift_dist)
				tokens[2] = str(int(tokens[2]) + shift_dist)

			# Write new coordinate to BED file output
			writer.write(f"{'\t'.join(tokens)}\n")

	writer.close()
