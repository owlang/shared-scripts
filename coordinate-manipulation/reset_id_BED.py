import sys, argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script resets the id column of a BED file.

# example-input.bed
chr1	30	70	NAME-1	0	+
chr2	150	190	NAME-2	0	-

# example-output.bed
chr1	30	70	chr1:30-70	0	+
chr2	150	190	chr2:150-190	0	-

Example: python reset_id_BED.py -i COORD.bed -o NEW.bed''')
	parser.add_argument('-i','--input', metavar='bedfile', required=True, help='a BED file to reset id for')
	parser.add_argument('-o','--output', metavar='outfile', required=True, help='a BED file of the deduplicated BED coord IDs (unordered)')
	parser.add_argument('--strand', action='store_true', help='use strand information in new ID')
	parser.add_argument('--underscore', action='store_true', help='id tokens purely delimited by underscores')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Write BED file in new order.'''

	# Parse params
	args = getParams()

	# Open file handles
	reader = open(args.input, 'r')
	writer = open(args.output, 'w')
	for line in reader:
		tokens = line.strip().split('\t')

		# Confirm 6 columns
		assert len(tokens) >= 6, f"Not enough columns in entry: {line}"

		# Reformat id token
		if args.underscore:
			tokens[3] = '_'.join(tokens[:3])
		else:
			tokens[3] = f"{tokens[0]}:{tokens[1]}-{tokens[2]}"
		if args.strand:
			tokens[3] += f"_{tokens[5]}"

		# Write tokens
		writer.write('\t'.join(tokens) + "\n")

	# Close file handles
	writer.close()
	reader.close()
