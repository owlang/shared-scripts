import sys
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will pileup BedGraph scores.

Example: python reorder_byIDCol.py -i INPUT -r REF.tab -c 4 -o OUTPUT''')
	parser.add_argument('-i','--input', metavar='bedgraph_fn', required=True, help='a BedGraph file of signal to pileup')
	parser.add_argument('-r','--reference', metavar='bed_fn', required=True, help='a BED file of distance calculated to')
	parser.add_argument('-o','--output', metavar='bed_fn', required=True, help='a BED file with the distance scores')

	#parser.add_argument('-t','--title', metavar='figure_title', dest='title', required=True, help='')

	args = parser.parse_args()
	return(args)

def loadBedGraph(bg_fn):
	coord2score = {}
	reader = open(bg_fn,'r')
	for line in reader:
		if (line.find("chrom")==0):
			continue
		tokens = line.strip().split('\t')
		coord2score.setdefault(tokens[0], {})
		for i in range(int(tokens[1]), int(tokens[2])):
			coord2score[tokens[0]].update({i:float(tokens[3])})
	reader.close()
	return(coord2score)

if __name__ == "__main__":
	'''Calls max signal within CDT pileup and returns BED-formatted coordinates for the max signal positions.'''

	# Load reference BED coordinates
	args = getParams()
	scoreDict = loadBedGraph(args.input)
	# print(scoreDict)

	# Initialize indicator for when header is written
	headerWritten = False

	writer = open(args.output,'w')
	# Parse pileup
	reader = open(args.reference,'r')
	for line in reader:
		# Skip first line
		tokens = line.strip().split('\t')

		# Load RefPT info
		chrstr = tokens[0]
		start = int(tokens[1])
		stop = int(tokens[2])
		id = tokens[3]
		strand = tokens[5]

		# Write header if not yet written
		if (headerWritten):
			writer.write("YORF\tNAME\t" + "\t".join([str(i) for i in range(stop-start)]) + "\n")

		# Write CDT values
		values = [str(scoreDict[chrstr].get(i,0)) for i in range(start, stop)]
		if (strand == "-"):
			values.reverse()
		writer.write(id + "\t" + id + "\t" + "\t".join(values) + "\n")
	reader.close()
	writer.close()
