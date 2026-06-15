#!/usr/bin/env python3
import sys, os
import argparse
import pandas as pd
import numpy as np

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will parse bedtools closest output to define a phase.
 - .cdt headers must be ['YORF', 'NAME', '0', '1', '2', ...]

Note: The 10-bp phasing mask is based on Olivia's windows.

Input:
	the input file should be a 13-column file formatted like the bedtools closest output where the two inputs (-a and -b) are BED6 formatted and the thirteenth column is the distance.
	Typical usage involves shifting 
Example:
	`bedtools closest -D a -wo -a FIRST.bed -b PHASED.bed`

Output:
|--dir_name
  |--left_phase-{p}.bed   # `FIRST.bed`  - left BED6 (col1-6) for each phase p in {1..10}
  |--right_phase-{p}.bed  # `PHASED.bed` - right BED6 (col7-12) for each phase p in {1..10}
  |--phasing_info.txt     # .tsv file of information on inputs, parameters, distances (col 13), and computed phases

Example: python phase_split_BED.py -s SENSE.cdt -a ANTI.cdt -o OUTPUT.tsv''')
	parser.add_argument('-i','--input', metavar='tsv_fn', required=True, help='a BED13 file of the bedtools closest output')
	parser.add_argument('-O','--output-dir', metavar='dir_name', required=True, help='a directory to save the output files to')

	parser.add_argument('--left', default='left_phase', help='specify a basename for the left (-a) output bedfiles (default=left_phase)')
	parser.add_argument('--right', default='right_phase', help='specify a basename for the right (-b) output bedfiles (default=right_phase)')

	# TODO: add support for a BED7 input

	# parser.add_argument('--id', choices=['left','right'], required=True, help='specify if id column used in --phasing-info comes from left or right BED6')
	parser.add_argument('--mod', type=float, default=10, help='specify a different phasing length, probably never really used (default=10)')

	# parser.add_argument('--batch', metavar='batch_size', type=int, default=10000, help='for large BED/CDT files, set a number of rows to process at a time')
	
	# parser.add_argument('--batch', metavar='batch_size', type=int, default=10000, help='for large BED/CDT files, set a number of rows to process at a time')
	parser.add_argument('--qc-plot', metavar='img_fn', help='write summary stats to figure file (.png or .svg)')
	# parser.add_argument('--info', metavar='tsv_fn', help='a TSV file with stats and metadata associated with phasing')

	args = parser.parse_args()
	return(args)


def load_bedtsv(bedtsv_fn):
	bedtsv_dtypes = {
		'a_chr': str,
		'a_start': np.int32,
		'a_stop': np.int32,
		'a_id': str,
		'a_score': str,
		'a_strand': str,
		'b_chr': str,
		'b_start': np.int32,
		'b_stop': np.int32,
		'b_id': str,
		'b_score': str,
		'b_strand': str,
		'Dist': np.int32
	}
	assert sys.version_info[0] >= 3, "Python must be v3+ because I am relying on dict preserving order of added key-values"

	bedtsv_df = pd.read_csv(bedtsv_fn, sep='\t', index_col=None, names=bedtsv_dtypes.keys(), dtype=bedtsv_dtypes)
	assert bedtsv_df.shape[1]==13, "All records must be 13 columns (BED6 + BED6 + dist)"
	return(bedtsv_df)

def main():

	args = getParams()

	# Fast-fail on dependencies
	if args.qc_plot:
		import matplotlib.pyplot as plt
		import seaborn as sns

	# Load data
	bedtsv_df = load_bedtsv(args.input)

	# Compute phase
	bedtsv_df['phase'] = bedtsv_df['Dist'].mod(10)
	
	# Summarize phase counts
	phase_counts = pd.DataFrame(bedtsv_df['phase'].value_counts())
	phase_counts = phase_counts.sort_index()
	print(phase_counts)

	# Make directory if one doesn't already exist
	if not os.path.exists(args.output_dir):
		os.makedirs(args.output_dir)

	# Write each phase group to new .bed file
	for phase in phase_counts.index:

		slice_df = bedtsv_df.loc[bedtsv_df['phase']==phase,:]
		slice_df = slice_df.drop(columns=['phase', 'Dist'])

		# Write left and right BED6 files from slice
		slice_df[['a_chr', 'a_start', 'a_stop', 'a_id', 'a_score', 'a_strand']].to_csv(
			os.path.join(args.output_dir, f"{args.left}-{phase}.bed"),
			sep="\t", header=None, index=False
		)
		slice_df[['b_chr', 'b_start', 'b_stop', 'b_id', 'b_score', 'b_strand']].to_csv(
			os.path.join(args.output_dir, f"{args.right}-{phase}.bed"),
			sep="\t", header=None, index=False
		)

	# Make QC plot for phasing details
	if args.qc_plot:

		# phase_counts['percentage'] = 100 * phase_counts['count'] / phase_counts['count'].sum()

		# Initialize plot base with twin axes
		fig, ax = plt.subplots(1,2)

		sns.barplot(phase_counts, ax=ax[0], y='phase', x='count', orient='y', color='lightgray')
		ax[0].bar_label(ax[0].containers[0], labels=phase_counts['count'], padding=-30)
		# ax.bar_label(ax.containers[0], labels=phase_counts['percentage'])
		# ax[0].tick_params(axis='x', labelrotation=35)

		# dist_counts = pd.DataFrame(bedtsv_df['Dist'].value_counts())
		# # dist_counts = dist_counts.sort_index()
		# print(dist_counts)
		# dist_counts['count'] = dist_counts['count'].astype(np.int32)
		# dist_counts.index = dist_counts.index.astype(np.int32)
		sns.histplot(bedtsv_df, ax=ax[1], y='Dist', color='lightgray', binwidth=20, binrange=(-501,500))
		# ax[1].tick_params(axis='x', labelrotation=35)
		ax[1].set(xscale="log")

		fig.savefig(args.qc_plot) #, transparent=True)

if __name__ == '__main__':
	main()
