import sys, getopt
import re
import argparse

ALL_NT = ["A","T","C","G"]

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will write all [ATCG]{k} kmer possibilities as a FASTA-formatted file.

Example: python all_kmers_FASTA.py -k 4 -o OUTPUT''')
	parser.add_argument('-k','--kmer-size', metavar='size', type=int, required=True, help='the length of the sequence')
	parser.add_argument('-o','--output', metavar='kmer-fasta', required=True, help='file to save FASTA-formatted k-mer to')

	args = parser.parse_args()
	return(args)


def add_nucleotide(k):
	'''Recursively add ATCG'''
	print("Kmer = %i" % k)
	if(k==0):
		return([""])
	kminus_list = add_nucleotide(k-1)
	klist = []
	for kminus_kmer in kminus_list:
		for NT in ALL_NT:
			klist.append(NT+kminus_kmer)
	return(klist)

if __name__ == "__main__":
	'''Write BED file in new order.'''
	args = getParams()

	writer = open(args.output, 'w')
	for kmer in add_nucleotide(args.kmer_size):
		writer.write(">%s\n%s\n" % (kmer, kmer))
	writer.close()
