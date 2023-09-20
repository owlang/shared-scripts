

GETBAM=get_BAM_from_ENCODEsearch.py
GETENCSR=get_ENCSR_from_ENCODEsearch.py

# URL filters:
# frame=object&format=json&limit=all
# 	- General options
# type=File&file_format=bam&output_type=alignments
# 	- File objects
# 	- BAM filetype
# 	- "alignments" subtype (as opposed to "unfiltered alignments")
# biosample_ontology.term_name=K562
# 	- Biosample = K562
# assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq
# 	- Assay = "TF ChIP-seq" or "Histone ChIP-seq"
# assembly=GRCh38
# 	- Genome build = "GRCh38"
BAM_K562_CHIP_URL="https://www.encodeproject.org/search/?type=File&file_format=bam&output_type=alignments&biosample_ontology.term_name=K562&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&assembly=GRCh38&frame=object&format=json&limit=all"
# BAM_K562_CHIP_URL="https://www.encodeproject.org/search/?type=File&file_format=bam&output_type=alignments&biosample_ontology.term_name=K562&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&assembly=GRCh38&frame=object&format=json"
# python $GETBAM -i $BAM_K562_CHIP_URL -o K562_ChIP-seq_all_BAM.tsv

# URL filters:
# frame=object&format=json&limit=all
# 	- General options
# type=Experiment&control_type%21=%2A&status=released
# 	- Experiment objects
# 	- hide control type experiments
# 	- status = "released"
# assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq
# 	- Assay = "TF ChIP-seq" or "Histone ChIP-seq"
# biosample_ontology.term_name=K562
# 	- Biosample = K562
# assembly=GRCh38
# 	- Genome build = "GRCh38"
# perturbed=false
# 	- pertubed = "false"

ENCSR_K562_CHIP_URL="https://www.encodeproject.org/search/?type=Experiment&control_type%21=%2A&status=released&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&assembly=GRCh38&perturbed=false&format=json&limit=all"
# ENCSR_K562_CHIP_URL="https://www.encodeproject.org/search/?type=Experiment&control_type%21=%2A&status=released&assay_title=TF+ChIP-seq&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&assembly=GRCh38&perturbed=false&format=json"
# python $GETENCSR -i $ENCSR_K562_CHIP_URL -o K562_ChIP-seq_all_ENCSR.tsv

# Pull intersect of ENCSR results (restrict BAM to "unperturbed set")
grep -f <(cut -f1 K562_ChIP-seq_all_ENCSR.tsv) K562_ChIP-seq_all_BAM.tsv > unperturbed_BAM.temp
# Remove pattern flow cell platforms
awk '{FS="\t"}{OFS="\t"}{if($12!="Illumina NovaSeq 6000" && $12!="Illumina HiSeq 4000") print}' unperturbed_BAM.temp > nopatternfc_BAM.temp
# Subset biological_replicate = 1, then sort by target
awk '{FS="\t"}{OFS="\t"}{if($14==1) print}' nopatternfc_BAM.temp | sort -t $'\t' -k17,17 > first_replicates_BAM.temp
# Create separate "male genome index" and "genome index" lists
awk '{FS="\t"}{OFS="\t"}{if($6=="male genome index") print}' first_replicates_BAM.temp > male_genome_index.tsv
awk '{FS="\t"}{OFS="\t"}{if($6=="genome index") print}' first_replicates_BAM.temp > genome_index.tsv

# Python script to apply selection criteria (must be sorted by target-column 17)
# i.e. pick most recent for each target
python deduplicate_ENCFF-bam_custom_criteria.py -i genome_index.tsv -o FINAL_K562_ChIP-seq_all_BAM_genome-index_unique.tsv
python deduplicate_ENCFF-bam_custom_criteria.py -i male_genome_index.tsv -o FINAL_K562_ChIP-seq_all_BAM_male-genome-index_unique.tsv

# Subset duplicates to look at
# cut -d $'\t' -f 15 first_replicates_BAM.temp |sort |uniq -c |sort -nr | grep -v ' 1 '  | awk '{print $2}' > duplicate_accessions.txt
# grep -f duplicate_accessions.txt K562_ChIP-seq_all_BAM_filtered.tsv


# Download Resulting file--check https://github.com/CEGRcode/GenoPipe/blob/master/paper/ENCODEdata-CellLines/job/00_download_data.pbs
# Just replace METADATA with path to this final TSV
# Change HREF to build index off of ENCFF
# Change MD5SSUM index to 2
# Update job array to number of samples and qsub
