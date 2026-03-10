#!/usr/bin/env python
import sys, argparse
from os.path import splitext
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter

# Use text, not shapes of text in SVG
plt.rcParams['svg.fonttype'] = 'none'

# Python 3.6+
# relies on dict insertion order

# Check Matplotlib colors when building your config files: https://matplotlib.org/stable/gallery/color/named_colors.html

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
python heatmap_CDT.py -i INPUT.cdt -o OUTPUT.png
''')

	parser.add_argument('-i','--input', metavar='cdt_fn', dest='data_file', required=False, default=None, help='CDT-formatted matrix for plotting heatmap (sub for ScriptManager heatmap)')
	parser.add_argument('-o','--output', metavar='output_svg', dest='output_svg', required=False, default=None, help='name of SVG filepath to save figure to (if none provided, figure pops up in new window)')

	parser.add_argument('--smooth', default=None, type=int, help='Apply a gaussian smoothing filter by specifying sigma integer value (default no smoothing)')
	parser.add_argument('--height', default=6, type=int, help='Height of heatmap image')
	parser.add_argument('--width', default=4, type=int, help='Width of heatmap image')
	parser.add_argument('--cmap', default='jet', help='Colormap choice (see matplotlib), default=\'jet\'')
	# parser.add_argument('--max', metavar='max_value', default=None, type=float, help='Cap the max value')

	args = parser.parse_args()
	return(args)

if __name__ == "__main__":
	'''Plot violin plot'''
	args = getParams()

	# Load data
	df = pd.read_csv(args.data_file, sep="\t", header=0, index_col=[0,1])
	print(df)

	# Initialize plot base with twin axes
	fig, ax= plt.subplots()

	# Specify dimensions
	plt.figure(figsize=(args.width, args.height))

	# # Log-transform the data
	# if (args.log):
	# 	data['Value'] = np.log(data['Value'])

	# Cap the max value
	# if (args.max != None):
		# data = data.clip(upper=pd.Series({'Value': args.max}), axis=1)

	# Smooth matrix with gaussian filter
	if (args.smooth != None):
		df = gaussian_filter(df, sigma=args.smooth)

	# Scatter Plot or other type of plot here!!!!!
	# could swap out for 'swarmplot' and google seaborn library for others
	ax = sns.heatmap(df, xticklabels=False, yticklabels=False, cmap='jet')

	# Label y-axis titles
	plt.ylabel("Gene")

	# Label x-axis titles
	plt.xlabel("Position")

	# Output...
	if(args.output_svg==None):
		plt.show()
	elif(splitext(args.output_svg)[-1]==".png"):
		plt.savefig(args.output_svg, transparent=True)
		sys.stderr.write("PNG written to %s\n" % args.output_svg)
	elif(splitext(args.output_svg)[-1]==".svg"):
		plt.savefig(args.output_svg, transparent=True)
		sys.stderr.write("SVG written to %s\n" % args.output_svg)
	else:
		sys.stderr.write("Please use SVG file extension to save output!\n")
		plt.show()