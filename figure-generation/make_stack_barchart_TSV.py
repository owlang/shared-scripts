#!/usr/bin/env python
import argparse, sys
from os.path import isfile, join, splitext
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# from os import listdir
# from os.path import isfile, join, splitext
# import re, sys
# import random

# Python 3.6+
# relies on dict insertion order

# Check Matplotlib colors when building your config files: https://matplotlib.org/stable/gallery/color/named_colors.html

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-i','--input', metavar='tsv_file', required=True, default=None, help='tab-delimited file where each column label is the x-axis category and each row is a different group (color)')
	parser.add_argument('-o','--output', metavar='output_svg', required=False, default=None, help='name of SVG filepath to save figure to (if none provided, figure pops up in new window)')

	parser.add_argument('--palette', metavar='seaborn_palette_name', required=False, default=None, help='name of Seaborn palette to use')
	parser.add_argument('--title', metavar='string', required=False, default=None, help='title to add to the plot')

	parser.add_argument('--height', metavar='string', required=False, default=6, help='figure height')
	parser.add_argument('--width', metavar='string', required=False, default=10, help='figure width')

	args = parser.parse_args()
	return(args)

# Example Data (from ../sequence-analysis/updownstream_di-nt_tally.py):
# 	-10	-9	-8	-7	-6	-5	-4	-3	-2	-1	+1	+2	+3	+4	+5	+6	+7	+8	+9	+10
# AA	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	1.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	
# AT	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	
# AC	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	1.0	1.0	0.0	0.0	
# AG	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	0.0	0.0	1.0	0.0	1.0	
# TA	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	
# TT	0.0	1.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	
# TC	0.0	1.0	0.0	2.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	
# TG	0.0	2.0	1.0	0.0	0.0	0.0	1.0	1.0	1.0	1.0	0.0	1.0	0.0	1.0	1.0	0.0	0.0	0.0	1.0	
# CA	0.0	0.0	1.0	0.0	0.0	0.0	1.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	0.0	
# CT	2.0	0.0	0.0	0.0	0.0	2.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	1.0	0.0	
# CC	0.0	0.0	0.0	0.0	3.0	2.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	
# CG	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	
# GA	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	1.0	0.0	1.0	0.0	0.0	1.0	0.0	0.0	0.0	
# GT	2.0	0.0	2.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	2.0	0.0	0.0	1.0	0.0	0.0	0.0	
# GC	0.0	0.0	0.0	1.0	1.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	1.0	0.0	
# GG	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	0.0	1.0	0.0	0.0	1.0	0.0	0.0	0.0	1.0	


if __name__ == "__main__":
	'''Plot stacked bar chart'''
	args = getParams()

	# Parse input data to a DataFrame
	df = pd.read_csv(args.input, sep='\t', index_col=0, header=0)
	print(df)

	# Plotting
	plt.figure(figsize=(args.width, args.height))

	# Create palette
	palette = sns.color_palette()
	if (args.palette != None):
		palette = sns.color_palette(args.palette, as_cmap=True) (np.linspace(0, 1, len(df.index)))
	print(len(df.index))

	# Initialize the bottom array for stacking
	bottom = np.zeros(len(df.columns))

	# Plot each category as a stacked bar
	for i, category in enumerate(df.index):

		# Determine color index from palette
		c = i % len(palette)
		# print(c)

		# Plot bar from bottom and upate
		plt.bar(df.columns, df.loc[category, :], color=palette[c], label=category, bottom=bottom)
		bottom += df.loc[category, :]  # Update the bottom for the next category

	# Add labels and title
	plt.xlabel('X_Values')
	plt.ylabel('Count')
	if (args.title != None):
		plt.title(args.title)
	plt.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')

	# Show the plot
	plt.tight_layout()

	# Output...
	if(args.output==None):
		plt.show()
	else:
		try:
			plt.savefig(args.output, transparent=True)
			sys.stderr.write("Image written to %s\n" % args.output)
		except:
			sys.stderr.write("Please use SVG/PNG file extension to save output!\n")
			plt.show()
