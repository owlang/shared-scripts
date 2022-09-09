import sys
import argparse

arabic2roman_map = {'chr1':'chrI',
					'chr2':'chrII',
					'chr3':'chrIII',
					'chr4':'chrIV',
					'chr5':'chrV',
					'chr6':'chrVI',
					'chr7':'chrVII',
					'chr8':'chrVIII',
					'chr9':'chrIX',
					'chr10':'chrX',
					'chr11':'chrXI',
					'chr12':'chrXII',
					'chr13':'chrXIII',
					'chr14':'chrXIV',
					'chr15':'chrXV',
					'chr16':'chrXVI',
					'chrM':'chrmt'}
				
roman2arabic_map = {'chrI'  :'chr1',
					'chrII' :'chr2',
					'chrIII':'chr3',
					'chrIV' :'chr4',
					'chrV'  :'chr5',
					'chrVI' :'chr6',
					'chrVII':'chr7',
					'chrVIII':'chr8',
					'chrIX' :'chr9',
					'chrX'  :'chr10',
					'chrXI' :'chr11',
					'chrXII':'chr12',
					'chrXIII':'chr13',
					'chrXIV':'chr14',
					'chrXV' :'chr15',
					'chrXVI':'chr16',
					'chrmt' :'chrM'}


def get_params():
	'''Get parameters from the command line'''
	
	# Set-up parser
	parser = argparse.ArgumentParser(description='Take tokens from any tab-delimited file format and swap out the chromosome numbering system (Arabic to Roman Numerals and vice versa). New file is written to STDOUT')
	
	parser.add_argument('--a2r', dest='a2r', action='store_true', default=False, help='Numeral system direction is arabic input and roman output (default)')
	parser.add_argument('--r2a', dest='r2a', action='store_true', default=False, help='Numeral system direction is roman input and arabic output')
	parser.add_argument('filename', metavar='filename', help='The file where we want to swap chromosome names')
	parser.set_defaults(which='a2r')
	
	# Parse with parser
	args = parser.parse_args()
	
	
	# add constraints and default	
	if( args.a2r and args.r2a ):
		raise Exception( 'Cannot map from arabic to roman numeral system AND roman to arabic at the same time!\nPlease choose only one of the following flags to use [-a2r | -r2a]')
	elif( args.r2a ):
		args.which = 'r2a'
	
	return( args )
	

def replace_tokens_with_map(filename,map):
	'''Replace all tokens within the given file that match a key in the given map with the mapped value
		filename	String	path to file that we wish to parse
		map			dict	maps all tokens we wish to replace to the token values we want
	'''
	# loop through the file
	reader = open(filename,'r')
	for line in reader:
		# break each line into tokens
		tokens = line.strip().split('\t')
		# replace tokens as appropriate
		new_tokens = [ map.get(t,t) for t in tokens ]
		# write to STDOUT
		sys.stdout.write('\t'.join(new_tokens)+'\n')
	reader.close()


def main():
	
	# parser args
	args = get_params()
	
	# using arguments, set-up main method calls
	if( args.which=='a2r' ):
		replace_tokens_with_map(args.filename, arabic2roman_map)
	elif( args.which=='r2a' ):
		replace_tokens_with_map(args.filename, roman2arabic_map)
	else:
		raise Exception( 'This map option is not recognized: %s' % args.which )
		
main()
sys.stderr.write('DONE...\n')
