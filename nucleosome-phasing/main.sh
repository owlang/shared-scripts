set -exo

SCRIPTMANAGER=../../scriptmanager/build/libs/ScriptManager-v0.15.jar 
PHASE=phase_refpt-300bp-window.py
PHASE=phase_refpt-general-window.py
SHIFT=../coordinate-manipulation/shift_per-site_BED.py
SPLIT=phase_split_BED.py
FILTERL=../coordinate-manipulation/filter_BED_by_list_ColumnSelect.pl

TSS=test/TSSstart_Xu.bed
NUC=test/NFR_YEP_downstreamNuc.bed
BAM=test/37071_Htz1_i5006_BY4741_filtered.bam
GENOME=../data/sacCer3/sacCer3.fa
SIZES=../data/sacCer3/sacCer3.fa.fai
# Filter invalid Nuc entry:
grep -v $'YFL068W\t' $NUC > test/NFR_YEP_downstreamNuc_Removed-YFL068W.bed

[ -d Dyad-Phasing ] || mkdir Dyad-Phasing

BASE=Dyad-Phasing/Dyad

# Expand and TagPileup
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -c 300 test/NFR_YEP_downstreamNuc_Removed-YFL068W.bed -o ${BASE}_300bp.bed
java -jar $SCRIPTMANAGER read-analysis tag-pileup --cpu 4 --window-smooth -5 -1 \
    ${BASE}_300bp.bed $BAM \
    -M ${BASE}_300bp_5read1 \
    -o ${BASE}_300bp_unphased-composite.out

# Call phases
python $PHASE -s ${BASE}_300bp_5read1_sense.cdt -a ${BASE}_300bp_5read1_anti.cdt \
    -o ${BASE}_300bp_5read1_phasing.tsv --qc-plot ${BASE}_300bp_5read1_phasing-QC-plot.png

# Split out ambiguously phased nucleosomes
sed '1d' ${BASE}_300bp_5read1_phasing.tsv | awk 'BEGIN{OFS="\t";FS="\t"}{if ($2=="ambiguous") print $1}' > Dyad-Phasing/AmbiguousPhase.txt
perl $FILTERL ${BASE}_300bp.bed Dyad-Phasing/AmbiguousPhase.txt 3 keep ${BASE}_300bp_Ambiguous.bed
perl $FILTERL ${BASE}_300bp.bed Dyad-Phasing/AmbiguousPhase.txt 3 remove ${BASE}_300bp_Unambiguous.bed
perl $FILTERL ${BASE}_300bp_5read1_phasing.tsv Dyad-Phasing/AmbiguousPhase.txt 0 remove Dyad-Phasing/ShiftInfo_Unambiguous.tsv

# Per-site shift nucleosomes to same-phase (sync)
python $SHIFT -i ${BASE}_300bp_Unambiguous.bed -r Dyad-Phasing/ShiftInfo_Unambiguous.tsv -o ${BASE}_300bp_Unambiguous-Synced.bed

# Narrow dyad expansion
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -c 2 ${BASE}_300bp_Unambiguous-Synced.bed -o ${BASE}_Synced_2bp.bed
java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -c 2 $TSS -o Dyad-Phasing/TSS_2bp.bed
bedtools slop -s -l 0 -r -1 -g $SIZES -i ${BASE}_Synced_2bp.bed > ${BASE}_Synced_1bp.bed
bedtools slop -s -l 0 -r -1 -g $SIZES -i Dyad-Phasing/TSS_2bp.bed > Dyad-Phasing/TSS_1bp.bed

# Compute distance to closest TSS
bedtools sort -g $SIZES -i yad-Phasing/TSS_1bp.bed > Dyad-Phasing/TSS_sorted.bed
bedtools sort -g $SIZES -i ${BASE}_Synced_1bp.bed > Dyad-Phasing/Nuc_sorted.bed
bedtools closest -S -D a -wo -a Dyad-Phasing/TSS_sorted.bed -b Dyad-Phasing/Nuc_sorted.bed > Dyad-Phasing/TSS-Synced.tsv

python $SPLIT -i Dyad-Phasing/TSS-Synced.tsv -O Dyad-Phasing/split --qc-plot Dyad-Phasing/split/QC-plot.png

TEMP=grouped
[ -d $TEMP ] || mkdir $TEMP

for file in Dyad-Phasing/split/*phase*.bed;
do
    BED=$(basename $file ".bed")
    java -jar $SCRIPTMANAGER coordinate-manipulation expand-bed -c 300 $file -o $TEMP/${BED}_300bp.bed
    java -jar $SCRIPTMANAGER read-analysis tag-pileup --cpu 4 --window-smooth -5 -1 \
        $TEMP/${BED}_300bp.bed $BAM \
        -M $TEMP/${BED}_phased_5read1 \
        -o $TEMP/${BED}_phased-composite.out

done


# Re-pileup on synced Nucs
java -jar $SCRIPTMANAGER read-analysis tag-pileup --cpu 4 --window-smooth -5 -1 \
    ${BASE}_300bp_Unambiguous-Synced.bed $BAM \
    -M ${BASE}_300bp_Unambiguous-Synced_5read1 \
    -o ${BASE}_300bp_phased-composite.out

# Check phasing of each half
python $PHASE -s ${BASE}_300bp_Unambiguous-Synced_5read1_sense.cdt -a ${BASE}_300bp_Unambiguous-Synced_5read1_anti.cdt \
    -o Dyad-Phasing/Unambiguous-Synced_5read1_left-phasing.tsv --qc-plot Dyad-Phasing/Unambiguous-Synced_5read1_left-phasing-QC-plot.png \
    --sense-period-range -6 -3 --anti-period-range -6 -3

python $PHASE -s ${BASE}_300bp_Unambiguous-Synced_5read1_sense.cdt -a ${BASE}_300bp_Unambiguous-Synced_5read1_anti.cdt \
    -o Dyad-Phasing/Unambiguous-Synced_5read1_right-phasing.tsv --qc-plot Dyad-Phasing/Unambiguous-Synced_5read1_right-phasing-QC-plot.png \
    --sense-period-range 3 6 --anti-period-range 3 6

paste <(cut -f1-2 Dyad-Phasing/Unambiguous-Synced_5read1_left-phasing.tsv) \
    <(cut -f1-2 Dyad-Phasing/Unambiguous-Synced_5read1_right-phasing.tsv) \
    | awk 'BEGIN{OFS="\t";FS="\t"}{if ($1!=$3) print "Mismatch"; else print $1,$2,$4;}' \
    > Dyad-Phasing/Match_Left-Right-Phasing.tsv

cut -f2-3 Dyad-Phasing/Match_Left-Right-Phasing.tsv | sort | uniq -c > Dyad-Phasing/Match_Left-Right-Phasing.stats