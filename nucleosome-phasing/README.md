# nucleosome-phasing

## Requirements

### Packages

* python
  * pysam
  * pandas
  * seaborn
* bedtools

### Inputs

You will need a `.bam` file of some type of benzonase-digested library 

## Recommended usage

Most peak-callers are not 1bp precise with their translational phasing of dyad calls. This isn't always a technical limitation of the peak caller but some nucleosomes positioning is a bit fuzzy because in a bulk population, some cells might have their nucleosomes shifted a few bp from each other, esp the dynamic ones like at genes undergoing active transcription.

As a result, we need to phase our dyad reference point to have consistent rotational positioning before computing different *relational phases* to some biological feature like a motif or TSS.

### Step 1: Phase your dydad reference point (dyad.bed --> phased_dyad.bed)

Use the `phase_refpt-general-window.py` script to generate the shift values needed to phase dyad annotations. Then apply the shift using `../coordinate-manipulation/shift_per-site_BED.py`.

```sh
SCRIPTMANAGER=
PHASE=
SHIFT=

BAM=nucleosome-benz-sample.bam
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -c 300 dyad.bed -o dyad_300bp.bed
# Use both 5' ends for benzonase digested data. May want to switch to -5 -2 for Benz ChIP-exo. User should make an explicit decision here.
java -jar $SCRIPTMANAGER read-analysis tag-pileup --cpu 4 --window-smooth -5 -a \
    dyad_300bp.bed $BAM \
    -M dyad_300bp__unphased__5readBoth \
    -o dyad_300bp__unphased__5readBoth.out

# Call phases
python $PHASE -s dyad_300bp__unphased__5readBoth_sense.cdt -a dyad_300bp__unphased__5readBoth_anti.cdt \
    -o phasing.tsv --qc-plot phasing-QC-plot.png

# Shift dyads
python $SHIFT -i dyad_300bp.bed -r phasing.tsv -o phased_dyad_300bp.bed

```

> [!IMPORTANT]
> The user should consider whether their dataset will need to select for the 5' end cut site of Read 1, Read 2, or both depending on their assay. Benzonase-seq, Benzonase ChIP-exo, DNase-seq, and other genomic assays all have their own considerations. Different library construction strategies may also need to be considered when making this decision.

### Step 2: Compute distances to your reference point of interest (phased_dyad.bed + tss.bed --> dyad-tss.bed13)

This step should be done using `bedtools` so that the user has full control on customizing the parameters of dyad to reference association. Here is a suggested command as a starting point for generating the BED13 file needed in the next step. There resulting file should have 13 columns with the first bed file (col 1-6), second bed file (7-12), and a distance measure (col 13) stacked together.

```sh
# I like to start by ensuring the files are 1bp centered by ScriptManager dyad standards:
# - scriptmanager re-expand to 2bp (only supports even windows but convenient for getting the stranded center correct)
# - bedtools stranded slop to subtract one from the relative right
# - ensure the files are BED6 (6 columm limit)
# - next step requires the inputs to be sorted
GSIZE=/path/to/genome.fa.fai
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -s -c 2 synced_dyad_300bp.bed | bedtools slop -s -l 0 -r -1 -g $GSIZE -i | cut -f1-6 | bedtools sort -i - -g $GSIZE > phased_dyad.bed
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -s -c 2 tss.bed               | bedtools slop -s -l 0 -r -1 -g $GSIZE -i | cut -f1-6 | bedtools sort -i - -g $GSIZE > tss.bed

# Use this basic bedtools command to get the closest
bedtools closest -D a -wo -a tss.bed -b phased_dyad.bed > dyad-tss.bed13
```

There are any number of modifications or filters you can perform on the bedtools closest command. Here are some ideas:

* require both annotations be on the same strand (`-S`)
* get distance relative to dyad instead of relative to the tss (`-D b`)
* ignore upstream or downstream annotations (`-iu`/`-io`)
* consider ignoring strand of dyad and switching dyad to match refpt. You may need to repeat step 1 if you do so.
* filter for unique dyads or unique annotations (`awk '{...}'`/`sort`/`uniq`)

### Step 3: Compute relative phases and split into groups (dyad-tss.bed13 --> dyad-phaseX.bed + tss-phaseX.bed)

This script is relatively straightforward by computing the relative phase from col 13 and splits the files by the relative phase (modulus 10):

![BED13 Input Format](img/BED13_Input.png)

```sh
SPLIT=phase_split_BED.py
python $SPLIT -i dyad-tss.bed13 -o dyad-tss_groups

# |--dyad-tss_groups
#   |--left_phase-0.bed
#   |--left_phase-1.bed
#   |--left_phase-2.bed
#   |--left_phase-3.bed
#   |--left_phase-4.bed
#   |--left_phase-5.bed
#   |--left_phase-6.bed
#   |--left_phase-7.bed
#   |--left_phase-8.bed
#   |--left_phase-9.bed
#   |--right_phase-0.bed
#   |--right_phase-1.bed
#   |--right_phase-2.bed
#   |--right_phase-3.bed
#   |--right_phase-4.bed
#   |--right_phase-5.bed
#   |--right_phase-6.bed
#   |--right_phase-7.bed
#   |--right_phase-8.bed
#   |--right_phase-9.bed
```

## Test data

Here are details for how the test data was generated and how to run tests.

### test data generation

```sh
NUC=NFR_YEP_downstreamNuc.bed # generated from Rossi et al 2021 (YEP) STable1
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="01_RP") print}' $NUC | shuf | head -n 100  > test-input/Dyad_01-RP.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="02_STM") print}' $NUC | shuf | head -n 100 > test-input/Dyad_02-STM.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="03_TFO") print}' $NUC | shuf | head -n 100 > test-input/Dyad_03-TFO.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="04_UNB") print}' $NUC | shuf | head -n 100 > temp-Dyad_04-UNB.bed

java -jar $SCRIPTMANAGER read-analysis tag-pilepu 

# TODO: Tag Pileup and split by total occupancy
```

### running test data

```sh

```

## TODO: Validation

Here are technical details for how this script was vetted to set default parameters and options. Most users not interested in updating this script will not find this interesting.

### Selecting period

* check by phasing on flanks - same phase?
* right should correlate with left, even if right and left both don't correlate with full
    * if so, then you may have a bad phasing period
    * Scatter: right v left
    * Scatter: full v right
    * Scatter: full v left
* try: 10bp, 10.2bp, 10.5bp

### Basic hypothesis checking

Hypothesis: expect better rotational and translational phasing scores on 04_UNB over others.
Hypothesis: expect less uniform rotational preference on CAGE (max) TSS, at least for 04_UNB.

```sh
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="01_RP") print}' $NUC | shuf | head -n 100  > test-input/Dyad_01-RP.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="02_STM") print}' $NUC | shuf | head -n 100 > test-input/Dyad_02-STM.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="03_TFO") print}' $NUC | shuf | head -n 100 > test-input/Dyad_03-TFO.bed
awk 'BEGIN{OFS="\t";FS="\t"}{if ($4=="04_UNB") print}' $NUC | shuf | head -n 100 > temp-Dyad_04-UNB.bed
```
