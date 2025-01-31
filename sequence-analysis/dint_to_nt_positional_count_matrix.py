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
Merge dinucleotide counts (output from updownsteram_di-nt_tally.py) to single-nucleotide counts
============
    """, formatter_class = argparse.RawTextHelpFormatter)

    parser.add_argument('-i','--input', metavar='bam_fn', required=True, help='the dinucleotide positional count matrix to reduce')
    parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='the single nt positional count matrix')

    args = parser.parse_args()

    return(args)

def initialize_di_nt_df(left, right):
    '''Initialize df for tracking dinucleotide tallies by position relative to cut site'''

    # Initialize row index labels of all 16 dinucleotides

    # Initialize column labels (range without 0)
    # column_names = [i for i in range((-1*left), right)]
    column_names = [i for i in range((-1*right), right)]

    # Initialize matrix of zeros with labels (NaN in last column)
    df = pd.DataFrame(np.nan, columns=column_names, index=row_labels)
    df.iloc[:,:-1] = 0

    # print(df)
    return(df)


# Main program which takes in input parameters
if __name__ == '__main__':

    args = getParams()

    # Validate BAM file
    df = pd.read_csv(args.input, sep='\t', index_col=0, header=0)

    # Drop last column (updownsteram_di-nt_tally.py fills last col with NaNs)
    df = df.iloc[:,:-1]

    # Create a new column in the DataFrame to store the first character of the index
    df['Single_NT'] = df.index.str[0]

    # Group by the first character and sum the rows
    result = df.groupby('Single_NT').sum()

    # Drop the temporary 'First_Char' column
    result = result.drop(columns=['Single_NT'], errors='ignore')

    # Write the results
    result.to_csv(args.output, sep="\t")
