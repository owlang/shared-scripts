#!/usr/bin/env python
import sys, argparse
from os.path import splitext
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Python 3.6+
# relies on dict insertion order

# Check Matplotlib colors when building your config files: https://matplotlib.org/stable/gallery/color/named_colors.html

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-i','--input', metavar='two_col_file', dest='data_file', required=False, default=None, help='tab-delimited file made of two columns: first column y values to plot (must all be numeric values), second column is the grouping (which violin group along x-axis to contribute to)')
	parser.add_argument('-o','--output', metavar='output_svg', dest='output_svg', required=False, default=None, help='name of SVG filepath to save figure to (if none provided, figure pops up in new window)')

	# parser.add_argument('--log', action='store_true', help='Log transform the values')
	# parser.add_argument('--max', metavar='max_value', default=None, type=float, help='Cap the max value')

	args = parser.parse_args()
	return(args)


def parse_data(encode_results_file):
	'''Parse three columns of data (y=col1, category=col2)'''
	plot_data = {"y":[],"category":[]}
	reader = open(encode_results_file,'r')
	for line in reader:
		tokens = line.strip().split('\t')
		plot_data["y"].append(float(tokens[0]))
		plot_data["category"].append(tokens[1])
	reader.close()
	return(plot_data)

# Example Data:
# Value	Category
# 0.550716	category1
# 0.493109	category3
# 0.401034	category2
# 0.498233	category1
# 0.579172	category3
# 0.658480	category1
# 0.386018	category3
# 0.464670	category1
# 0.481569	category2
# 0.299219	category1
# 0.463803	category3
# 0.575400	category1
# 0.398278	category2
# 0.519507	category2
# 0.570949	category3
# 0.521441	category2
# 0.405716	category3
# 0.554221	category2
# 0.583154	category3
# 0.416495	category3
# 0.529519	category1
# 0.684446	category3

if __name__ == "__main__":
	'''Plot violin plot'''
	args = getParams()

	# Initialize plot base with twin axes
	fig, ax= plt.subplots()

	data = None
	if( args.data_file ==None ):
		data = fake_data()
	else:
		data = pd.read_csv(args.data_file, sep="\t", header=0)

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
	ax = sns.violinplot(x="Category", y="Value", data=data)

	# Label y-axis titles
	plt.ylabel("Value")

	# Label x-axis titles
	ax.tick_params(axis='x', rotation=20)
	plt.xlabel("Category")

	# Output...
	if(args.output_svg==None):
		plt.show()
	elif(splitext(args.output_svg)[-1]!=".svg"):
		sys.stderr.write("Please use SVG file extension to save output!\n")
		plt.show()
	else:
		plt.savefig(args.output_svg, transparent=True)
		sys.stderr.write("SVG written to %s\n" % args.output_svg)
