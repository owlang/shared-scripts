import argparse
import random

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description = '''
============
Generate random sequence "genome".
============
''', formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-l', metavar='len_of_sequences', default=200, type=int, help='the length of each sequence (bp)')
    parser.add_argument('-n', metavar='num_sequences', default=10, type=int, help='the number of sequences (named chr1 to chrN)')
    parser.add_argument('-o','--output', metavar='fa_fn', required=True, help='the output FASTA file of random sequences')

    args = parser.parse_args()
    return(args)

# Main program which takes in input parameters
if __name__ == '__main__':
    args = getParams()

    # Create file writer
    writer = open(args.output, 'w')

    for i in range(args.n):
        # Write seq header
        writer.write('>chr%i\n' % (i+1))
        # Sample from A, T, C, and G chars
        writer.write('%s\n' % ''.join(random.choices(['A','T','C','G'], k=args.l)))
    # Close writer
    writer.close()