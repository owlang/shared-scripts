#!/bin/python
import os, sys, argparse
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
sns.set()

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='Build lineplot of sra growth stats.')

	parser.add_argument('-i','--input', metavar='input_fn', required=True, help='the downloaded sra_stat.csv')
	parser.add_argument('-o','--output', metavar='png_fn', required=True, help='the output figure image')

	args = parser.parse_args()
	return(args)

'''
date,bases,open_access_bases,bytes,open_access_bytes
"06/05/2007",20304190150,20304190150,50496285115,50496285115
"04/04/2008",39591836573,39591836573,98175829054,98175829054
"04/05/2008",41196134195,41196134195,102158063571,102158063571
"04/09/2008",41645296177,41645296177,103295608811,103295608811
'''

# Main program which takes in input parameters
if __name__ == '__main__':
	'''Load data into a pandas dataframe and plot the line'''

	# Parse input/outputs
	args = getParams()

	# Populate dataframe with tab file data
	filedata = pd.read_table(args.input, sep=',')

	# Convert the formatted date column to datetime
	filedata['formatted_date'] = pd.to_datetime(filedata['date'], format="%m/%d/%Y")

	# Sort the DataFrame by the formatted date column
	filedata = filedata.sort_values('formatted_date')

	# Create the line plot using seaborn
	snsplot = sns.lineplot(data=filedata, x='formatted_date', y='open_access_bases')#, ci=None, bottom=0)

	# Set y-axis scale to logarithmic
	plt.yscale('log')

	# Rotate the x-axis labels for better readability (optional)
	plt.xticks(rotation=45)

	# Save figure by output filename
	fig = snsplot.get_figure()
	fig.savefig(args.output)
