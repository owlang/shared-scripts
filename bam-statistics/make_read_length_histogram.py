import sys, getopt
from os.path import isfile, join, splitext
import seaborn as sns
import matplotlib.pyplot as plt
import pysam
import pandas as pd
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will plot the mapped read length (Nanopore or Read1 filter).

Example: python make_read_length_histogram.py -i INPUT.bam -o OUTPUT.png -n 200 -x 1000''')
	parser.add_argument('-i','--input', metavar='input', required=True, help='a BAM file to stat')

	parser.add_argument('-o','--output', metavar='output', required=True, help='the filepath to histogram image (.png or .svg)')
	parser.add_argument('-x','--max', metavar='max_val', type=int, default=-1, help='max read length to keep')
	parser.add_argument('-n','--min', metavar='min_val', type=int, default=-1, help='min read length to keep')
	parser.add_argument('--overflow', action='store_true', help='include an overflow bin')

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

	rlength_tally = {}

	# open input BAM file
	samfile = pysam.AlignmentFile(args.input, "rb")
	# Iterate across all reads
	for sr in samfile.fetch():
		rlen = sr.reference_length
		# filter max if specified
		if (args.max > -1 and rlen > args.max):
			# print("max %s" % sr.reference_length)
			# Add an overlfow bin
			if (args.overflow):
				rlen = args.max + 1
			else:
				continue
		# filter min if specified
		if (args.min > -1 and rlen < args.min):
			# print("min %s" % sr.reference_length)
			continue

		# tally if passed filter
		rlength_tally.setdefault(rlen,0)
		rlength_tally[rlen] += 1
	# Close files
	samfile.close()

	# Structure tally into df
	data = pd.DataFrame.from_dict(rlength_tally, orient='index', columns=['Read Count'])
	data['Read Length'] = data.index
	print(data)


	# Scatter Plot or other type of plot here!!!!!
	# could swap out for 'swarmplot' and google seaborn library for others
	ax = sns.barplot(x='Read Length', y="Read Count", data=data)

	# Label y-axis titles
	plt.ylabel("Read Count")

	# Label x-axis titles
	ax.tick_params(axis='x', rotation=20)
	plt.xlabel("Read Length")

	# Output...
	if(args.output==None):
		plt.show()
	elif(splitext(args.output)[-1]!=".svg"):
		sys.stderr.write("Please use SVG file extension to save output!\n")
		plt.savefig(args.output, transparent=True)
	else:
		plt.savefig(args.output, transparent=True)
		sys.stderr.write("SVG written to %s\n" % args.output)