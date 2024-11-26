#!/usr/bin/env python
import sys
from os import listdir
from os.path import isfile, join, splitext
import sys
import re
import argparse
import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Python 3.6+
# relies on dict insertion order

# Check Matplotlib colors when building your config files: https://matplotlib.org/stable/gallery/color/named_colors.html

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-i','--input', metavar='two_col_file', dest='data_file', required=False, default=None, help='tab-delimited file with the first row header made of two columns: first column y values to plot (must all be numeric values), second column is the grouping (which violin group along x-axis to contribute to)')
	parser.add_argument('-o','--output', metavar='output_svg', dest='output_svg', required=False, default=None, help='name of SVG filepath to save figure to (if none provided, figure pops up in new window)')

	parser.add_argument('--log', action='store_true', help='Log transform the values')
	# parser.add_argument('--max', metavar='max_value', default=None, type=float, help='Cap the max value')

	args = parser.parse_args()
	return(args)


# Example Data:
# ID	ValueX	ValueY
# YJL052C-A	1.43809	2.22466
# YKL178C	0.981945	0
# YLR091W	0.805799	1.32733
# YLR346C	5.0317	2.5946


if __name__ == "__main__":
	'''Plot violin plot'''
	args = getParams()

	# Initialize plot base with twin axes
	fig, ax= plt.subplots()

	data = None
	if( args.data_file ==None ):
		data = fake_data()
	else:
		data = pd.read_csv(args.data_file, sep="\t", header=0, names=["ValueX", "ValueY"])

	# # Log-transform the data
	# if (args.log):
	# 	data['Value'] = np.log(data['Value'])

	# Cap the max value
	# if (args.max != None):
		# data = data.clip(upper=pd.Series({'Value': args.max}), axis=1)

	#plot figure with specificied size
	# plt.figure(figsize=(8,4))

	# Scatter Plot or other type of plot here!!!!!
	# could swap out for 'swarmplot' and google seaborn library for others
	ax = sns.scatterplot(x="ValueX", y="ValueY", data=data)

	if (args.log):
		ax.set(xscale="log", yscale="log")

	# Output...
	if(args.output_svg==None):
		plt.show()
	elif(splitext(args.output_svg)[-1]!=".svg"):
		sys.stderr.write("Please use SVG file extension to save output!\n")
		plt.show()
	else:
		plt.savefig(args.output_svg, transparent=True)
		sys.stderr.write("SVG written to %s\n" % args.output_svg)
