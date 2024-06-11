import sys
import argparse

signal_info = []
signal_counts_f = []
signal_counts_r = []


def getParams():
	'''Parse parameters from the command line'''

	parser = argparse.ArgumentParser(description='''
This script sums the signal between two ScIdx files to output a new ScIdx file.

Example: python sum_two_ScIdx.py -a SIGNAL.scidx -b SIGNAL.scidx > RESULTS.scidx''')
	parser.add_argument('-a','--asignal', metavar='scidxfile', dest='asignal_fn', required=True, help='a ScIdx file to add')
	parser.add_argument('-b','--bsignal', metavar='scidxfile', dest='bsignal_fn', required=True, help='a ScIdx file to add')
	parser.add_argument('-o','--output', metavar='outfile', dest='output_fn', required=True, help='a ScIdx file of summed signal')

	args = parser.parse_args()
	return(args)


def loadSCIDX(scidx_file, indicator):
	'''Load ScIdx file into memory'''

	sys.stderr.write( 'Begin parsing ScIdx file: %s\n' % scidx_file )
	info = []

	# Store Signal information from Signal file
	reader = open(scidx_file,'r')
	for line in reader:
		# skip comments
		if( line.find('#')==0 or line.find('chrom')==0 ):
			continue
		# tokenize and store ScIdx info
		tokens = line.strip().split('\t')
		info.append(( indicator, tokens[0], int(tokens[1]), int(tokens[2]), int(tokens[3]), int(tokens[4]) ))
	reader.close()

	sys.stderr.write( '...finished.\n' )
	return(info)

if __name__ == "__main__":
	'''Merge and write ScIdx file difference.'''

	args = getParams()

	# Load signal & background info
	b_info = loadSCIDX(args.bsignal_fn,'b')
	merge_info = loadSCIDX(args.asignal_fn,'s')
	output_writer = open(args.output_fn,'w')

	# Merge and sort
	merge_info.extend(b_info)
	merge_info = sorted(merge_info, key = lambda x: (x[1], x[2]))
	b_info = ""

	# Merge double-entries
	counter = 0
	while (counter < len(merge_info)):
		# Parse current coord info
		ctokens = merge_info[counter]

		# Check if next coord exists
		if (counter+1 < len(merge_info)):
			ntokens = merge_info[counter+1]

			# Check if next entry has matching chr coords
			if (ctokens[1]==ntokens[1] and ctokens[2]==ntokens[2]):
				# Calculate difference
				new_tokens = [ ctokens[1], str(ctokens[2]), str(ntokens[3]+ctokens[3]), str(ntokens[4]+ctokens[4]), str(ntokens[5]+ctokens[5]) ]
				output_writer.write( '\t'.join(new_tokens) + "\n")
				counter += 2
				continue
		# Print current tokens if next doesn't match
		new_tokens = [ ctokens[1], str(ctokens[2]), str(ctokens[3]), str(ctokens[4]), str(ctokens[5]) ]
		output_writer.write( '\t'.join(new_tokens) + "\n")
		counter += 1
	output_writer.close()
