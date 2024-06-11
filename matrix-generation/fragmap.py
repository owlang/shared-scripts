import sys,argparse
import pysam
import numpy as np

# Based on David Price's introduced FragMap figure idea from CSHL 2021.

# At some point this should be compared to the Price lab version when they fill in the as-of-now empty repostitory: https://github.com/P-TEFb/fragMap

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
		chr,start,stop,strand = tokens[0],int(tokens[1]),int(tokens[2]),tokens[5]
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
		COORDS.append((chr,start,stop,strand))
	reader.close()
	if(len(COORDS)<1):
		sys.stderr.write("BED File must contain at least one coordinate!\n")
		quit()
	return(COORDS)

def bin_fragments(matrix,fbin=1):
	if(fbin==1):
		return(matrix)
	print("Bin matrix into appropriate fragment bins")
	# print(matrix)
	BINNED_MATRIX = np.zeros((1,np.shape(matrix)[1]))
	index = 0
	for i in range(np.shape(matrix)[0]):
		# print("(index,i): (%i, %i)" % (index, i))
		if( i % fbin==0 and i!=0):
			BINNED_MATRIX = np.vstack((BINNED_MATRIX, matrix[i,:]))
			index += 1
		else:
			BINNED_MATRIX[index,:] = np.add(BINNED_MATRIX[index,:], matrix[i,:])
		# print(BINNED_MATRIX)
	# print("FINAL...")
	# print(BINNED_MATRIX)
	return(BINNED_MATRIX)

def bin_genomic(matrix,gbin=1):
	if(gbin==1):
		return(matrix)
	print("Bin matrix into appropriate genomic bins")

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description= \
	'''Attempt to recreate FragMap figure from David Price lab (code not yet available) for visualization and eventual incorporation into ScriptManager.

	Basically a tab pileup by fragment size instead of gene-wise...
		- smooshing figure down to x-axis would result in a composite plot and
		- smooshing it left to the y-axis would result in fragment size histogram plot

	Right now it is written to output CDT files that are compatible with ScriptManager for visualization
	''')

	# parser.add_argument('-d','--data-file', metavar='data_file', dest='data_file', required=True, help='')
	parser.add_argument('-i','--bed-intervals', metavar='bedfile', dest='bedfilepath', required=True, help='The BED intervals to pileup on for FragMap figure')
	parser.add_argument('-b','--bam', metavar='bamfile', dest='bamfilepath', required=True, help='The BAM data to pileup on the BED intervals')

	# Set minimum fragment size (bp) = 0
	# Set maximum fragment size (bp) = 400
	# Set fragment bin size (bp) = 1
	parser.add_argument('--fmin', metavar='minFragSize', dest='fmin', type=int, required=False, default=0, help='The minimum fragment size to track (bp)')
	parser.add_argument('--fmax', metavar='maxFragSize', dest='fmax', type=int, required=False, default=400, help='The maximum fragment size to track (bp)')
	parser.add_argument('--fbin', metavar='binFragSize', dest='fbin', type=int, required=False, default=1, help='The fragment size bin size(bp)')

	# Set genomic bin size (bp) = 1
	parser.add_argument('--gbin', metavar='binIntervalSize', dest='gbin', required=False, default=1, help='The genomic size bin size (bp)')

	# Sum vs norm per bed interval = sum total

	# separate vs combined = combined
	parser.add_argument('--separate', action='store_true', dest='separate', help="Store FragMap matrices in a strand-specific manner")

	# Set read = 1
	# fragment, read1, read2, midpoint
	parser.add_argument('--read', metavar='readEncoding', dest='read', type=int, required=False, default=1, help= \
	'''The positional encoding along the sequenced fragment to use:
		0 = full fragment length;
		1 = 5\' end of read 1 (default);
		2 = 5\' end of read 2;
		3 = fragment midpoint;
	''')

	# Require PE = True
	parser.add_argument('-p','--require-pe', dest='requirePE', action='store_true', help='The fragments included in the count must have both reads mapped')

	# Set output CDT file basename = FragMap_<BAM>_<BED>_<read>_<sep>
	parser.add_argument('-o','--output-cdt', metavar='outfile', dest='outfilepath', required=True, help='The CDT output basename to save FragMap matrix/ces to')

	args = parser.parse_args()

	# Re-adjust requirePE arg according to read encoding
	if(args.read in [0,3]):
		args.requirePE = true
		print("Non-Read1/2 5' end pileups not supported yet.")
		exit()

	return(args)

def unit_tests():
	# TEST: Fragment Binning from test matrix
	bin_fragments(np.arange(30).reshape(10,3),4)

if __name__ == '__main__':
	'''Main pileup function'''

	args = getParams()

	COORDS = validateBED(args.bedfilepath)
	GLEN = COORDS[0][2]-COORDS[0][1]
	FLEN = args.fmax-args.fmin +1
	print("COORDS: %i coordinates loaded from %s" % (len(COORDS),args.bedfilepath))
	print("GLEN(bp): %i and FLEN(bp): %i" % (GLEN,FLEN))
	print("Fragment Limits(bp): %i to %i" % (args.fmin,args.fmax))
	print("Fragment Bins(bp): %i" % (args.fbin))
	print("Genomic Bins(bp): %i" % (args.gbin))
	print("Strand Separated: %r" % (args.separate))
	print("Outpath basename: %s" % (args.outfilepath))

	# Initialize separate matrices for same and opposite strand
	MATRIX_SAME = np.zeros((FLEN, GLEN))
	MATRIX_OPPOSITE = None
	if(args.separate):
		MATRIX_OPPOSITE = np.zeros((FLEN, GLEN))
	sys.stderr.write("Local matrix dim: (%i,%i)\n" % (len(MATRIX_SAME),len(MATRIX_SAME[0])))

	# print("x: %i" % len(MATRIX_SAME))
	# print("y: %i" % len(MATRIX_SAME[0]))
	# open BAM file
	samfile = pysam.AlignmentFile(args.bamfilepath, "rb")
	# parse BED coords
	for coord in COORDS:
		COORD_TAGS = 0

		# parse overlapping BAM reads
		print(coord)
		for read in samfile.fetch(coord[0],coord[1]-400,coord[2]+400):
			## Include read filter criteria
			# Filter out unmapped or non-primary alignments
			if(read.is_unmapped):
				print("thisRead is unmapped")
				continue
			if(read.is_secondary):
				print("thisRead is secondary")
				continue
			if(read.is_supplementary):
				print("thisRead is secondary")
				continue
			if(read.is_duplicate):
				print("thisRead is a duplicate")
				continue
			# Filter for proper pairs if requiring paired-end data
			if(args.requirePE and (not read.is_paired)):
				print("thisRead is not pair")
				# proper?
				continue
			# Filter to include only read1/read2 according to encoding
			if(args.read==0 or args.read==1 or args.read==3):
				if(read.is_read2):
					print("thisRead != R1 when required R1/M/F encoding")
					continue
			elif(args.read == 2):
				if(read.is_read1):
					print("thisRead != R2 when required R2 encoding")
					continue

			# Determine if read is same or opposite stranded
			SAME = read.is_reverse == (coord[3]=="-")

			# Select Read1 5' end position
			index = read.reference_start - coord[1]
			if((read.is_reverse and args.read==1) or (not read.is_reverse and args.read==2)):
				index = read.reference_end - coord[1] - 1
			# if(coord[3]=="-"):
			# 	index = GLEN - index

			# Skip reads whose mark falls off the interval
			if(index<0 or index>=GLEN):
				print("thisRead falls outside coord interval")
				continue
			# Skip reads whose insert size falls outside captured interval
			if(read.template_length<args.fmin or read.template_length>args.fmax):
				print("fragment size falls outside coord interval")
				continue

			# Update appropriate MATRIX variable
			if(not SAME and args.separate):
				MATRIX_OPPOSITE[read.template_length-args.fmin][index] += 1
			else:
				# sys.stderr.write(str(read.template_length-args.fmin) + "\n")
				MATRIX_SAME[read.template_length-args.fmin][index] += 1
			COORD_TAGS += 1
		print(COORD_TAGS)

		# Total tag normalize the matrix for this BED Coordinate
		# if(args.totaltag):
		# MATRIX = [ [ i/TOTAL_TAGS for i in row] for row in MATRIX]
		# for i in range(FLEN):
		# 	for j in range(GLEN):
		# 		MATRIX_SAME[i][j] = FRAGMAP[i][j] + MATRIX[i][j]
		#FRAGMAP = [ [ FRAGMAP[i][j]+MATRIX[i][j] for j in range(len(MATRIX[i]))] for i in range(len(MATRIX))]
	# Close files
	samfile.close()

	# Reduce by genomic bin size
	#FRAGMAP = bin_genomic(FRAGMAP,args.gbin)
	# Reduce by fragment bin size
	MATRIX_SAME = bin_fragments(MATRIX_SAME,args.fbin)
	if(args.separate):
		MATRIX_OPPOSITE = bin_fragments(MATRIX_OPPOSITE,args.fbin)


	# Output CDT (sense)
	OUTFILE_SAME = args.outfilepath + "_sense.cdt"
	if(args.read==0 or args.read==3):
		OUTFILE_SAME = args.outfilepath + "_combined.cdt"
	writer = open(OUTFILE_SAME, 'w')
	# print Genomic bin header
	writer.write("\t" + "\t".join(["\t" + str(g) for g in range(len(MATRIX_SAME[0])) ]) + "\n" )
	nextf = args.fmin
	for f in range(np.shape(MATRIX_SAME)[0]):
		writer.write("%i\t%i\t%s\n" % (nextf, nextf+args.fbin-1, "\t".join([ str(MATRIX_SAME[f][m]) for m in range(np.shape(MATRIX_SAME)[1]) ]) ))
		nextf = nextf+args.fbin
	writer.close()

	# Output CDT (anti)
	if(args.separate):
		writer = open(args.outfilepath + "_anti.cdt", 'w')
		# print Genomic bin header
		writer.write("\t" + "\t".join(["\t" + str(g) for g in range(len(MATRIX_OPPOSITE[0])) ]) + "\n" )
		nextf = args.fmin
		for f in range(np.shape(MATRIX_OPPOSITE)[0]):
			writer.write("%i\t%i\t%s\n" % (nextf, nextf+args.fbin-1, "\t".join([ str(MATRIX_OPPOSITE[f][m]) for m in range(np.shape(MATRIX_OPPOSITE)[1]) ]) ))
			nextf = nextf+args.fbin
		writer.close()
