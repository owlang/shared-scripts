from os import listdir
from os.path import isfile, join, splitext
import sys
import re
import argparse
import random
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Python 3.6+
# relies on dict insertion order

# Check Matplotlib colors when building your config files: https://matplotlib.org/stable/gallery/color/named_colors.html

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='')

	parser.add_argument('-i','--input', metavar='two_col_file', dest='data_file', required=False, default=None, help='tab-delimited file made of two columns: first column y values to plot (must all be numeric values), second column is the grouping (which violin group along x-axis to contribute to)')
	parser.add_argument('-o','--output', metavar='output_svg', dest='output_svg', required=False, default=None, help='name of SVG filepath to save figure to (if none provided, figure pops up in new window)')

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


def fake_data(n=500):
	'''Generate fake data to test script'''
	mu1 = 1
	sigma1 = 0.5
	plot_data = {
		"y":[random.gauss(mu1,sigma1) for _ in range(n)],
		"category":random.choices(["category1","category2","category3"],k=n) }
	#[ sys.stdout.write("%f\t%s\n" % (plot_data["y"][i],plot_data["category"][i])) for i in range(n)]
	return(plot_data)

if __name__ == "__main__":
	'''Plot violin plot'''
	args = getParams()

	# Initialize plot base with twin axes
	fig, ax= plt.subplots()

	data = None
	if( args.data_file ==None ):
		data = fake_data()
	else:
		data = parse_data(args.data_file)

	# Scatter Plot or other type of plot here!!!!!
	# could swap out for 'swarmplot' and google seaborn library for others
	ax = sns.violinplot(x="category", y="y", data=data)

	# Label y-axis titles
	plt.ylabel("Y values (column 1)")

	# Label x-axis titles
	plt.xlabel("X values (column 2)")

	# Label Figure title
	ax.set_title("Chitvan's Violin Plot")

	# Output...
	if(args.output_svg==None):
		plt.show()
	elif(splitext(args.output_svg)[-1]!=".svg"):
		sys.stderr.write("Please use SVG file extension to save output!\n")
		plt.show()
	else:
		plt.savefig(args.output_svg)
		sys.stderr.write("SVG written to %s\n" % args.output_svg)
