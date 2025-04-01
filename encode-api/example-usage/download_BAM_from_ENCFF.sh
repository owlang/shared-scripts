#!/bin/bash
#PBS -l nodes=1:ppn=6
#PBS -l pmem=24gb
#PBS -l walltime=05:00:00
#PBS -A open
#PBS -o logs/download.data.log.out
#PBS -e logs/download.data.log.err
#PBS -t 1-NSAMPLES

module load gcc/9.3.1
module load samtools
module load anaconda3
source activate genopipe

WRK=/path/to/BAM/directory
cd $WRK

[ -d logs ] || mkdir logs
[ -d results/BAM ] || mkdir -p results/BAM

METADATA=FINAL_K562_ChIP-seq_all_BAM_genome-index_unique.tsv
INFO=`sed "${PBS_ARRAYID}q;d" $METADATA`
ENCFF=`echo $INFO | awk '{print $1}'`
#echo $INFO

cd results/BAM
BAM=$ENCFF.bam


# Download Resulting file--check https://github.com/CEGRcode/GenoPipe/blob/master/paper/ENCODEdata-CellLines/job/00_download_data.pbs
# Just replace METADATA with path to this final TSV
# Change HREF to build index off of ENCFF
# Change MD5SSUM index to 2
# Update job array to number of samples and qsub


# ENCODE data download
HREF=`echo $INFO | awk '{print $2}'`
echo "Fetching from https://www.encodeproject.org$HREF"
wget https://www.encodeproject.org$HREF

# Checksum of resulting BAM
MD5SUM=`echo $INFO | awk '{print $3}'`
if [[ `md5sum $BAM` =~ $MD5SUM ]]; then
	echo "($PBS_ARRAYID) $BAM passed."
else
	echo "($PBS_ARRAYID) $BAM md5checksum failed!"
	rm $BAM
	exit
fi

# Index BAM file
samtools index $BAM
