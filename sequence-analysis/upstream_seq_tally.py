import pysam
import sys, argparse, csv, os
import math
import numpy
import pysam

comp = {'A':'T', 'T':'A',
		'C':'G', 'G':'C',
		'N':'N'}

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description = """
============
Get tally of upstream sequences from reads in a BAM file.
============
""", formatter_class = argparse.RawTextHelpFormatter)

	parser.add_argument('-i','--input', metavar='bam_fn', required=True, help='the BAM file of reads to analyze')
	parser.add_argument('-g','--genome', metavar='fasta_fn', required=True, help='the genomic sequence FASTA file')
	parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited k-mer list with read tally counts')
	parser.add_argument('-p', action='store_true', help='only check properly paired reads')

	parser.add_argument('-k','--kmer', default=10, type=int, help='the number of bp upstream of read start to check')

	args = parser.parse_args()
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

# Main program which takes in input parameters
if __name__ == '__main__':
	args = getParams()

	# Validate BAM file
	if(not validateBAM(args.input)):
		sys.exit(-1)

	print("BAM file: ", args.input)
	print("Genome fasta: ", args.genome)
	print("Output file: ", args.output)

	# Initialize output data variable
	TALLY = {}
	# open BAM file
	samfile = pysam.AlignmentFile(args.input, "rb")
	# open Genome fasta file
	GENOME = pysam.FastaFile(args.genome)

	# Loop the samfile iterator
	for read in samfile.fetch():
		# Skip unmapped
		if (read.is_proper_pair and args.p):
			continue
		# Check chr name
		if read.reference_name in GENOME.references:
			START = -1
			STOP = -1

			# Retrieve sequence before/after read according to strand mapping
			if(read.is_reverse):
				START = read.reference_end
				STOP = read.reference_end + args.kmer
			else:
				START = read.reference_start - args.kmer
				STOP = read.reference_start

			# Validate window and fetch sequence
			if (START <= 0 or STOP > GENOME.get_reference_length(read.reference_name)):
				continue
			KMER = GENOME.fetch(read.reference_name, START, STOP).upper()

			# Take reverse complement if read maps to reverse strand
			if (read.is_reverse):
				KMER = reverse_complement(KMER)

			TALLY.setdefault(KMER, [0,0])
			# Increment read-specific tally
			if(read.is_read1):
				TALLY[KMER][0] += 1
			else:
				TALLY[KMER][1] += 1
	# Close files
	GENOME.close()
	samfile.close()

	# Write tally counts
	writer = open(args.output, 'w')
	for key in sorted(TALLY.keys()):
		value = TALLY[key]
		writer.write("\t".join([ key, str(value[0]), str(value[1]), str(value[0]+value[1]) ]) + "\n")
	writer.close()
