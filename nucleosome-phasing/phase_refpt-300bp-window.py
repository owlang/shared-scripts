#!/usr/bin/env python3
import sys, warnings
import argparse
import pandas as pd

def getParams():
	'''Parse parameters from the command line'''
	parser = argparse.ArgumentParser(description='''
This script will phase nucleosomes from a 300bp window. Assumes matching sort for both CDT inputs.

Note: this script is based on the hardcoded values in Haining's original script given to Rebecca. There appear to be some errors in the indexing that need to be resolved but for practical purposes, the resulting shifts from this script are more-or-less workable.

Example: python phase_refpt-300bp-window.py -s SENSE.cdt -a ANTI.cdt -o OUTPUT.tsv''')
	parser.add_argument('-s','--sense', metavar='cdt_fn', required=True, help='a CDT file of the pileup for the -i .bed file')
	parser.add_argument('-a','--anti', metavar='cdt_fn', required=True, help='a CDT file of the pileup for the -i .bed file')
	parser.add_argument('-o','--output', metavar='tsv_fn', required=True, help='a TSV file with the id and phasing shift distance along with all the scoring intermediate values for determining phase')

	# parser.add_argument('--batch', metavar='batch_size', type=int, default=10000, help='for large BED/CDT files, set a number of rows to process at a time')
	parser.add_argument('--qc-plot', metavar='img_fn', help='write summary stats to figure file (.png or .svg)')
	# parser.add_argument('--info', metavar='tsv_fn', help='a TSV file with stats and metadata associated with phasing')

	args = parser.parse_args()
	return(args)

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
	assert cdt_df.shape[1] == 302, "CDT must have 2 header columns + 300 value columns"
	cdt_df.set_index(['YORF','NAME'], inplace=True)
	# Cast all data values to numeric types
	cdt_df.columns = [int(i) for i in cdt_df.columns]
	# cdt_df = cdt_df.convert_dtypes()
	cdt_df[cdt_df.columns] = cdt_df[cdt_df.columns].astype('float')
	return(cdt_df)


def main():
	
	args = getParams()

	warnings.warn("This is an old and hard-coded version of phasing based on Haining's windows. Please consider using phase_refpt-general-window.py instead.")

	# Fast-fail on dependencies
	if args.qc_plot:
		import matplotlib.pyplot as plt
		import seaborn as sns

	# Load data
	sense_df = load_cdt(args.sense)
	anti_df = load_cdt(args.anti)

	assert anti_df.shape[0] == sense_df.shape[0], "Number of .cdt records does not match between sense and anti"

	# Count tags at each phase
	sense_start, sense_stop = 130, 180 # half-open, i.e. {130..179} - original shell script used same intervals
	anti_start, anti_stop = 130, 180 # half-open, i.e. {130..179} - original shell script used same intervals
	both_phase = {}

	for phase in range(10):
		sense_slices = list(range(sense_start+phase, sense_stop, 10))
		anti_slices = list(range(anti_start+phase, anti_stop, 10))
		
		print(f"--phase{phase}--")
		slices_str = ",".join([f"{i:>5d}" for i in sense_slices])
		print(f"sense_{phase}: [{slices_str}]")
		slices_str = ",".join([f"{i:>5d}" for i in anti_slices])
		print(f"anti_{phase}:  [{slices_str}]")
		
		both_phase[f"sense_{phase}"] = sense_df.loc[:,sense_slices].sum(axis=1)
		both_phase[f"anti_{phase}"] = anti_df.loc[:,anti_slices].sum(axis=1)

	both_phase_df = pd.DataFrame(both_phase, index=sense_df.index)
	both_phase_df['total'] = both_phase_df.sum(axis=1)

	both_phase = None

	# Score: sum both sense and anti by 2 offset and normalize by total tags
	pseudo_total = both_phase_df['total'].add(1)
	both_phase_df[f"1_score"] = both_phase_df["sense_0"].add(both_phase_df["anti_8"]) / pseudo_total
	both_phase_df[f"2_score"] = both_phase_df["sense_1"].add(both_phase_df["anti_9"]) / pseudo_total
	both_phase_df[f"3_score"] = both_phase_df["sense_2"].add(both_phase_df["anti_0"]) / pseudo_total
	both_phase_df[f"4_score"] = both_phase_df["sense_3"].add(both_phase_df["anti_1"]) / pseudo_total
	both_phase_df[f"5_score"] = both_phase_df["sense_4"].add(both_phase_df["anti_2"]) / pseudo_total
	both_phase_df[f"6_score"] = both_phase_df["sense_5"].add(both_phase_df["anti_3"]) / pseudo_total
	both_phase_df[f"7_score"] = both_phase_df["sense_6"].add(both_phase_df["anti_4"]) / pseudo_total
	both_phase_df[f"8_score"] = both_phase_df["sense_7"].add(both_phase_df["anti_5"]) / pseudo_total
	both_phase_df[f"9_score"] = both_phase_df["sense_8"].add(both_phase_df["anti_6"]) / pseudo_total
	both_phase_df[f"0_score"] = both_phase_df["sense_9"].add(both_phase_df["anti_7"]) / pseudo_total

	pseudo_total = None

	# Determine max score with associated phase and label ambiguous max scores
	score_max_df = both_phase_df[[f"{p}_score" for p in range(10)]] # slice scores from main df
	both_phase_df['max_score'] = score_max_df.max(axis="columns") # save max score
	both_phase_df['phase'] = score_max_df.idxmax(axis="columns") # add phase of max score
	for index, phase in both_phase_df['phase'].items():
		score_max_df.loc[index, phase] = 0 # zero out idxmax value
	both_phase_df['max_score2'] = score_max_df.max(axis="columns") # get second-highest max
	# Set phase to ambiguous if max_score2 matches max_score (tied for max)
	phase_wabmig = ["ambiguous" if row.max_score == row.max_score2 else row.phase for (idx, row) in both_phase_df.iterrows()]
	both_phase_df['phase'] = phase_wabmig
	both_phase_df = both_phase_df.drop(columns=['max_score2']) # drop phase (for convenient max)
	
	score_max_df = None

	# Map phase assignment to shift
	phase2shift = {
		"1_score": 0,
		"2_score": 1, "0_score": -1,
		"3_score": 2, "9_score": -2,
		"4_score": 3, "8_score": -3,
		"5_score": 4, "7_score": -4,
		"6_score": 5,
	}
	both_phase_df['shift'] = both_phase_df['phase'].map(phase2shift)
	
	# Reorder columns for output
	column_reorder = ['shift', 'phase', 'max_score'] + [f"{p}_score" for p in range(10)] + ['total'] + [f"sense_{p}" for p in range(10)] + [f"anti_{p}" for p in range(10)]
	both_phase_df = both_phase_df[column_reorder]

	# Write output
	both_phase_df.to_csv(args.output, sep="\t")

	# Make QC plot for phasing details
	if args.qc_plot:
		
		phase_counts = pd.DataFrame(both_phase_df['phase'].value_counts())
		phase_counts = phase_counts.sort_index()
		phase_counts['percentage'] = 100 * phase_counts['count'] / phase_counts['count'].sum()

		# Initialize plot base with twin axes
		fig, ax = plt.subplots(1,2, sharey='row')

		# Specify dimensions
		# plt.figure(figsize=(args.width, args.height))
		# plt.figure(figsize=(6, 4))

		sns.barplot(phase_counts, ax=ax[0], y='phase', x='count', orient="y", color='lightgray')
		ax[0].bar_label(ax[0].containers[0], labels=phase_counts['count'], padding=-30)
		# ax.bar_label(ax.containers[0], labels=phase_counts['percentage'])
		ax[0].tick_params(axis='x', labelrotation=35)
		
		sns.boxplot(both_phase_df, ax=ax[1], y='phase', x='max_score', orient="y", color='lightgray')

		fig.savefig(args.qc_plot) #, transparent=True)

if __name__ == '__main__':
	main()


####################################################################################
#            ASCII Art for diagraming dyad window index selection below            #
####################################################################################

# ========CDT index (+header, 0-index)========
#          1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0
# 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012
# ========CDT index (+header, 1-index)========
# 0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0
# 01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
# ========CDT index (-header, 0-index)========
# --0                                                                                                   1                                                                                                   2                                                                                                   3
# --0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         
# --012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
# dyad-midpoint                                                                                                                                          |123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# ========CDT index (-header, 0-index)========
# --0                                                                                                   1                                                                                                   2                                                                                                   3
# --0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         
# --012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789


# *******HAINING WINDOWS*******

# ========Post-cut index (1-indexed)========
#                                                                             0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5
#                                                                              123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
# cut -f 78-227                                                                |----------------------------------------------------------------------------------------------------------------------------------------------------|
# awk                                                                                                                                                                                                                                
# 1 # $56+$66+$76+$86+ $96,                                                                                                           |         |         |         |         |
# 2 # $57+$67+$77+$87+ $97,                                                                                                            |         |         |         |         |
# 3 # $58+$68+$78+$88+ $98,                                                                                                             |         |         |         |         |
# 4 # $59+$69+$79+$89+ $99,                                                                                                              |         |         |         |         |
# 5 # $60+$70+$80+$90+$100,                                                                                                               |         |         |         |         |
# 6 # $61+$71+$81+$91+$101,                                                                                                                |         |         |         |         |
# 7 # $52+$62+$72+$82+ $92,                                                                                                                 |         |         |         |         |
# 8 # $53+$63+$73+$83+ $93,                                                                                                                  |         |         |         |         |
# 9 # $54+$64+$74+$84+ $94,                                                                                                                   |         |         |         |         |
# 0 # $55+$65+$75+$85+ $95                                                                                                                     |         |         |         |         |

# cut -f 78-227                                                                |----------------------------------------------------------------------------------------------------------------------------------------------------|
# awk (second set runs off the window...)
#11 # $56+$66+$76+$86+$96+$107+$117+$127+$137+$147,
#12 # $57+$67+$77+$87+$97+$108+$118+$128+$138+$148,
#13 # $58+$68+$78+$88+$98+$109+$119+$129+$139+$149,
#14 # $59+$69+$79+$89+$99+$110+$120+$130+$140+$150,
#15 # $50+$60+$70+$80+$90+$101+$111+$121+$131+$141,
#16 # $51+$61+$71+$81+$91+$102+$112+$122+$132+$142,
#17 # $52+$62+$72+$82+$92+$103+$113+$123+$133+$143,
#18 # $53+$63+$73+$83+$93+$104+$114+$124+$134+$144,
#19 # $54+$64+$74+$84+$94+$105+$115+$125+$135+$145,
#20 # $55+$65+$75+$85+$95+$106+$116+$126+$136+$146                                                                                              |         |         |         |         |

# counts: sense (1-10), anti (11-20)
# awk 
	#  $1+$19,
	#  $2+$20,
	#  $3+$11,
	#  $4+$12,
	#  $5+$13,
	#  $6+$14,
	#  $7+$15,
	#  $8+$16,
	#  $9+$17,
	# $10+$18
# awk
	# add total count (per-row) to 11th column
# awk
	# Divide each phase count by 11th total (+1 pseudocount)
# paste
	# Append score to .bed file
