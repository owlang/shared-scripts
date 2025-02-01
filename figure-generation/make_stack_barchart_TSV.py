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
	parser.add_argument('--entropy', action='store_true', help='add entropy line')

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

def calculate_entropy(df):

	# Turn counts into frequencies
	freq = df.div(df.sum())

	# Take log2 of frequencies
	log2f = -1 * np.log2(freq)

	# f * np.log2(f)
	flog2f = freq * log2f

	# Calculate the entropy for each position
	entropy = flog2f.sum()

	return(entropy)


if __name__ == "__main__":
	'''Plot stacked bar chart'''
	args = getParams()

	# Parse input data to a DataFrame
	df = pd.read_csv(args.input, sep='\t', index_col=0, header=0)
	print(df)

	# Plotting
	fig, ax1 = plt.subplots(figsize=(args.width, args.height))

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
		ax1.bar(df.columns, df.loc[category, :], color=palette[c], label=category, bottom=bottom)
		bottom += df.loc[category, :]  # Update the bottom for the next category

	# Add labels and title for the primary y-axis
	ax1.set_xlabel('X_Values')
	ax1.set_ylabel('Count (Primary Y-Axis)')
	if args.title is not None:
		ax1.set_title(args.title)
	ax1.set_ylim(bottom=0, top=max(df.sum()))

	# Store legend info
	lines, labels = ax1.get_legend_handles_labels()

	if (args.entropy):
		# Create a secondary y-axis for the line plot
		ax2 = ax1.twinx()

		# Calculate and plot entropy
		ax2.plot(df.columns, calculate_entropy(df).T, color='orchid', marker='o', label='Entropy', linewidth=2)

		# Add label for the secondary y-axis
		ax2.set_ylabel('Entropy', color='orchid')
		ax2.tick_params(axis='y', labelcolor='orchid')  # Set secondary y-axis tick color to purple
		ax2.set_ylim(bottom=0, top=2)

		# Add secondary legend info
		lines2, labels2 = ax2.get_legend_handles_labels()
		lines = lines + lines2
		labels = labels + labels2

	# Combine legends from both axes
	ax1.legend(lines, labels, title='Category', bbox_to_anchor=(1.1, 1), loc='upper left')

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
