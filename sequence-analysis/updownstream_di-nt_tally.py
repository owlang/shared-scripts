import sys, argparse, csv, os
import numpy as np
import pandas as pd
import pysam
import math

comp = {'A':'T', 'T':'A',
		'C':'G', 'G':'C',
		'N':'N'}
NT = ['A', 'T', 'C', 'G']

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description = """
============
Get tally of dinucleotides around 5' cut site from reads in a BAM file. Ignores N-containing sequences around the read.
============
		Single read example output:
		                   |------------------->   (Read, '|' indicates 5' cut site, '>' indicates read direction)
		     A  T  C  G  T  T  A  T  C  A  G  G    (Sequence)
		    -5 -4 -3 -2 -1 +1 +2 +3 +4 +5 +6 +7    (Position with respect to cut site, range defined by `-l 5` and `-r 7` flags, note zero not included)
		AA   0  0  0  0  0  0  0  0  0  0  0  NaN  (Each dinucleotide tally count, each column should sum to the number of reads analyzed)
		AT   1  0  0  0  0  0  1  0  0  0  0  NaN   Note: keep NaN in last column for clarity of dinucleotide offset
		AC   0  0  0  0  0  0  0  0  0  0  0  NaN
		AG   0  0  0  0  0  0  0  0  0  1  0  NaN
		TA   0  0  0  0  0  1  0  0  0  0  0  NaN
		TT   0  0  0  0  1  0  0  0  0  0  0  NaN
		TC   0  1  0  0  0  0  0  1  0  0  0  NaN
		TG   0  0  0  0  0  0  0  0  0  0  0  NaN
		CA   0  0  0  0  0  0  0  0  1  0  0  NaN
		CT   0  0  0  0  0  0  0  0  0  0  0  NaN
		CC   0  0  0  0  0  0  0  0  0  0  0  NaN
		CG   0  0  1  0  0  0  0  0  0  0  0  NaN
		GA   0  0  0  0  0  0  0  0  0  0  0  NaN
		GT   0  0  0  1  0  0  0  0  0  0  0  NaN
		GC   0  0  0  0  0  0  0  0  0  0  0  NaN
		GG   0  0  0  0  0  0  0  0  0  0  1  NaN
""", formatter_class = argparse.RawTextHelpFormatter)

	parser.add_argument('-i','--input', metavar='bam_fn', required=True, help='the BAM file of reads to analyze')
	parser.add_argument('-g','--genome', metavar='fasta_fn', required=True, help='the genomic sequence FASTA file')
	parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited k-mer list with read tally counts')

	parser.add_argument('-l', metavar='dist_up', type=int, default=10, help='number of bp upstream of cut site to tally (negative values exclude cut site from examined range)')
	parser.add_argument('-r', metavar='dist_down', type=int, default=10, help='number of bp downstream of cut site to tally (negative values exclude cut site from examined range)')

	parser.add_argument('-p', action='store_true', help='only check properly paired reads')
	parser.add_argument('--read1', action='store_true', help='only check read 1 cut sites')
	parser.add_argument('--read2', action='store_true', help='only check read 2 cut sites')

	args = parser.parse_args()

	if (args.read1 and args.read2):
		raise Exception ("Cannot select both read1 and read2")

	if ((-1*args.l) > args.r):
		raise Exception ("Cannot use left bound that is downstream from right bound")

	return(args)

def reverse_complement(seq):
	rc = ""
	for char in seq:
		rc = comp[char] + rc
	return(rc)

def validateBAM(bam):
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

def initialize_di_nt_df(left, right):
	'''Initialize df for tracking dinucleotide tallies by position relative to cut site'''
	
	# Initialize row index labels of all 16 dinucleotides
	row_labels = [one+two for one in NT for two in NT]

	# Initialize column labels (range without 0)
	column_names = [i for i in range((-1*left), right)] # asymmetric expansion
	# column_names = [i for i in range((-1*half_window), half_window)]  #symmetric expansion

	# Initialize matrix of zeros with labels (NaN in last column)
	df = pd.DataFrame(np.nan, columns=column_names, index=row_labels)
	df.iloc[:,:-1] = 0

	# print(df)
	return(df)


# Main program which takes in input parameters
if __name__ == '__main__':
	args = getParams()

	# Validate BAM file
	if(not validateBAM(args.input)):
		sys.exit(-1)

	print("BAM file: ", args.input)
	print("Genome fasta: ", args.genome)
	print("Output file: ", args.output)

	# Open the BAM file
	bam = pysam.AlignmentFile(args.input, "rb")

	# Open the genome file
	genome = pysam.FastaFile(args.genome)

	# Initialize a dictionary to store dinucleotide counts by position
	df_counts = initialize_di_nt_df(args.l, args.r)

	counter = 0

	# Iterate through each read in the BAM file
	for read in bam:
		# Skip unmapped, secondary, and supplementary reads
		if read.is_unmapped or read.is_secondary or read.is_supplementary:
			continue
		# Skip based on user requirements for proper pair
		if ((not read.is_proper_pair) and args.p):
			continue
		# Skip based on user requirements for read1/2
		if ((not read.is_read1) and args.read1):
			continue
		if ((not read.is_read2) and args.read2):
			continue

		# Check chr name
		ref_name = read.reference_name
		if ref_name not in genome.references:
			raise Exception("Reference sequence name %s does not exist in provided genome" % ref_name)

		ref_pos = -1
		start = -1
		end = -1

		# Get the reference position of the start of read 1
		#                             -l 2 -r 1
		#        |------->   + R1
		#        <-------|   - R2
		#        <-------|   - R1
		#        |------->   + R2
		#        *         *     start, end --> 4, 9
		#  1 2 3 4 5 6 7 8 9
		#    - - | -             (+) 2:6
		#              - | - -   (-) 6:10

		# Calculate the window range from the cut site position
		if(read.is_reverse):
			start = read.reference_end - args.r - 1 # -1 to move from exclusive to inclusive
			end = read.reference_end + args.l
			# print("(%s) %i --> %i --> %i" % ("-", start, read.reference_end - 1 , end))
		else:
			start = read.reference_start - args.l
			end = read.reference_start + args.r + 1 # +1 to move from inclusive to exclusive
			# print("(%s) %i --> %i --> %i" % ("+", start, read.reference_start , end))

		# Validate window and fetch sequence
		if (start <= 0 or end > genome.get_reference_length(ref_name)):
			# raise Exception("Sequence window falls at the edge of the chromosome: (%s: %i-%i)" % (ref_name, start, end))
			sys.stderr.write("Sequence window falls at the edge of the chromosome: (%s: %i-%i) skipping..." % (ref_name, start, end))
			continue

		# Fetch the sequence from the genome (skip N-containing)
		sequence = genome.fetch(ref_name, start, end).upper()
		if (sequence.find('N')>=0):
			continue

		# Take reverse complement if read maps to reverse strand
		if (read.is_reverse):
			sequence = reverse_complement(sequence)

		# Iterate through the sequence and tally dinucleotides by position
		for i in range(len(sequence) - 1):
			dinucleotide = sequence[i:i+2]
			position = i - args.l  # Position relative to the read start
			# print(position)
			df_counts.loc[dinucleotide, position] += 1

		# Print progress
		counter += 1
		if (counter % 100 == 0):
			print('%i reads tallied...' % counter)

	# Close files
	genome.close()
	bam.close()

	# Relabel tally counts (shift 0 -> +1, 1 -> +2, ...etc)
	new_column_names = [ "+" + str(val+1) if val >= 0 else val for val in df_counts.columns]
	df_counts.columns = new_column_names

	# Write tally counts
	df_counts.to_csv(args.output, sep="\t")
