import sys, getopt
import re
import argparse


def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script to deduplicate BED coordinates, selecting coord ids to keep by score value.

Example: python unique_BED_coord_byScore.py -i COORD.bed [-a] [-x -n] -o ID.txt''')
	parser.add_argument('-i','--input', metavar='bedfile', required=True, help='a BED file to unique (must have unique identifiers)')
	parser.add_argument('-o','--output', metavar='outfile', required=True, help='a TXT file of the deduplicated BED coord IDs (unordered)')
	parser.add_argument('-a','--absolute', action="store_true", help='Use absolute score values')

	# parse selection of representative criteria
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-x','--max', action="store_true", help='Keep coordinate with maxiumum score value (if matching, first instance is used)')
	group.add_argument('-n','--min', action="store_true", help='Keep coordinate with minimum score value  (if matching, first instance is used)')

	args = parser.parse_args()
	return(args)


def loadBED(bed_file):
	'''Load coordinate intervals into dictionary keyed on id column'''
	# chr4	130537	130538	YDL184C	53	-
	# chr4	221853	221854	YDL133C-A	52	-
	# chr15	649054	649055	YOR167C	47	-
	# chr4	310216	310217	YDL081C	94	-
	# chr15	253637	253638	YOL040C	60	-
	# chr4	1239380	1239381	YDR382W	112	+
	# chr15	1028682	1028683	YOR369C	57	-
	# chr7	366041	366042	YGL076C	45	-
	# chr4	1301574	1301575	YDR418W	42	+
	# chr8	36081	36082	YHL033C	56	-

	coord2ids = {}
	reader = open(bed_file,'r')
	# Update sequence with each variant
	counter = 0
	for line in reader:
		tokens = line.strip().split("\t")
		coord = '%s:%s-%s' % (tokens[0], tokens[1], tokens[2])
		value = ( tokens[3], int(tokens[4]) )
		if (coord not in coord2ids.keys()):
			coord2ids.update({ coord:[value] })
		else:
			coord2ids[coord].append(value)
		counter += 1
	reader.close()
	print('%i coords --> %i unique (%i diff)' % (counter, len(coord2ids), counter-len(coord2ids)))
	return coord2ids

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()
	print(args)

	coord2ids = loadBED(args.input)

	writer = open(args.output, 'w')
	for c in coord2ids.keys():
		coord_group = coord2ids[c]
		# Perform score operations if non-unique
		if (len(coord_group) > 1):
			# Sort id-score tuples by score (apply absolute if flagged)
			coord_group_sorted = sorted(coord_group,key=lambda x: x[1])
			if (args.absolute):
				coord_group_sorted = sorted(coord_group,key=lambda x: abs(x[1]))
			# print("=======")
			# print(coord_group)
			# print(coord_group_sorted)

			# Overwrite unsorted with sorted
			coord_group = coord_group_sorted

			# if (args.max):
			# 	print(coord_group[-1][0])
			# elif(args.min):
			# 	print(coord_group[0][0])

		# Write min/max accordingly (doesn't matter which if only one value in list)
		if (args.max):
			writer.write(coord_group[-1][0] + "\n")
		elif(args.min):
			writer.write(coord_group[0][0] + "\n")
	writer.close()
