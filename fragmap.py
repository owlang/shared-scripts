import sys,argparse
import pysam

# Mimic David Price's FragMap figures from CSHL 2021

# At some point this should be compared to the Price lab version when they fill in the as-of-now empty repostitory: https://github.com/P-TEFb/fragMap

# Basically a tab pileup by fragment size instead of gene-wise...smooshing figure down to x-axis would result in a composite plot and smooshing it left to the y-axis would result in fragment size histogram plot

# Right now it is written to output CDT files that are compatible with ScriptManager for visualization

# Send this to Jordan when done so that he can visualize BZ data with this

def validateBED(bedfilename):
	'''Parse BED file for coordinate intervals and check interval sizes match'''
	COORDS = []
	interval_size = -999
	reader = open(bedfilename,'r')
	for line in reader:
		if(line.find("#")==0):
			continue
		tokens = line.strip().split("\t")
		chr,start,stop = tokens[0],int(tokens[1]),int(tokens[2])
		# Check start/stop validity
		if(start>stop):
			raise RuntimeError("Invalid BED coordinates: %s\n" % (line.strip()))
			return(False)
		# Set interval size if not already set
		if(interval_size==-999):
			interval_size = stop-start
		# Check interval size matches other coords
		if(interval_size!=(stop-start)):
			raise RuntimeError("BED interval size does not match the others: %s\n" % (line.strip()))
			return(False)
		COORDS.append((chr,start,stop))
	reader.close()
	if(len(COORDS)<1):
		sys.stderr.write("BED File must contain at least one coordinate!\n")
		quit()
	return(COORDS)

def bin_fragments(matrix,fbin=1):
	if(fbin==1):
		return(matrix)
	print("Bin matrix into appropriate fragment bins")

def bin_genomic(matrix,gbin=1):
	if(gbin==1):
		return(matrix)
	print("Bin matrix into appropriate genomic bins")

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='Attempt to recreate FragMap figure from David Price lab (code not yet available) for visualization and eventual incorporation into ScriptManager.')

	# parser.add_argument('-d','--data-file', metavar='data_file', dest='data_file', required=True, help='')
	parser.add_argument('-i','--bed-intervals', metavar='bedfile', dest='bedfilepath', required=True, help='The BED intervals to pileup on for FragMap figure')
	parser.add_argument('-b','--bam', metavar='bamfile', dest='bamfilepath', required=True, help='The BAM data to pileup on the BED intervals')

	# Set minimum fragment size (bp) = 0
	# Set maximum fragment size (bp) = 400
	# Set fragment bin size (bp) = 1
	parser.add_argument('--fmin', metavar='minFragSize', dest='fmin', required=False, default=0, help='The minimum fragment size to track (bp)')
	parser.add_argument('--fmax', metavar='maxFragSize', dest='fmax', required=False, default=400, help='The maximum fragment size to track (bp)')
	parser.add_argument('--fbin', metavar='binFragSize', dest='fbin', required=False, default=1, help='The fragment size bin size(bp)')

	# Set genomic bin size (bp) = 1
	parser.add_argument('--gbin', metavar='binIntervalSize', dest='gbin', required=False, default=1, help='The genomic size bin size (bp)')

	# Sum vs norm per bed interval = sum total

	# separate vs combined = combined

	# Set read = Read1
	# read1, read2, all, midpoint

	# Require PE = True
	parser.add_argument('-p','--require-pe', dest='requirePE', required=False, default=True, help='The fragments included in the count must have both reads mapped')

	# Set output composite file = composite_average.out
	# Set output CDT file basename = FragMap_<BAM>_<BED>_<read>_<sep>
	parser.add_argument('-o','--output-cdt', metavar='outfile', dest='outfilepath', required=True, help='The CDT output filepath to save FragMap matrix to')


	args = parser.parse_args()
	return(args)


if __name__ == '__main__':
	'''Main pileup function'''
	args = getParams()
	COORDS = validateBED(args.bedfilepath)
	FRAGMAP = None

	GLEN = COORDS[0][2]-COORDS[0][1]
	FLEN = args.fmax-args.fmin

	# open BAM file
	samfile = pysam.AlignmentFile(args.bamfilepath, "rb")
	# parse BED coords
	for coord in COORDS:
		MATRIX = [[0.]*GLEN] * FLEN
		sys.stderr.write("Local matrix dim: (%i,%i)\n" % (len(MATRIX),len(MATRIX[0])))
		TOTAL_TAGS = 0

		# parse overlapping BAM reads
		print(coord)
		for read in samfile.fetch(coord[0],coord[1]-400,coord[2]+400):
			## Include read filter criteria
			# Filter out unmapped or non-primary alignments
			if(read.is_duplicate):
				print("some read is duplicate")
				continue
			#if(read.is_unmapped or read.is_secondary or read.is_supplementary or read.is_duplicate):
			#	print("some read is unmapped/secondary/supplementary/duplicate")
			#	continue
			# Filter for proper pairs if requiring paired-end data
			if(args.requirePE and (not read.is_paired)):
				#print("some read is not pair")
				# proper?
				continue
			# Filter to include only read1 (may change depending on args criteria)
			#if(not read.is_read1):
				#print("some read is not read1")
			#	continue
			# Later add read.is_reverse for separate flag

			print(read.template_length)
			print(read.cigarstring)
			#print(read.cigarstring)
			index = read.reference_start - coord[1]
			#print(coord[1])
			#print(read.reference_start)
			print(index)
			# Skip reads whose point falls off the interval
			if(index<0 or index>=GLEN):
				print("skip this read")
				continue
			MATRIX[read.template_length][index] += 1
			TOTAL_TAGS += 1
		print(TOTAL_TAGS)

		# Total tag normalize the matrix for this BED Coordinate
		# if(args.totaltag):
		# MATRIX = [ [ i/TOTAL_TAGS for i in row] for row in MATRIX]
		if(FRAGMAP==None):
			FRAGMAP = MATRIX
			continue
		for i in range(FLEN):
			for j in range(GLEN):
				FRAGMAP[i][j] = FRAGMAP[i][j] + MATRIX[i][j]
		#FRAGMAP = [ [ FRAGMAP[i][j]+MATRIX[i][j] for j in range(len(MATRIX[i]))] for i in range(len(MATRIX))]
		print(MATRIX[0][120:130])
		print(MATRIX[50][120:130])
	# Close files
	samfile.close()

	# Reduce by genomic bin size
	#FRAGMAP = bin_genomic(FRAGMAP,args.gbin)
	# Reduce by fragment bin size
	#FRAGMAP = bin_fragments(FRAGMAP,args.fbin)
	print(MATRIX[0][120:130])
	print(MATRIX[50][120:130])

	# Output CDT
	writer = open(args.outfilepath, 'w')
	# print Genomic bin header
	writer.write("\t" + "\t".join(["\t" + str(g) for g in range(len(FRAGMAP[0])) ]) + "\n" )
	nextf = args.fmin
	for f in range(len(FRAGMAP)):
		writer.write("%i\t%i\t%s\n" % (nextf, nextf+args.fbin-1, "\t".join([ str(m) for m in FRAGMAP[f] ]) ))
		nextf = nextf+args.fbin
	writer.close()
