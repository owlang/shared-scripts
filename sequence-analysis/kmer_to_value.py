import sys, getopt
import re
import argparse

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will create a CDT from a FASTA sequence.

Example: python kmer_to_value.py -i INPUT.fa -r REF.tab -o OUTPUT.cdt''')
	parser.add_argument('-i','--input', metavar='input_fn', required=True, help='a FASTA file of sequence to scan')
	parser.add_argument('-r','--reference', metavar='tab_fn', required=True, help='a two column of kmer to value (col1=<kmer>, col2=<value>)')
	parser.add_argument('--pad-back', action="store_true", help='pad k-1 zeros to CDT at back of matrix (right)')
	parser.add_argument('--pad-front', action="store_true", help='pad k-1 zeros to CDT at front of matrix (left)')
	parser.add_argument('--default-value', metavar='default', default="0", help='default value if k-mer not found')
	parser.add_argument('-o','--output', metavar='cdt_fn', required=True, help='a CDT file of the signal matrix')

	#parser.add_argument('-t','--title', metavar='figure_title', dest='title', required=True, help='')

	args = parser.parse_args()
	return(args)


def loadInput(tab_file, k=None):
	'''Load kmer to values into dictionary keyed on kmer column. Validate all kmers are same k length'''
	kmer2val = {}
	reader = open(tab_file,'r')
	# Update sequence with each variant
	for line in reader:
		tokens = line.strip().split("\t")
		kmer = tokens[0]
		if (k==None):
			k = len(kmer)
		if (k!=len(kmer)):
			raise RuntimeError("kmer length not consistent in reference file")
		kmer2val.update({kmer:float(tokens[1])})
	reader.close()
	return kmer2val

if __name__ == "__main__":
	'''Write CDT file with kmer-scanned values.'''
	args = getParams()

	# Load all BED file entries into memory
	kmer2val = loadInput(args.reference)
	K = len(list(kmer2val.keys())[0])

	id = ""
	seq = None
	lines = []
	reader = open(args.input,'r')
	for line in reader:
		new_line = line.strip().split("\t")[0]
		# process FASTA header
		if (new_line.find(">") == 0):
			if (seq != None):
				# scan seq to get values
				values = [str(kmer2val.get(seq[i:i+K], args.default_value)) for i in range(len(seq)-K)]
				# write values to CDT
				lines.append(id + "\t" + id + "\t" + "\t".join(values))
			id = new_line[1:]
			seq = ""
		# process FASTA sequence line
		else:
			seq += new_line
	reader.close()

	# Write CDT
	writer = open(args.output, 'w')
	writer.write("\n".join(lines))
	writer.close()
