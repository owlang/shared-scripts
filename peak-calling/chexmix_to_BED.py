import sys, argparse

# ### ChExMix output
# #Condition      Name    Index   TotalSigCount   SigCtrlScaling  SignalFraction
# #Condition      chipexo 0       1.7786067E7     1.000   0.411
# #Replicate      ParentCond      Name    Index   SigCount        CtrlCount       CtrlScaling     SignalFraction
# #Replicate      chipexo chipexo:rep1    0       1.7786067E7     0       1       0.411
# #
# #Point  chipexo_Sig     chipexo_Ctrl    chipexo_log2Fold        chipexo_log2Q   SubtypePoint    Tau     SubtypeName     SubtypeSequence SubtypeMotifScore
# chrM:14182      4223.1  1.7     11.313  -Infinity       chrM:14182:-    1.00    Subtype5        TTGTTGGTGTATATATTGTAA   0.00
# chrM:12407      3178.4  1.8     10.750  -Infinity       chrM:12393:+    0.56    Subtype5        TTCCCCCCATCCTTACCACCC   12.10
# chrM:15538      3130.4  1.4     11.078  -Infinity       chrM:15536:+    0.39    Subtype5        CCCCTTAAACACCCCTCCCCA   9.05
# chrM:11866      2964.5  1.3     11.155  -Infinity       chrM:11866:+    1.00    Subtype5        ACCTCGCCTTACCCCCCACTA   9.36
# chrM:6432       2960.4  2.9     9.989   -Infinity       chrM:6435:+     0.46    Subtype5        TGCCATAACCCAATACCAAAC   3.30
# chrM:9167       2532.7  1.5     10.721  -Infinity       chrM:9167:+     1.00    Subtype5        GCCTACGTTTTCACACTTCTA   4.27

FIELDNAME_ORDER = [
    'Point', 'chipexo_Sig', 'chipexo_Ctrl', 'chipexo_log2Fold', 'chipexo_log2Q',
    'SubtypePoint', 'Tau', 'SubtypeName', 'SubtypeSequence', 'SubtypeMotifScore'
    ]


def getParams():
    '''Parse parameters from the command line'''
    parser = argparse.ArgumentParser(description='''
This script reformats the *_chipexo.events output from ChExMix to a proper stranded BED file.

`--subtypes 0`
    keep only rows where events['SubtypeName'] == 'Subtype0'
`--score SubtypeMotifScore`
    copy value from events['SubtypeMotifScore'] into the .bed output score column
                                     
Example: python chexmix_to_BED.py -i COORD.bed -o NEW.bed''')
    parser.add_argument('-i','--input', metavar='bedfile', required=True, help='a BED file to reset id for')
    parser.add_argument('-o','--output', metavar='outfile', required=True, help='a BED file of the deduplicated BED coord IDs (unordered)')
    parser.add_argument('--subtype', default=None, help='only parse out a specific subtype, use integer (default=all subtypes)')
    parser.add_argument('--score', default='chipexo_Sig', choices=[
        'chipexo_Sig', 'chipexo_Ctrl', 'chipexo_log2Fold', 'chipexo_log2Q',
        'Tau', 'SubtypeName', 'SubtypeSequence', 'SubtypeMotifScore'
        ], help='select field to use for the score column (default="chipexo_Sig")')

    args = parser.parse_args()
    return(args)

if __name__ == "__main__":
    '''Write BED file in new order.'''

    # Parse params
    args = getParams()

    # Open file handles
    reader = open(args.input, 'r')
    writer = open(args.output, 'w')
    for line in reader:
        # Skip comments
        if line.startswith('#'):
            continue
        tokens = line.strip().split('\t')

        # Confirm 10 columns
        assert len(tokens) >= 10, f"Not enough columns in entry: {line}"

        # if subtype filter specified and subtype filter does not match
        subtype_idx = FIELDNAME_ORDER.index('SubtypeName') # gets subtype 
        if args.subtype and f"Subtype{args.subtype}" != tokens[subtype_idx]:
            # Then skip subtypes that don't match
            continue

        chrom_str = tokens[FIELDNAME_ORDER.index('SubtypePoint')]
        chrom = chrom_str.split(":")[0]
        start = chrom_str.split(":")[1]
        strand = chrom_str.split(":")[2]

        # Adjust strand
        if strand != "-":
            start = str(int(start) - 2)

        # Set end of interval
        stop = str(int(start) + 1)

        score = tokens[FIELDNAME_ORDER.index(args.score)]

        # Reformat id token
        id = '_'.join(chrom_str.split(":"))

        # Write tokens
        writer.write('\t'.join([chrom, start, stop, id, score, strand]) + "\n")

    # Close file handles
    writer.close()
    reader.close()
