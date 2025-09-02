import sys, argparse
import re
import pysam
import argparse

def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script will extract sequences from a BAM file and write them to a .fasta file but padded with Ns so that they are in the same frame.

Example: python pad_bam-sequences_woffset.py -i INPUT.bam -o OUTPUT.fasta''')
    parser.add_argument('-i','--input', metavar='input', required=True, help='a BAM file to filter')
    parser.add_argument('-o','--output', metavar='output', required=True, help='the FASTA file of padded read sequences')
    parser.add_argument('-c','--coord', metavar='chrname:start-stop', required=True, help='the coordinate range string to extract reads from')
    # parser.add_argument('--read1', action='store_true', help='only display from read 1')
    # parser.add_argument('--read2', action='store_true', help='only display from read 2')


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


def reverse_complement(seq):
    seq = seq.upper()
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return ''.join(complement.get(base, 'N') for base in reversed(seq))


if __name__ == "__main__":
    '''Write BAM file that meets the filter criteria.'''
    args = getParams()

    # Validate BAM file
    if(not validateBAM(args.input)):
        sys.exit(-1)

    # parse coordinate string
    pattern = re.compile("(chr[0-9]+):([0-9]+)-([0-9]+)")
    chr_name, start, stop = re.fullmatch(pattern, args.coord).group(1, 2, 3)
    start, stop = int(start), int(stop)

    print(f"Input:  {args.input}")
    print(f"Output: {args.output}")
    print(f"chrom:  {chr_name}")
    print(f"start:  {start}")
    print(f"stop:   {stop}")

    fa_lines = []

    # open input BAM file
    samfile = pysam.AlignmentFile(args.input, "rb")
    # Iterate across all reads
    for sr in samfile.fetch(chr_name, start, stop):

        # Initialize Ns as rectangle
        seq = ['N'] * (stop - start)

        qseq = sr.query_sequence
        # if sr.is_reverse:
        #     qseq = reverse_complement(qseq)
        # print(qseq)
            
        # Update seq array with query sequence
        offset = sr.reference_start - start
        for i in range(len(qseq)):
            seq[offset+i] = qseq[i]

        # append sequence and header
        fa_lines.append(f">{sr.query_name}")
        fa_lines.append(''.join(seq))

    # Close files
    samfile.close()

    # Write FASTA
    with open(args.output, 'w') as f:
        f.write('\n'.join(fa_lines))