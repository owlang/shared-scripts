#!/usr/bin/env python3
import sys
import argparse
import pandas as pd
# import numpy as np
from decimal import Decimal, ROUND_HALF_UP

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will phase nucleosomes from a 300bp window. Assumes matching sort for both CDT inputs.
 - .cdt headers must be ['YORF', 'NAME', '0', '1', '2', ...]

Note: The 10-bp phasing mask is based on Olivia's windows.

Example: python phase_refpt-general-window.py -s SENSE.cdt -a ANTI.cdt -o OUTPUT.tsv''')
	parser.add_argument('-s','--sense', metavar='cdt_fn', required=True, help='a CDT file of the pileup for the -i .bed file')
	parser.add_argument('-a','--anti', metavar='cdt_fn', required=True, help='a CDT file of the pileup for the -i .bed file')
	parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='a TSV file with the id and phasing shift distance along with all the scoring intermediate values for determining phase')

	# options for customizing phasing strategy params
	parser.add_argument('--zero', default=None, type=int, help='Hardcode the 0-shift phasing position (based on .cdt header label, not matrix index)')
	parser.add_argument('--period', default="10.0", type=str, help='Set a dynamic period size. Can be non-integers so try out 10.2 or 10.5. Precision limited to 0.001 so anything higher than that will be rounded before running the script. (default=10.0)')
	parser.add_argument('--shift-range', nargs=2, default=(-4,6), metavar=('shift_start', 'shift_end_exclusive'), type=int, help='Shift offsets to test with respect to the zero position as a half-open interval. (default = -4 to 6)')
	parser.add_argument('--sense-period-range', nargs=2, default=(-6,2), metavar=('nperiod_start', 'nperiod_end'), type=int, help='Set a period range to sample relative to shift center for sense (default = -6 to +2). Values are inclusive.')
	parser.add_argument('--anti-period-range',  nargs=2, default=(-2,6), metavar=('nperiod_start', 'nperiod_end'),type=int, help='Set a period range to sample relative to shift center for anti  (default = +2 to -6). Values are inclusive.')

	# TODO: add alternative scoring strategies
	# parser.add_argument('--score', metavar='type', default='norm_total', choices=['norm_total'] help='select a scoring strategy for selecting max_score phase')

	# TODO: switch to pandas blocks for larger .bed files
	# parser.add_argument('--batch', metavar='batch_size', type=int, default=10000, help='for large BED/CDT files, set a number of rows to process at a time')

	# options for reporting, do not affect output
	parser.add_argument('--print-schematic', action='store_true', help='print the ACII art diagramming index selection (doesn\'t change output)')
	parser.add_argument('--qc-plot', metavar='img_fn', help='write summary stats to figure file (.png or .svg)')

	args = parser.parse_args()

	# Parse args.period into exact decimal
	# (this was added b/c floats were creating rounding errors that affected period indexing later...)
	args.period = Decimal(args.period)

	assert args.period > 0, "Invalid period length: period ({args.period}) must be greater than 1"
	assert args.shift_range[0] < args.shift_range[1], "Invalid shift range: first value ({args.shift_range[0]}) must be less than the second value ({args.shift_range[1]})"
	assert args.sense_period_range[0] < args.sense_period_range[1], "Invalid sense period range: first value ({args.sense_period_range[0]}) must be less than the second value ({args.sense_period_range[1]})"
	assert args.anti_period_range[0] < args.anti_period_range[1], "Invalid anti period range: first value ({args.anti_period_range[0]}) must be less than the second value ({args.anti_period_range[1]})"

	return(args)

def get_general_schematic():
	'''Return ASCII art for diagramming window index selection'''
	return("""
####################################################################################
#            ASCII Art for diagraming dyad window index selection below            #
####################################################################################

--CDT index (-header, 0-index)
--0                                                                                                   1                                                                                                   2                                                                                                   3
--0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         
--012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
dyad-160                                                               |---------|=========|---------|=========|---------|=========|---------|=========0---------|=========|---------|=========|---------|=========|---------|=========|
                                                                                 012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
relative-dist                                                          8         7         6         5         4         3         2         1         0         1         2         3         4         5         6         7         8
                                                                       0987654321098765432109876543210987654321098765432109876543210987654321012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
sense-mask                                                                                  |---------|---------|---------|---------|---------|---------|---------|---------|                                                                     -59 to 22 (half-open)
anti-mask                                                                                                                         |---------|---------|---------|---------|---------|---------|---------|---------|                               -21 to 59 (half-open)

####################################################################################

""")


def get_relative_schematic(zero, ncol=300, period=10, shift_range=(-4,5), sense_period_range=(-6,2), anti_period_range=(-2,6)):
	'''Return ASCII art for diagramming window index selection'''
	ascii_art = """
####################################################################################
#            ASCII Art for diagraming dyad window index selection below            #
####################################################################################

CDT index (-header, 0-index)
"""

	sense_mask = build_mask(sense_period_range, period, anti=False)
	anti_mask  = build_mask(anti_period_range, period,  anti=True)

	pad = 20

	# Add parameters
	ascii_art += f"{'ncol':<{20}} = {ncol}\n"
	ascii_art += f"{'zero':<{20}} = {zero}\n"
	ascii_art += f"{'period':<{20}} = {period}\n"
	ascii_art += f"{'shift_range':<{20}} = ({shift_range[0]},{shift_range[1]})\n"
	ascii_art += f"{'sense_period_range':<{20}} = ({sense_period_range[0]},{sense_period_range[1]})\n"
	ascii_art += f"{'anti_period_range':<{20}} = ({anti_period_range[0]},{anti_period_range[1]})\n"
	ascii_art += "--------\n"

	# store rows of ASCII formatting without row label and .cdt YORF/NAME padding (starting at 0 of index)
	header2line = {}

	# add .cdt index header
	header2line['cdt idx (hundreds)'] = ''.join([' '] * 99).join([str(i % 10) for i in range(int(ncol // 100)+1)])
	header2line['cdt idx (tens)']     = ''.join([' '] * 9 ).join([str(i % 10) for i in range(int(ncol // 10)+1)])
	header2line['cdt idx (ones)']     = ''.join(                 [str(i % 10) for i in range(int(ncol))])

	# # add dyad zero label
	# # TODO: add basic dyad schematic around midpoint
	# # TODO: generalize to period
	# dyad_char_list = ['|' if i % 10]
	# char_list = [' '] * ncol
	# char_list[dyad_mid_idx] = '0'
	# dyad_mid_str = ''.join(char_list)

	print(zero)

	# add dyad zero label
	char_list = [' '] * ncol
	char_list[zero] = '0'
	header2line['zero'] = ''.join(char_list)

	# add sense label
	sense_mask_0 = [i + zero for i in sense_mask]
	char_list = [' '] * (min(sense_mask_0))
	char_list += ['-' for _ in range(max(sense_mask_0)-min(sense_mask_0)+1)]
	for idx in sense_mask_0:
		char_list[idx] = '|'
	header2line['sense_mask_0'] = ''.join(char_list)

	# add anti label
	anti_mask_0 = [i + zero for i in anti_mask]
	char_list = [' '] * (min(anti_mask_0))
	char_list += ['-' for _ in range(max(anti_mask_0)-min(anti_mask_0)+1)]
	for idx in anti_mask_0:
		char_list[idx] = '|'
	header2line['anti_mask_0'] = ''.join(char_list)

	# add shift label
	char_list = [' '] * (zero+shift_range[0])
	char_list += [str(i)[-1] for i in range(shift_range[0], shift_range[1])]
	header2line['shift_range'] = ''.join(char_list)

	# add relative idx
	char_list = [str(i-zero)[-1] for i in range(ncol)]
	for idx in range(min(min(sense_mask_0), min(anti_mask_0))):
		char_list[idx] = ' '
	for idx in range(max(max(sense_mask_0), max(anti_mask_0))+1, len(char_list)):
		char_list[idx] = ' '
	header2line['relative_dist'] = ''.join(char_list)

	row_order = ["cdt idx (hundreds)", "cdt idx (tens)", "cdt idx (ones)", "zero", "shift_range", "relative_dist", "sense_mask_0", "anti_mask_0"]
	for key in row_order:
		value = header2line[key]
		ascii_art += f"{key:<{pad}}|--{value}\n"

	ascii_art += "\n####################################################################################\n"

	return(ascii_art)

# def load_bed(bed_fn):
# 	bed_dtypes = {
# 		'chr': str,
# 		'start': np.int32,
# 		'stop': np.int32,
# 		'id': str,
# 		'score': np.float64,
# 		'strand': str
# 	}
# 	bed_df = pd.read_csv(bed_fn, sep='\t', index_col=None, names=['chr', 'start', 'stop', 'id', 'score', 'strand'], dtypes=bed_dtypes)
# 	assert all([ row['stop'] - row['start'] == 300 for row in bed_df.iterrows()]), "All .bed records must be 300bp in length"
# 	return(bed_df)

def load_cdt(cdt_fn):
	cdt_df = pd.read_csv(cdt_fn, sep='\t', index_col=None, header=0)
	assert cdt_df.columns[0] == "YORF", "CDT must have first column named \"YORF\""
	assert cdt_df.columns[1] == "NAME", "CDT must have second column named \"NAME\""
	# assert cdt_df.shape[1] == 302, "CDT must have 2 header columns + 300 value columns"
	cdt_df.set_index(['YORF'], inplace=True)
	cdt_df = cdt_df.drop(columns=['NAME'])
	# Cast all data values to numeric types
	cdt_df.columns = [int(i) for i in cdt_df.columns]
	# cdt_df = cdt_df.convert_dtypes()
	cdt_df[cdt_df.columns] = cdt_df[cdt_df.columns].astype('float')
	return(cdt_df)

def build_mask(period_range, period, anti=False):
	'''Build mask of relative slices to tally (cut sites).

	Toy:
	( 6) dyad midpoint      |  ------0------
	     genomic coordinate |  012345678901234567891
	( 9) phase mark         |           .
	(10) sense cut-sites    |            |--->
	( 8) anti cut-sites     |      <---|
	
	"phase mark" == "shift_offset"
	'''
	left_period, right_period = period_range
	period_range = [period*p for p in range(left_period, right_period + 1, 1)]

	if anti:
		return([int((p-1).to_integral_value(rounding=ROUND_HALF_UP)) for p in period_range])  # -1 offset, 2 periods left, 6 periods right
	return([int((p+1).to_integral_value(rounding=ROUND_HALF_UP)) for p in period_range])      # +1 offset, 6 periods left, 2 periods right

def main():
	
	args = getParams()

	# Fast-fail on dependencies
	if args.qc_plot:
		import matplotlib.pyplot as plt
		import seaborn as sns

	# Load data
	sense_df = load_cdt(args.sense)
	anti_df = load_cdt(args.anti)

	assert anti_df.shape[0] == sense_df.shape[0], "Number of .cdt records does not match between sense and anti"
	assert anti_df.shape[1] == sense_df.shape[1], "Number of .cdt columns does not match between sense and anti"

	# Define zero shift and determine shift range to search
	if not args.zero:
		args.zero = (anti_df.shape[1] - 1) // 2
	shift_list = [(o, args.zero + o) for o in range(args.shift_range[0], args.shift_range[1])] # half-open shift_range

	assert args.zero > 0, "Invalid zero position index: zero ({args.zero}) must be greater than 0"
	assert args.zero < sense_df.shape[1], "Invalid zero position index: zero ({args.zero}) extends past the available number of .cdt columns"
	assert all([s>=0 and s<anti_df.shape[1] for (o,s) in shift_list]), "Shift range provided goes out-of-bounds on .cdt provided - check that your shift range and doesn't extend past the available number of .cdt columns."

	# Build relative slice mask to apply to each shift position
	sense_mask = build_mask(args.sense_period_range, args.period, anti=False)
	anti_mask  = build_mask(args.anti_period_range, args.period,  anti=True)

	# Load data
	sense_df = load_cdt(args.sense)
	anti_df = load_cdt(args.anti)

	both_phase = {}

	total_indexes_captured = {'sense': [], 'anti': []}
	# Count tags at different shifts
	for (offset, shift_index) in shift_list:
		sense_slices = [shift_index + i for i in sense_mask]
		anti_slices  = [shift_index + i for i in anti_mask]

		# Store sense/anti respective indexes counted in one way or another
		total_indexes_captured['sense'] += sense_slices
		total_indexes_captured['anti'] += anti_slices

		print(f"--offset{offset}--")
		slices_str = ",".join([f"{i:>5d}" for i in sense_slices])
		print(f"sense_{offset}: [{slices_str}]")
		slices_str = ",".join([f"{i:>5d}" for i in anti_slices])
		print(f"anti_{offset}:  [{slices_str}]")
		
		assert all([s>=0 and s<anti_df.shape[1] for s in sense_slices]), "Sense slices go out-of-bounds on the sense .cdt provided - check that your shift range and mask patterns don't extend past the available number of .cdt columns."
		assert all([s>=0 and s<anti_df.shape[1] for s in anti_slices ]), "Sense slices go out-of-bounds on the anti .cdt provided - check that your shift range and mask patterns don't extend past the available number of .cdt columns."
	
		both_phase[f"sense_{offset}"] = sense_df.loc[:,sense_slices].sum(axis=1)
		both_phase[f"anti_{offset}"] = anti_df.loc[:,anti_slices].sum(axis=1)

	# Initialize both phase tally counts into a df
	both_phase_df = pd.DataFrame(both_phase, index=sense_df.index)
	both_phase = None # memory clean-up for unused dictionary

	# Compute total tags for later normalization
	both_phase_df['sense_total'] = sense_df[list(set(total_indexes_captured['sense']))].sum(axis=1)
	both_phase_df['anti_total'] = anti_df[list(set(total_indexes_captured['anti']))].sum(axis=1)
	both_phase_df['total'] = both_phase_df['sense_total'] + both_phase_df['anti_total']

	# Score: sum both sense and anti by 2 offset and normalize by total tags in range
	pseudo_total = both_phase_df['total'].add(1)
	for (offset, shift_index) in shift_list:
		both_phase_df[f"{offset}_score"] = both_phase_df[f"sense_{offset}"].add(both_phase_df[f"anti_{offset}"]) / pseudo_total

	pseudo_total = None

	# Determine max score with associated phase and label ambiguous max scores
	score_max_df = both_phase_df[[f"{o}_score" for o,s in shift_list]] # slice scores from main df
	both_phase_df['max_score'] = score_max_df.max(axis="columns") # save max score
	both_phase_df['shift'] = score_max_df.idxmax(axis="columns") # add phase of max score
	for index, shift in both_phase_df['shift'].items():
		score_max_df.loc[index, shift] = 0 # zero out idxmax value
	both_phase_df['max_score2'] = score_max_df.max(axis="columns") # get second-highest max

	# Set phase to ambiguous if max_score2 matches max_score (tied for max)
	ambiguous_idx = both_phase_df['max_score']==both_phase_df['max_score2']
	both_phase_df.loc[ambiguous_idx, 'shift'] = "ambiguous"
	both_phase_df = both_phase_df.drop(columns=['max_score2']) # drop phase (for convenient max)
	
	score_max_df = None

	# Map phase assignment to shift and format
	def shift2int(s):
		return(s.split('_')[0])
	def shift2phase(s):
		if s=="ambiguous":
			return(s)
		return(str((int(s) + 1) % 10))
	both_phase_df['shift'] = both_phase_df['shift'].apply(shift2int)
	both_phase_df['phase'] = both_phase_df['shift'].apply(shift2phase)

	# Reorder columns for output
	column_reorder = ['shift', 'phase', 'max_score'] + [f"{o}_score" for (o,i) in shift_list] + ['total'] + [f"sense_{o}" for (o,i) in shift_list] + [f"anti_{o}" for (o,i) in shift_list]
	both_phase_df = both_phase_df[column_reorder]

	# Write output
	both_phase_df.to_csv(args.output, sep="\t")

	# Print ASCII schematic
	if args.print_schematic:
		# sys.stdout.write(get_general_schematic())
		sys.stdout.write(get_relative_schematic(args.zero, ncol=anti_df.shape[1], period=args.period, shift_range=args.shift_range, sense_period_range=args.sense_period_range, anti_period_range=args.anti_period_range))


	# Make QC plot for phasing details
	if args.qc_plot:
		
		phase_counts = pd.DataFrame(both_phase_df['phase'].value_counts())
		phase_counts = phase_counts.sort_index()
		# phase_counts['percentage'] = 100 * phase_counts['count'] / phase_counts['count'].sum()
		
		print(sum(both_phase_df['max_score']==0))

		# Initialize plot base with twin axes
		fig, ax = plt.subplots(1,3, sharey='row')

		# Specify dimensions
		# plt.figure(figsize=(args.width, args.height))
		# plt.figure(figsize=(6, 4))

		sns.barplot(phase_counts, ax=ax[0], y='phase', x='count', orient='y', color='lightgray')
		ax[0].bar_label(ax[0].containers[0], labels=phase_counts['count'], padding=-30)
		# ax.bar_label(ax.containers[0], labels=phase_counts['percentage'])
		ax[0].tick_params(axis='x', labelrotation=35)

		sns.boxplot(both_phase_df, ax=ax[1], y='phase', x='max_score', orient='y', color='lightgray')
		
		sns.boxplot(both_phase_df, ax=ax[2], y='phase', x='total', orient='y', color='lightgray')
		ax[2].set(xscale="log")

		fig.savefig(args.qc_plot) #, transparent=True)

if __name__ == '__main__':
	main()
