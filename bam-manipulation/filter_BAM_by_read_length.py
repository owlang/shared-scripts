import sys, getopt
import pysam
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will filter a BAM file by mapped read length (Nanopore or Read1 filter).

Example: python filter_BAM_by_read_length.py -i INPUT.bam -o OUTPUT.bam -x 1000 -n 200''')
	parser.add_argument('-i','--input', metavar='input', required=True, help='a BAM file to filter')

	parser.add_argument('-o','--output', metavar='output', required=True, help='the BAM file filtered by read lengths')
	parser.add_argument('-x','--max', metavar='max_val', type=int, default=-1, help='max read length to keep')
	parser.add_argument('-n','--min', metavar='min_val', type=int, default=-1, help='min read length to keep')

	args = parser.parse_args()
	return(args)

def validateBAM(bam):
	'''Validate BAM file'''
	try:
		samfile = pysam.AlignmentFile(bam, "rb")
		index = samfile.check_index()
		samfile.close()
		return index
	except:
		print("BAM index not detected.\nAttempting to index now...\n")
		pysam.index(str(bam))
		if not os.path.isfile(bam + ".bai"):
			raise RuntimeError("BAM indexing failed, please check if BAM file is sorted")
			return False
		print("BAM index successfully generated.\n")
		return True

if __name__ == "__main__":
	'''Write BAM file that meets the filter criteria.'''
	args = getParams()

	# Validate BAM file
	if(not validateBAM(args.input)):
		sys.exit(-1)

	print("Max: %i" % args.max)
	print("Min: %i" % args.min)
	print("Input: " + args.input)
	print("Output: " + args.output)

	# open input BAM file
	samfile = pysam.AlignmentFile(args.input, "rb")
	# open output BAM file
	filterfile = pysam.AlignmentFile(args.output, "wb", template=samfile)
	# Iterate across all reads
	for sr in samfile.fetch():
		# filter max if specified
		if (args.max > -1 and sr.reference_length > args.max):
			# print("max %s" % sr.reference_length)
			continue
		# filter min if specified
		if (args.min > -1 and sr.reference_length < args.min):
			# print("min %s" % sr.reference_length)
			continue
		# write if passed filter
		filterfile.write(sr)
	# Close files
	samfile.close()
	filterfile.close()