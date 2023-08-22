
import pysam
import sys, argparse, csv, os
import math
import numpy
import pysam

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description = """
============
Get position weight matrix from tally of upstream sequences.
============
""", formatter_class = argparse.RawTextHelpFormatter)

	parser.add_argument('-i','--input', metavar='bam_fn', required=True, help='the tab-delimited k-mer list with read tally counts')
	parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the output tab-delimited k-mer list with read tally counts')

	parser.add_argument('-c','--column', default=3, type=int, help='the column index to use for the count (1=read1, 2=read2, 3=allreads)')

	args = parser.parse_args()
	return(args)

# Main program which takes in input parameters
if __name__ == '__main__':
	args = getParams()

	print("BAM file: ", args.input)
	print("Output file: ", args.output)

	PWM = None

	# Read the Kmers into the PWM and tally
	reader = open(args.input,'r')
	for line in reader:
		tokens = line.strip().split('\t')
		if(PWM == None):
			mlen = len(tokens[0])
			PWM = {'A':[0]*mlen, 'T':[0]*mlen, 'C':[0]*mlen, 'G':[0]*mlen, 'N':[0]*mlen}
		for i,char in enumerate(tokens[0]):
			PWM[char][i] += float(tokens[args.column])
	reader.close()

	# Write the PWM
	writer = open(args.output,'w')
	writer.write("-\t" + "\t".join([str(i) for i in range(len(PWM['A']))]) + "\n")
	writer.write("A\t" + "\t".join([str(i) for i in PWM['A']]) + "\n")
	writer.write("T\t" + "\t".join([str(i) for i in PWM['T']]) + "\n")
	writer.write("C\t" + "\t".join([str(i) for i in PWM['C']]) + "\n")
	writer.write("G\t" + "\t".join([str(i) for i in PWM['G']]) + "\n")
	writer.write("N\t" + "\t".join([str(i) for i in PWM['N']]) + "\n")
	writer.close()
