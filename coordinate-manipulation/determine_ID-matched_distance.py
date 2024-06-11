import sys
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will reorder a file.

Example: python reorder_byIDCol.py -i INPUT -r REF.tab -c 4 -o OUTPUT''')
	parser.add_argument('-i','--input', metavar='bed_fn', required=True, help='a BED file of signal to pileup')
	parser.add_argument('-r','--reference', metavar='bed_fn', required=True, help='a BED file of distance calculated to')
	parser.add_argument('-o','--output', metavar='bed_fn', required=True, help='a BED file with the distance scores')

	#parser.add_argument('-t','--title', metavar='figure_title', dest='title', required=True, help='')

	args = parser.parse_args()
	return(args)

def loadBED(bed_fn):
	id2bed = {}
	reader = open(bed_fn,'r')
	for line in reader:
		tokens = line.strip().split('\t')
		id = tokens[3]
		id2bed.update({id:tokens})
	reader.close()
	return(id2bed)

if __name__ == "__main__":
	'''Calls max signal within CDT pileup and returns BED-formatted coordinates for the max signal positions.'''

	# Load reference BED coordinates
	args = getParams()
	coords = loadBED(args.reference)

	writer = open(args.output,'w')
	# Parse pileup
	reader = open(args.input,'r')
	for line in reader:
		# Skip first line
		if(line.find("YORF")==0):
			continue
		tokens = line.strip().split('\t')
		# if(tokens[3]=="YHL033C"):
		# 	continue
		id = tokens[3]

		# Get pre-loaded coord
		r_coord = coords.get(id,[""]*6)
		distance = -10
		if(r_coord[5]=='-' and tokens[5]=='-'):
			r_mid = int(r_coord[1]) + (int(r_coord[2]) - int(r_coord[1]))//2
			t_mid = int(tokens[1]) + (int(tokens[2]) - int(tokens[1]))//2
			distance = r_mid - t_mid
		if(r_coord[5]!='-' and tokens[5]!='-'and r_coord[1]!=""):
			r_mid = int(r_coord[1]) + (int(r_coord[2]) - int(r_coord[1]))//2
			t_mid = int(tokens[1]) + (int(tokens[2]) - int(tokens[1]))//2
			distance = t_mid - r_mid

		# Write new coordinate to BED file output
		writer.write("\t".join(r_coord) + "\t" + "\t".join(tokens) + "\t" + str(distance) + "\n")
	reader.close()
	writer.close()
